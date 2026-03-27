"""Service to sync household tasks from Notion to the local database.

Syncs from two Notion databases:
1. Tasks DB — general tasks with Assignee, Status, Priority, Projects (rooms), Date
2. Chores DB — recurring chores with Frequency, Last Done, Rooms (multi-select)
"""

import json
from datetime import date
from typing import Any

import httpx
from sqlalchemy.orm import Session

from ..config import settings
from ..models.task import (
    Priority,
    Recurrence,
    TaskCategory,
    TaskDB,
    TaskMode,
    TaskSource,
    TaskStatus,
)

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Map Notion room names to TaskCategory enum values
ROOM_TO_CATEGORY: dict[str, str] = {
    "kitchen": TaskCategory.KITCHEN.value,
    "dining room": TaskCategory.DINING_ROOM.value,
    "living room": TaskCategory.LIVING_ROOM.value,
    "master bedroom": TaskCategory.MASTER_BEDROOM.value,
    "master bathroom": TaskCategory.MASTER_BATHROOM.value,
    "bathroom": TaskCategory.BATHROOM.value,
    "office": TaskCategory.OFFICE.value,
    "stairwell": TaskCategory.STAIRWELL.value,
}

# Map Notion status values to TaskStatus enum
STATUS_MAP: dict[str, str] = {
    "not started": TaskStatus.NOT_STARTED.value,
    "in progress": TaskStatus.IN_PROGRESS.value,
    "done": TaskStatus.DONE.value,
    "archived": TaskStatus.ARCHIVED.value,
}

# Map Notion frequency values to Recurrence enum
FREQUENCY_MAP: dict[str, str] = {
    "daily": Recurrence.DAILY.value,
    "weekly": Recurrence.WEEKLY.value,
    "bi-weekly": Recurrence.BI_WEEKLY.value,
    "monthly": Recurrence.MONTHLY.value,
    "seasonally": Recurrence.SEASONALLY.value,
    "semi-annually": Recurrence.SEMI_ANNUALLY.value,
    "annually": Recurrence.ANNUALLY.value,
}

PRIORITY_MAP: dict[str, str] = {
    "low": Priority.LOW.value,
    "medium": Priority.MEDIUM.value,
    "high": Priority.HIGH.value,
}


def _notion_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.notion_api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


# --- Helpers for parsing Notion property types ---

def _safe_title(props: dict[str, Any], *keys: str) -> str:
    for key in keys:
        prop = props.get(key)
        if prop and prop.get("title"):
            parts = prop["title"]
            text = "".join(p.get("plain_text", "") for p in parts)
            if text:
                return text
    return "Untitled"


def _safe_select(prop: dict[str, Any] | None) -> str | None:
    if prop and prop.get("select") and prop["select"].get("name"):
        return prop["select"]["name"]
    return None


def _safe_status(prop: dict[str, Any] | None) -> str | None:
    if prop and prop.get("status") and prop["status"].get("name"):
        return prop["status"]["name"]
    return None


def _safe_multi_select(prop: dict[str, Any] | None) -> list[str]:
    if prop and prop.get("multi_select"):
        return [opt["name"] for opt in prop["multi_select"] if opt.get("name")]
    return []


def _safe_date(prop: dict[str, Any] | None) -> date | None:
    if prop and prop.get("date") and prop["date"].get("start"):
        try:
            return date.fromisoformat(prop["date"]["start"][:10])
        except ValueError:
            pass
    return None


def _safe_person(prop: dict[str, Any] | None) -> str | None:
    if prop and prop.get("people"):
        people = prop["people"]
        if people:
            return people[0].get("name", None)
    return None


def _safe_relation(prop: dict[str, Any] | None) -> list[str]:
    """Extract relation page IDs."""
    if prop and prop.get("relation"):
        return [r["id"] for r in prop["relation"] if r.get("id")]
    return []


# --- Parse Tasks DB pages ---

def _parse_tasks_db_page(page: dict[str, Any]) -> dict[str, Any]:
    """Parse a page from the Tasks database.

    Properties: Task name (title), Assignee (person), Status (status),
    Priority (select), Projects (relation), 📅 Date (date)
    """
    props = page.get("properties", {})

    status_name = _safe_status(props.get("Status"))
    status = STATUS_MAP.get(status_name.lower(), TaskStatus.NOT_STARTED.value) if status_name else TaskStatus.NOT_STARTED.value

    priority_name = _safe_select(props.get("Priority"))
    priority = PRIORITY_MAP.get(priority_name.lower(), Priority.MEDIUM.value) if priority_name else Priority.MEDIUM.value

    return {
        "notion_id": page["id"],
        "source": TaskSource.TASKS.value,
        "title": _safe_title(props, "Task name", "Name"),
        "assigned_to": _safe_person(props.get("Assignee")),
        "status": status,
        "priority": priority,
        "due_date": _safe_date(props.get("📅 Date")),
        "recurrence": Recurrence.ONCE.value,
        "category": TaskCategory.GENERAL.value,
        "mode": TaskMode.ADULT.value,
        "active": status != TaskStatus.ARCHIVED.value,
    }


# --- Parse Chores DB pages ---

def _parse_chores_db_page(page: dict[str, Any]) -> dict[str, Any]:
    """Parse a page from the Chores database.

    Properties: Task (title), Frequency (select), Last Done (date),
    Rooms (multi_select), Status (formula), Do Next (formula)
    """
    props = page.get("properties", {})

    # Map frequency
    freq_name = _safe_select(props.get("Frequency"))
    recurrence = FREQUENCY_MAP.get(freq_name.lower(), Recurrence.ONCE.value) if freq_name else Recurrence.ONCE.value

    # Map rooms to category (use first room as primary category)
    rooms = _safe_multi_select(props.get("Rooms"))
    rooms_json = json.dumps(rooms) if rooms else None
    category = TaskCategory.GENERAL.value
    if rooms:
        first_room = rooms[0].lower()
        category = ROOM_TO_CATEGORY.get(first_room, TaskCategory.GENERAL.value)

    last_done = _safe_date(props.get("Last Done"))

    return {
        "notion_id": page["id"],
        "source": TaskSource.CHORES.value,
        "title": _safe_title(props, "Task", "Name"),
        "assigned_to": None,  # Chores DB doesn't have assignee
        "status": TaskStatus.NOT_STARTED.value,
        "priority": Priority.MEDIUM.value,
        "due_date": None,
        "recurrence": recurrence,
        "category": category,
        "rooms": rooms_json,
        "mode": TaskMode.FAMILY.value,
        "active": True,
        "last_completed": last_done,
    }


# --- Fetch from Notion API ---

async def _fetch_notion_db(database_id: str) -> list[dict[str, Any]]:
    """Fetch all pages from a Notion database with pagination."""
    if not settings.notion_api_key or not database_id:
        return []

    url = f"{NOTION_API_URL}/databases/{database_id}/query"
    results: list[dict[str, Any]] = []
    has_more = True
    start_cursor = None

    async with httpx.AsyncClient() as client:
        while has_more:
            body: dict[str, Any] = {}
            if start_cursor:
                body["start_cursor"] = start_cursor

            resp = await client.post(url, headers=_notion_headers(), json=body, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            results.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")

    return results


async def fetch_tasks_db() -> list[dict[str, Any]]:
    """Fetch and parse all pages from the Tasks database."""
    pages = await _fetch_notion_db(settings.notion_tasks_db_id)
    return [_parse_tasks_db_page(p) for p in pages]


async def fetch_chores_db() -> list[dict[str, Any]]:
    """Fetch and parse all pages from the Chores database."""
    pages = await _fetch_notion_db(settings.notion_chores_db_id)
    return [_parse_chores_db_page(p) for p in pages]


# --- Sync to local DB ---

def _upsert_tasks(db: Session, tasks_data: list[dict[str, Any]]) -> dict[str, int]:
    created = 0
    updated = 0

    for task_data in tasks_data:
        notion_id = task_data["notion_id"]
        existing = db.query(TaskDB).filter(TaskDB.notion_id == notion_id).first()

        if existing:
            for key, value in task_data.items():
                if key != "notion_id":
                    setattr(existing, key, value)
            updated += 1
        else:
            new_task = TaskDB(**task_data)
            db.add(new_task)
            created += 1

    return {"created": created, "updated": updated}


async def sync_tasks_from_notion(db: Session) -> dict[str, int]:
    """Sync from both Tasks and Chores databases. Returns counts."""
    total_created = 0
    total_updated = 0

    # Sync Tasks DB
    if settings.notion_tasks_db_id:
        tasks = await fetch_tasks_db()
        result = _upsert_tasks(db, tasks)
        total_created += result["created"]
        total_updated += result["updated"]

    # Sync Chores DB
    if settings.notion_chores_db_id:
        chores = await fetch_chores_db()
        result = _upsert_tasks(db, chores)
        total_created += result["created"]
        total_updated += result["updated"]

    db.commit()
    return {"created": total_created, "updated": total_updated}

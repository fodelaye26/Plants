"""Service to sync household tasks from Notion to the local database."""

from datetime import date
from typing import Any

import httpx
from sqlalchemy.orm import Session

from ..config import settings
from ..models.task import Recurrence, TaskCategory, TaskDB, TaskMode, TaskStatus, TimeWindow

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _notion_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.notion_api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _safe_select(prop: dict[str, Any] | None, enum_cls: type, default: str) -> str:
    if prop and prop.get("select") and prop["select"].get("name"):
        val = prop["select"]["name"].lower().replace(" ", "_")
        try:
            return enum_cls(val).value
        except ValueError:
            pass
    return default


def _safe_text(prop: dict[str, Any] | None) -> str | None:
    if prop and prop.get("rich_text"):
        parts = prop["rich_text"]
        return "".join(p.get("plain_text", "") for p in parts) if parts else None
    return None


def _safe_title(prop: dict[str, Any] | None) -> str:
    if prop and prop.get("title"):
        parts = prop["title"]
        return "".join(p.get("plain_text", "") for p in parts) if parts else "Untitled"
    return "Untitled"


def _safe_date(prop: dict[str, Any] | None) -> date | None:
    if prop and prop.get("date") and prop["date"].get("start"):
        try:
            return date.fromisoformat(prop["date"]["start"])
        except ValueError:
            pass
    return None


def _safe_checkbox(prop: dict[str, Any] | None) -> bool:
    if prop and "checkbox" in prop:
        return prop["checkbox"]
    return False


def _safe_number(prop: dict[str, Any] | None, default: int = 1) -> int:
    if prop and prop.get("number") is not None:
        return int(prop["number"])
    return default


def _safe_person(prop: dict[str, Any] | None) -> str | None:
    if prop and prop.get("people"):
        people = prop["people"]
        if people:
            return people[0].get("name", None)
    return None


def _safe_url(prop: dict[str, Any] | None) -> str | None:
    if prop and prop.get("url"):
        return prop["url"]
    return None


def _parse_notion_task(page: dict[str, Any]) -> dict[str, Any]:
    """Parse a Notion page into task fields."""
    props = page.get("properties", {})

    return {
        "notion_id": page["id"],
        "title": _safe_title(props.get("Task Name") or props.get("Name")),
        "assigned_to": _safe_person(props.get("Assigned To")),
        "mode": _safe_select(props.get("Mode"), TaskMode, TaskMode.ADULT.value),
        "category": _safe_select(props.get("Category"), TaskCategory, TaskCategory.CLEANING.value),
        "status": _safe_select(props.get("Status"), TaskStatus, TaskStatus.NOT_STARTED.value),
        "recurrence": _safe_select(props.get("Recurrence"), Recurrence, Recurrence.ONCE.value),
        "due_date": _safe_date(props.get("Due Date")),
        "time_window": _safe_select(props.get("Time Window"), TimeWindow, TimeWindow.ANYTIME.value),
        "difficulty": _safe_number(props.get("Difficulty"), 1),
        "points": _safe_number(props.get("Points"), 1),
        "kid_friendly": _safe_checkbox(props.get("Kid Friendly")),
        "needs_parent_help": _safe_checkbox(props.get("Needs Parent Help")),
        "icon_key": _safe_text(props.get("Icon Key")),
        "voice_prompt_url": _safe_url(props.get("Voice Prompt URL")),
        "active": _safe_checkbox(props.get("Active")) if props.get("Active") else True,
    }


async def fetch_notion_tasks() -> list[dict[str, Any]]:
    """Fetch all tasks from the Notion tasks database."""
    if not settings.notion_api_key or not settings.notion_tasks_db_id:
        return []

    url = f"{NOTION_API_URL}/databases/{settings.notion_tasks_db_id}/query"
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

    return [_parse_notion_task(page) for page in results]


async def sync_tasks_from_notion(db: Session) -> dict[str, int]:
    """Sync tasks from Notion into the local database. Returns counts of created/updated."""
    tasks_data = await fetch_notion_tasks()
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

    db.commit()
    return {"created": created, "updated": updated}

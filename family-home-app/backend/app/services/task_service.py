"""Business logic for task operations."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..models.task import TaskCreate, TaskDB, TaskStatus, TaskUpdate


def get_tasks(
    db: Session,
    assigned_to: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    due_date: Optional[date] = None,
    active_only: bool = True,
) -> list[TaskDB]:
    query = db.query(TaskDB)
    if active_only:
        query = query.filter(TaskDB.active.is_(True))
    if assigned_to:
        query = query.filter(TaskDB.assigned_to == assigned_to)
    if status:
        query = query.filter(TaskDB.status == status.value)
    if due_date:
        query = query.filter(TaskDB.due_date == due_date)
    return query.order_by(TaskDB.due_date.asc().nullslast(), TaskDB.id).all()


def get_today_tasks(db: Session, assigned_to: Optional[str] = None) -> list[TaskDB]:
    today = date.today()
    query = db.query(TaskDB).filter(
        TaskDB.active.is_(True),
        TaskDB.status != TaskStatus.DONE.value,
        (TaskDB.due_date <= today) | (TaskDB.due_date.is_(None)),
    )
    if assigned_to:
        query = query.filter(TaskDB.assigned_to == assigned_to)
    return query.order_by(TaskDB.due_date.asc().nullslast(), TaskDB.id).all()


def create_task(db: Session, task_in: TaskCreate) -> TaskDB:
    task = TaskDB(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> TaskDB | None:
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        return None
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def complete_task(db: Session, task_id: int) -> TaskDB | None:
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not task:
        return None
    task.status = TaskStatus.DONE.value
    task.last_completed = datetime.now()
    db.commit()
    db.refresh(task)
    return task


def get_family_board(db: Session) -> dict[str, list[TaskDB]]:
    """Group active tasks by family member for the board view."""
    tasks = get_tasks(db, active_only=True)
    board: dict[str, list[TaskDB]] = {}
    for task in tasks:
        member = task.assigned_to or "Unassigned"
        board.setdefault(member, []).append(task)
    return board

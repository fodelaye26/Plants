from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from ..services.task_service import (
    complete_task,
    create_task,
    get_family_board,
    get_tasks,
    get_today_tasks,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    assigned_to: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    due_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return get_tasks(db, assigned_to=assigned_to, status=status, due_date=due_date)


@router.get("/today", response_model=list[TaskResponse])
def list_today_tasks(
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_today_tasks(db, assigned_to=assigned_to)


@router.get("/board")
def family_board(db: Session = Depends(get_db)):
    board = get_family_board(db)
    return {
        member: [TaskResponse.model_validate(t) for t in tasks]
        for member, tasks in board.items()
    }


@router.post("/", response_model=TaskResponse, status_code=201)
def add_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, task_in)


@router.patch("/{task_id}", response_model=TaskResponse)
def modify_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def mark_complete(task_id: int, db: Session = Depends(get_db)):
    task = complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

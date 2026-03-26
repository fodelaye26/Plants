from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.reminder import ReminderResponse, ReminderTone
from ..services.reminder_engine import generate_reminder, get_reminder_history

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/generate")
def get_reminder(
    member: Optional[str] = None,
    tone: ReminderTone = ReminderTone.CALM,
    db: Session = Depends(get_db),
):
    result = generate_reminder(db, member_name=member, tone=tone)
    return result


@router.get("/history", response_model=list[ReminderResponse])
def reminder_history(
    member: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return get_reminder_history(db, member_name=member, limit=limit)

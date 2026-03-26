from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from ..database import Base


class ReminderTone(str, Enum):
    CALM = "calm"
    PLAYFUL = "playful"
    COACH = "coach"


class ReminderDB(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_member = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    tone = Column(String, default=ReminderTone.CALM)
    time_window = Column(String, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ReminderResponse(BaseModel):
    id: int
    target_member: Optional[str] = None
    message: str
    tone: ReminderTone = ReminderTone.CALM
    time_window: str
    sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

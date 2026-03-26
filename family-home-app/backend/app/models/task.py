from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"


class TaskMode(str, Enum):
    ADULT = "adult"
    KID = "kid"
    FAMILY = "family"


class TaskCategory(str, Enum):
    KITCHEN = "kitchen"
    LAUNDRY = "laundry"
    TOYS = "toys"
    CLEANING = "cleaning"
    BEDTIME = "bedtime"
    SCHOOL = "school"
    OUTDOOR = "outdoor"
    ADMIN = "admin"


class TimeWindow(str, Enum):
    MORNING = "morning"
    AFTER_SCHOOL = "after_school"
    EVENING = "evening"
    ANYTIME = "anytime"


class Recurrence(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONCE = "once"


# SQLAlchemy model
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notion_id = Column(String, unique=True, nullable=True, index=True)
    title = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)
    mode = Column(String, default=TaskMode.ADULT)
    category = Column(String, default=TaskCategory.CLEANING)
    status = Column(String, default=TaskStatus.NOT_STARTED)
    recurrence = Column(String, default=Recurrence.ONCE)
    due_date = Column(Date, nullable=True)
    time_window = Column(String, default=TimeWindow.ANYTIME)
    difficulty = Column(Integer, default=1)
    points = Column(Integer, default=1)
    kid_friendly = Column(Boolean, default=False)
    needs_parent_help = Column(Boolean, default=False)
    icon_key = Column(String, nullable=True)
    voice_prompt_url = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    last_completed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# Pydantic schemas
class TaskBase(BaseModel):
    title: str
    assigned_to: Optional[str] = None
    mode: TaskMode = TaskMode.ADULT
    category: TaskCategory = TaskCategory.CLEANING
    recurrence: Recurrence = Recurrence.ONCE
    due_date: Optional[date] = None
    time_window: TimeWindow = TimeWindow.ANYTIME
    difficulty: int = 1
    points: int = 1
    kid_friendly: bool = False
    needs_parent_help: bool = False
    icon_key: Optional[str] = None
    voice_prompt_url: Optional[str] = None
    active: bool = True


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[TaskStatus] = None
    mode: Optional[TaskMode] = None
    category: Optional[TaskCategory] = None
    due_date: Optional[date] = None
    time_window: Optional[TimeWindow] = None
    difficulty: Optional[int] = None
    points: Optional[int] = None
    kid_friendly: Optional[bool] = None
    active: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    notion_id: Optional[str] = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    last_completed: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

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
    ARCHIVED = "archived"
    SKIPPED = "skipped"


class TaskMode(str, Enum):
    ADULT = "adult"
    KID = "kid"
    FAMILY = "family"


class TaskSource(str, Enum):
    """Which Notion database the task came from."""
    TASKS = "tasks"
    CHORES = "chores"
    MANUAL = "manual"


class TaskCategory(str, Enum):
    """Room-based categories matching Notion Chores 'Rooms' property."""
    KITCHEN = "kitchen"
    DINING_ROOM = "dining_room"
    LIVING_ROOM = "living_room"
    MASTER_BEDROOM = "master_bedroom"
    MASTER_BATHROOM = "master_bathroom"
    BATHROOM = "bathroom"
    OFFICE = "office"
    STAIRWELL = "stairwell"
    OUTDOOR = "outdoor"
    GENERAL = "general"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimeWindow(str, Enum):
    MORNING = "morning"
    AFTER_SCHOOL = "after_school"
    EVENING = "evening"
    ANYTIME = "anytime"


class Recurrence(str, Enum):
    """Matches Notion Chores 'Frequency' property."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    SEASONALLY = "seasonally"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    ONCE = "once"


# SQLAlchemy model
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notion_id = Column(String, unique=True, nullable=True, index=True)
    source = Column(String, default=TaskSource.MANUAL)
    title = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)
    mode = Column(String, default=TaskMode.ADULT)
    category = Column(String, default=TaskCategory.GENERAL)
    status = Column(String, default=TaskStatus.NOT_STARTED)
    priority = Column(String, default=Priority.MEDIUM)
    recurrence = Column(String, default=Recurrence.ONCE)
    due_date = Column(Date, nullable=True)
    time_window = Column(String, default=TimeWindow.ANYTIME)
    project_name = Column(String, nullable=True)  # Room/project from Notion Projects
    rooms = Column(String, nullable=True)          # JSON list of rooms from Chores DB
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
    source: TaskSource = TaskSource.MANUAL
    mode: TaskMode = TaskMode.ADULT
    category: TaskCategory = TaskCategory.GENERAL
    priority: Priority = Priority.MEDIUM
    recurrence: Recurrence = Recurrence.ONCE
    due_date: Optional[date] = None
    time_window: TimeWindow = TimeWindow.ANYTIME
    project_name: Optional[str] = None
    rooms: Optional[str] = None
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
    priority: Optional[Priority] = None
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

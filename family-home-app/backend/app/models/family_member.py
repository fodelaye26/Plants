from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class MemberRole(str, Enum):
    ADULT = "adult"
    KID = "kid"


class FamilyMemberDB(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notion_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    role = Column(String, default=MemberRole.ADULT)
    avatar = Column(String, nullable=True)
    color_theme = Column(String, default="#FFB347")
    points_total = Column(Integer, default=0)
    level = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


# Pydantic schemas
class FamilyMemberBase(BaseModel):
    name: str
    role: MemberRole = MemberRole.ADULT
    avatar: Optional[str] = None
    color_theme: str = "#FFB347"


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberResponse(FamilyMemberBase):
    id: int
    notion_id: Optional[str] = None
    points_total: int = 0
    level: int = 1
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

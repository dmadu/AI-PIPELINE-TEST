"""Pydantic models for the task API."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: Status = Status.todo


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[Status] = None


class Task(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime


def now() -> datetime:
    """Current UTC time."""
    return datetime.now(timezone.utc)

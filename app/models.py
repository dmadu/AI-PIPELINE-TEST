"""Pydantic schemas used by the API."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class TaskCreate(BaseModel):
    """Payload accepted when creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = False


class TaskUpdate(BaseModel):
    """Payload accepted when partially updating a task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None


class Task(BaseModel):
    """A stored task returned by the API."""

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

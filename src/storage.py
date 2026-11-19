"""Thread-safe in-memory task store."""

from threading import Lock
from typing import Dict, List, Optional

from .models import Status, Task, TaskCreate, TaskUpdate, now


class NotFound(Exception):
    """Raised when a task id does not exist."""


class TaskStore:
    def __init__(self) -> None:
        self._items: Dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def create(self, data: TaskCreate) -> Task:
        with self._lock:
            stamp = now()
            task = Task(
                id=self._next_id,
                created_at=stamp,
                updated_at=stamp,
                **data.model_dump(),
            )
            self._items[task.id] = task
            self._next_id += 1
            return task

    def list(self, status: Optional[Status] = None) -> List[Task]:
        with self._lock:
            items = list(self._items.values())
        if status is not None:
            items = [t for t in items if t.status == status]
        return sorted(items, key=lambda t: t.id)

    def get(self, task_id: int) -> Task:
        with self._lock:
            task = self._items.get(task_id)
        if task is None:
            raise NotFound(task_id)
        return task

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        with self._lock:
            task = self._items.get(task_id)
            if task is None:
                raise NotFound(task_id)
            patch = data.model_dump(exclude_unset=True, exclude_none=True)
            updated = task.model_copy(update={**patch, "updated_at": now()})
            self._items[task_id] = updated
            return updated

    def delete(self, task_id: int) -> None:
        with self._lock:
            if self._items.pop(task_id, None) is None:
                raise NotFound(task_id)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._next_id = 1


store = TaskStore()

"""Thread-safe in-memory task store."""

from threading import Lock
from typing import Dict, List, Optional

from .models import Task, TaskCreate, TaskUpdate, _now


class TaskStore:
    """Keeps tasks in a dictionary guarded by a lock."""

    def __init__(self) -> None:
        self._items: Dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def list(self, completed: Optional[bool] = None) -> List[Task]:
        """Return all tasks, optionally filtered by completion state."""
        with self._lock:
            items = list(self._items.values())
        if completed is not None:
            items = [item for item in items if item.completed == completed]
        return sorted(items, key=lambda item: item.id)

    def get(self, task_id: int) -> Optional[Task]:
        """Return a single task or None."""
        with self._lock:
            return self._items.get(task_id)

    def create(self, payload: TaskCreate) -> Task:
        """Store a new task and return it."""
        with self._lock:
            task = Task(id=self._next_id, **payload.model_dump())
            self._items[task.id] = task
            self._next_id += 1
            return task

    def update(self, task_id: int, payload: TaskUpdate) -> Optional[Task]:
        """Apply the provided fields to a task."""
        with self._lock:
            task = self._items.get(task_id)
            if task is None:
                return None
            changes = payload.model_dump(exclude_unset=True)
            if changes:
                task = task.model_copy(update={**changes, "updated_at": _now()})
                self._items[task_id] = task
            return task

    def delete(self, task_id: int) -> bool:
        """Remove a task. Return True if it existed."""
        with self._lock:
            return self._items.pop(task_id, None) is not None

    def clear(self) -> None:
        """Drop all tasks. Used by tests."""
        with self._lock:
            self._items.clear()
            self._next_id = 1


store = TaskStore()

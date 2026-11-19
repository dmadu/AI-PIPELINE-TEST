"""FastAPI application exposing the task endpoints."""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status

from .models import Task, TaskCreate, TaskUpdate
from .storage import store

app = FastAPI(title="Task API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    """Report that the service is running."""
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task])
def list_tasks(completed: Optional[bool] = Query(default=None)) -> List[Task]:
    """Return tasks, optionally filtered by completion state."""
    return store.list(completed)


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    """Create a task."""
    return store.create(payload)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    """Return a single task."""
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    """Update selected fields of a task."""
    task = store.update(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    """Delete a task."""
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

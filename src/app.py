"""FastAPI application exposing a task CRUD API."""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status as http_status

from .models import Status, Task, TaskCreate, TaskUpdate
from .storage import NotFound, store

app = FastAPI(title="Task API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=http_status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    return store.create(payload)


@app.get("/tasks", response_model=List[Task])
def list_tasks(status: Optional[Status] = Query(default=None)) -> List[Task]:
    return store.list(status)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    try:
        return store.get(task_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    try:
        return store.update(task_id, payload)
    except NotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    try:
        store.delete(task_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Task not found")

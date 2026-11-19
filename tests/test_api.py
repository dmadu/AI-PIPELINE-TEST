"""End-to-end tests for the task endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Start every test with an empty store."""
    store.clear()
    yield
    store.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get():
    created = client.post("/tasks", json={"title": "Write docs"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    fetched = client.get(f"/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Write docs"
    assert fetched.json()["completed"] is False


def test_list_with_filter():
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B", "completed": True})

    assert len(client.get("/tasks").json()) == 2
    done = client.get("/tasks", params={"completed": True}).json()
    assert len(done) == 1
    assert done[0]["title"] == "B"


def test_update():
    task_id = client.post("/tasks", json={"title": "Old"}).json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "Old"


def test_delete():
    task_id = client.post("/tasks", json={"title": "Temp"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_missing_task_returns_404():
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"title": "X"}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404


def test_validation_rejects_empty_title():
    assert client.post("/tasks", json={"title": ""}).status_code == 422

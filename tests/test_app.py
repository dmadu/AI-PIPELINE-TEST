"""API tests."""

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.storage import store


@pytest.fixture(autouse=True)
def clean_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get(client):
    created = client.post("/tasks", json={"title": "write docs"})
    assert created.status_code == 201
    task = created.json()
    assert task["id"] == 1
    assert task["status"] == "todo"

    fetched = client.get(f"/tasks/{task['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "write docs"


def test_list_and_filter(client):
    client.post("/tasks", json={"title": "a"})
    client.post("/tasks", json={"title": "b", "status": "done"})

    assert len(client.get("/tasks").json()) == 2
    filtered = client.get("/tasks", params={"status": "done"}).json()
    assert [t["title"] for t in filtered] == ["b"]


def test_partial_update(client):
    task_id = client.post("/tasks", json={"title": "a"}).json()["id"]
    updated = client.patch(f"/tasks/{task_id}", json={"status": "doing"})
    assert updated.status_code == 200
    body = updated.json()
    assert body["status"] == "doing"
    assert body["title"] == "a"


def test_delete(client):
    task_id = client.post("/tasks", json={"title": "a"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"title": "x"}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404


def test_validation_errors(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={}).status_code == 422
    assert client.post("/tasks", json={"title": "a", "status": "nope"}).status_code == 422

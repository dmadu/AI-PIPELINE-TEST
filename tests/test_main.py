import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.store import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    store.clear()
    yield
    store.clear()


def make_item(name="Widget", price=9.5):
    return client.post("/items", json={"name": name, "price": price})


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get():
    created = make_item()
    assert created.status_code == 201
    item_id = created.json()["id"]
    fetched = client.get(f"/items/{item_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Widget"


def test_list_items():
    make_item("A")
    make_item("B")
    assert len(client.get("/items").json()) == 2


def test_replace_item():
    item_id = make_item().json()["id"]
    res = client.put(f"/items/{item_id}", json={"name": "New", "price": 1.0})
    assert res.status_code == 200
    assert res.json()["name"] == "New"


def test_delete_item():
    item_id = make_item().json()["id"]
    assert client.delete(f"/items/{item_id}").status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_missing_item_returns_404():
    assert client.get("/items/999").status_code == 404


def test_validation_error():
    res = client.post("/items", json={"name": "", "price": -1})
    assert res.status_code == 422

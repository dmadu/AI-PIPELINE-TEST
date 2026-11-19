from typing import List

from fastapi import FastAPI, HTTPException, status

from .models import Item, ItemCreate
from .store import store

app = FastAPI(title="Items API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/items", response_model=List[Item])
def list_items() -> List[Item]:
    return store.list()


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    return store.create(payload)


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    item = store.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=Item)
def replace_item(item_id: int, payload: ItemCreate) -> Item:
    item = store.replace(item_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    if not store.delete(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

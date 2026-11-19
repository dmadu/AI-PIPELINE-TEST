from itertools import count
from typing import Dict, List, Optional

from .models import Item, ItemCreate


class ItemStore:
    """Simple in-memory item repository."""

    def __init__(self) -> None:
        self._items: Dict[int, Item] = {}
        self._ids = count(1)

    def list(self) -> List[Item]:
        return list(self._items.values())

    def get(self, item_id: int) -> Optional[Item]:
        return self._items.get(item_id)

    def create(self, data: ItemCreate) -> Item:
        item = Item(id=next(self._ids), **data.model_dump())
        self._items[item.id] = item
        return item

    def replace(self, item_id: int, data: ItemCreate) -> Optional[Item]:
        if item_id not in self._items:
            return None
        item = Item(id=item_id, **data.model_dump())
        self._items[item_id] = item
        return item

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None

    def clear(self) -> None:
        self._items.clear()


store = ItemStore()

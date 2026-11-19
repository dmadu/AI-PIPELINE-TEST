from typing import Optional

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Payload accepted when creating or replacing an item."""

    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemCreate):
    """Stored item, including its generated identifier."""

    id: int

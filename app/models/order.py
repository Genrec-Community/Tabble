from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .dish import Dish


class OrderItemBase(BaseModel):
    dish_id: int
    quantity: int = 1
    remarks: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    dish: Optional[Dish] = None

    # Add dish_name property to ensure it's always available
    @property
    def dish_name(self) -> str:
        if self.dish:
            return self.dish.name
        return "Unknown Dish"

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2


class OrderBase(BaseModel):
    table_number: int
    unique_id: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    username: Optional[str] = None
    password: Optional[str] = None


class OrderUpdate(BaseModel):
    status: str


class Order(OrderBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []
    person_id: Optional[int] = None
    person_name: Optional[str] = None
    visit_count: Optional[int] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2

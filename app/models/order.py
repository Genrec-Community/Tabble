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

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    table_number: int
    unique_id: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: str

class Order(OrderBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        orm_mode = True

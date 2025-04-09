from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: float
    quantity: int

class DishCreate(DishBase):
    pass

class DishUpdate(DishBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    image_path: Optional[str] = None

class Dish(DishBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

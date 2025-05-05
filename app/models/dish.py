from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: float
    quantity: int
    discount: Optional[float] = 0
    is_offer: Optional[int] = 0
    is_special: Optional[int] = 0

class DishCreate(DishBase):
    pass

class DishUpdate(DishBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    image_path: Optional[str] = None
    discount: Optional[float] = None
    is_offer: Optional[int] = None
    is_special: Optional[int] = None

class Dish(DishBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2

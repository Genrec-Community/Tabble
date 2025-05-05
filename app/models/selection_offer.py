from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SelectionOfferBase(BaseModel):
    min_amount: float
    discount_amount: float
    is_active: bool = True
    description: Optional[str] = None


class SelectionOfferCreate(SelectionOfferBase):
    pass


class SelectionOfferUpdate(BaseModel):
    min_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class SelectionOffer(SelectionOfferBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2

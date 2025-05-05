from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoyaltyProgramBase(BaseModel):
    visit_count: int
    discount_percentage: float
    is_active: bool = True


class LoyaltyProgramCreate(LoyaltyProgramBase):
    pass


class LoyaltyProgramUpdate(BaseModel):
    visit_count: Optional[int] = None
    discount_percentage: Optional[float] = None
    is_active: Optional[bool] = None


class LoyaltyProgram(LoyaltyProgramBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2

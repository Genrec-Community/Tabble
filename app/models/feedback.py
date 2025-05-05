from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackBase(BaseModel):
    order_id: int
    rating: int
    comment: Optional[str] = None
    person_id: Optional[int] = None


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2

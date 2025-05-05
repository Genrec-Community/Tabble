from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SettingsBase(BaseModel):
    hotel_name: str
    address: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    tax_id: Optional[str] = None
    logo_path: Optional[str] = None


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(BaseModel):
    hotel_name: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    tax_id: Optional[str] = None
    logo_path: Optional[str] = None


class Settings(SettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2

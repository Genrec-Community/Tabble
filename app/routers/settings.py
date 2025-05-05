from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime, timezone

from ..database import get_db, Settings
from ..models.settings import Settings as SettingsModel, SettingsUpdate

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)


# Get hotel settings
@router.get("/", response_model=SettingsModel)
def get_settings(db: Session = Depends(get_db)):
    # Get the first settings record or create one if it doesn't exist
    settings = db.query(Settings).first()
    
    if not settings:
        # Create default settings
        settings = Settings(
            hotel_name="Tabble Hotel",
            address="123 Main Street, City",
            contact_number="+1 123-456-7890",
            email="info@tabblehotel.com",
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


# Update hotel settings
@router.put("/", response_model=SettingsModel)
async def update_settings(
    hotel_name: str = Form(...),
    address: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    tax_id: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Get existing settings or create new
    settings = db.query(Settings).first()
    
    if not settings:
        settings = Settings(
            hotel_name=hotel_name,
            address=address,
            contact_number=contact_number,
            email=email,
            tax_id=tax_id,
        )
        db.add(settings)
    else:
        # Update fields
        settings.hotel_name = hotel_name
        settings.address = address
        settings.contact_number = contact_number
        settings.email = email
        settings.tax_id = tax_id
    
    # Handle logo upload if provided
    if logo:
        # Create directory if it doesn't exist
        os.makedirs("app/static/images/logo", exist_ok=True)
        
        # Save logo
        logo_path = f"app/static/images/logo/hotel_logo_{logo.filename}"
        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        
        # Update settings with logo path
        settings.logo_path = f"/static/images/logo/hotel_logo_{logo.filename}"
    
    # Update timestamp
    settings.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(settings)
    
    return settings

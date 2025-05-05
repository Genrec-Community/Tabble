from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from ..database import get_db, Feedback as FeedbackModel, Order, Person
from ..models.feedback import Feedback, FeedbackCreate

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)


# Create new feedback
@router.post("/", response_model=Feedback)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    # Check if order exists
    db_order = db.query(Order).filter(Order.id == feedback.order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if person exists if person_id is provided
    if feedback.person_id:
        db_person = db.query(Person).filter(Person.id == feedback.person_id).first()
        if not db_person:
            raise HTTPException(status_code=404, detail="Person not found")

    # Create feedback
    db_feedback = FeedbackModel(
        order_id=feedback.order_id,
        person_id=feedback.person_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=datetime.now(timezone.utc),
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


# Get all feedback
@router.get("/", response_model=List[Feedback])
def get_all_feedback(db: Session = Depends(get_db)):
    return db.query(FeedbackModel).all()


# Get feedback by order_id
@router.get("/order/{order_id}", response_model=Feedback)
def get_feedback_by_order(order_id: int, db: Session = Depends(get_db)):
    db_feedback = db.query(FeedbackModel).filter(FeedbackModel.order_id == order_id).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback


# Get feedback by person_id
@router.get("/person/{person_id}", response_model=List[Feedback])
def get_feedback_by_person(person_id: int, db: Session = Depends(get_db)):
    return db.query(FeedbackModel).filter(FeedbackModel.person_id == person_id).all()

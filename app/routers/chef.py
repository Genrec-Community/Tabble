from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db, Dish, Order, OrderItem
from ..models.dish import Dish as DishModel
from ..models.order import Order as OrderModel

router = APIRouter(
    prefix="/chef",
    tags=["chef"],
    responses={404: {"description": "Not found"}},
)

# Add an API endpoint to get completed orders count
@router.get("/api/completed-orders-count")
def get_completed_orders_count(db: Session = Depends(get_db)):
    completed_orders = db.query(Order).filter(Order.status == "completed").count()
    return {"count": completed_orders}

# Get pending orders
@router.get("/orders/pending", response_model=List[OrderModel])
def get_pending_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.status == "pending").all()
    return orders

# Mark order as completed
@router.put("/orders/{order_id}/complete")
def complete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    db_order.status = "completed"
    db_order.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Order marked as completed"}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..database import get_db, Dish, Order, OrderItem
from ..models.dish import Dish as DishModel
from ..models.order import OrderCreate, Order as OrderModel

router = APIRouter(
    prefix="/customer",
    tags=["customer"],
    responses={404: {"description": "Not found"}},
)

# Get all dishes for menu
@router.get("/api/menu", response_model=List[DishModel])
def get_menu(category: str = None, db: Session = Depends(get_db)):
    if category:
        dishes = db.query(Dish).filter(Dish.category == category).all()
    else:
        dishes = db.query(Dish).all()
    return dishes

# Get all dish categories
@router.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Dish.category).distinct().all()
    return [category[0] for category in categories]

# Create new order
@router.post("/api/orders", response_model=OrderModel)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Create order
    db_order = Order(
        table_number=order.table_number,
        unique_id=order.unique_id,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create order items
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            dish_id=item.dish_id,
            quantity=item.quantity,
            remarks=item.remarks
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return db_order

# Get order status
@router.get("/api/orders/{order_id}", response_model=OrderModel)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Request payment for order
@router.put("/api/orders/{order_id}/payment")
def request_payment(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status != "completed":
        raise HTTPException(status_code=400, detail="Order must be completed before payment")

    db_order.status = "payment_requested"
    db_order.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Payment requested"}

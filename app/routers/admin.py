from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from ..database import get_db, Order, Dish, OrderItem
from ..models.order import Order as OrderModel
from ..models.dish import Dish as DishModel, DishCreate, DishUpdate

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# Get all orders
@router.get("/orders", response_model=List[OrderModel])
def get_all_orders(status: str = None, db: Session = Depends(get_db)):
    if status:
        orders = db.query(Order).filter(Order.status == status).all()
    else:
        orders = db.query(Order).all()
    return orders

# Get all dishes
@router.get("/api/dishes", response_model=List[DishModel])
def get_all_dishes(db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()
    return dishes

# Get dish by ID
@router.get("/api/dishes/{dish_id}", response_model=DishModel)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

# Create new dish
@router.post("/api/dishes", response_model=DishModel)
async def create_dish(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Create dish object
    db_dish = Dish(
        name=name,
        description=description,
        category=category,
        price=price,
        quantity=quantity
    )

    # Save dish to database
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)

    # Handle image upload if provided
    if image:
        # Create directory if it doesn't exist
        os.makedirs("app/static/images/dishes", exist_ok=True)

        # Save image
        image_path = f"app/static/images/dishes/{db_dish.id}_{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Update dish with image path
        db_dish.image_path = f"/static/images/dishes/{db_dish.id}_{image.filename}"
        db.commit()
        db.refresh(db_dish)

    return db_dish

# Update dish
@router.put("/api/dishes/{dish_id}", response_model=DishModel)
async def update_dish(
    dish_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    quantity: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Get existing dish
    db_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")

    # Update fields if provided
    if name:
        db_dish.name = name
    if description:
        db_dish.description = description
    if category:
        db_dish.category = category
    if price:
        db_dish.price = price
    if quantity:
        db_dish.quantity = quantity

    # Handle image upload if provided
    if image:
        # Create directory if it doesn't exist
        os.makedirs("app/static/images/dishes", exist_ok=True)

        # Save image
        image_path = f"app/static/images/dishes/{db_dish.id}_{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Update dish with image path
        db_dish.image_path = f"/static/images/dishes/{db_dish.id}_{image.filename}"

    # Update timestamp
    db_dish.updated_at = datetime.utcnow()

    # Save changes
    db.commit()
    db.refresh(db_dish)

    return db_dish

# Delete dish
@router.delete("/api/dishes/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")

    db.delete(db_dish)
    db.commit()

    return {"message": "Dish deleted successfully"}

# Get order statistics
@router.get("/stats/orders")
def get_order_stats(db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    completed_orders = db.query(Order).filter(Order.status == "completed").count()
    payment_requested = db.query(Order).filter(Order.status == "payment_requested").count()
    paid_orders = db.query(Order).filter(Order.status == "paid").count()

    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "payment_requested": payment_requested,
        "paid_orders": paid_orders
    }

# Mark order as paid
@router.put("/orders/{order_id}/paid")
def mark_order_paid(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status != "payment_requested":
        raise HTTPException(status_code=400, detail="Payment must be requested before marking as paid")

    db_order.status = "paid"
    db_order.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Order marked as paid"}

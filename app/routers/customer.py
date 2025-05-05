from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta

from ..database import get_db, Dish, Order, OrderItem, Person
from ..models.dish import Dish as DishModel
from ..models.order import OrderCreate, Order as OrderModel
from ..models.user import (
    PersonCreate,
    PersonLogin,
    Person as PersonModel,
    PhoneAuthRequest,
    PhoneVerifyRequest,
    UsernameRequest
)
from ..services import firebase_auth

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


# Get offer dishes
@router.get("/api/offers", response_model=List[DishModel])
def get_offers(db: Session = Depends(get_db)):
    dishes = db.query(Dish).filter(Dish.is_offer == 1).all()
    return dishes


# Get special dishes
@router.get("/api/specials", response_model=List[DishModel])
def get_specials(db: Session = Depends(get_db)):
    dishes = db.query(Dish).filter(Dish.is_special == 1).all()
    return dishes


# Get all dish categories
@router.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Dish.category).distinct().all()
    return [category[0] for category in categories]


# Register a new user or update existing user
@router.post("/api/register", response_model=PersonModel)
def register_user(user: PersonCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(Person).filter(Person.username == user.username).first()

    if db_user:
        # Update existing user's visit count and last visit time
        db_user.visit_count += 1
        db_user.last_visit = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        # Create new user
        db_user = Person(
            username=user.username,
            password=user.password,  # In a real app, you should hash this password
            visit_count=1,
            last_visit=datetime.now(timezone.utc),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


# Login user
@router.post("/api/login", response_model=Dict[str, Any])
def login_user(user_data: PersonLogin, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(Person).filter(Person.username == user_data.username).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
        )

    # Check password (in a real app, you would verify hashed passwords)
    if db_user.password != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    # Update visit count and last visit time
    db_user.visit_count += 1
    db_user.last_visit = datetime.now(timezone.utc)
    db.commit()

    # Return user info and a success message
    return {
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "visit_count": db_user.visit_count,
        },
        "message": "Login successful",
    }


# Create new order
@router.post("/api/orders", response_model=OrderModel)
def create_order(
    order: OrderCreate, person_id: int = None, db: Session = Depends(get_db)
):
    # If person_id is not provided but we have a username/password, try to find or create the user
    if not person_id and hasattr(order, "username") and hasattr(order, "password"):
        # Check if user exists
        db_user = db.query(Person).filter(Person.username == order.username).first()

        if db_user:
            # Update existing user's visit count
            db_user.visit_count += 1
            db_user.last_visit = datetime.now(timezone.utc)
            db.commit()
            person_id = db_user.id
        else:
            # Create new user
            db_user = Person(
                username=order.username,
                password=order.password,
                visit_count=1,
                last_visit=datetime.now(timezone.utc),
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            person_id = db_user.id

    # Create order
    db_order = Order(
        table_number=order.table_number,
        unique_id=order.unique_id,
        person_id=person_id,  # Link order to person if provided
        status="pending",
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Mark the table as occupied
    from ..database import Table

    db_table = db.query(Table).filter(Table.table_number == order.table_number).first()
    if db_table:
        db_table.is_occupied = True
        db_table.current_order_id = db_order.id
        db.commit()

    # Create order items
    for item in order.items:
        # Get the dish to include its information
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            continue  # Skip if dish doesn't exist

        db_item = OrderItem(
            order_id=db_order.id,
            dish_id=item.dish_id,
            quantity=item.quantity,
            remarks=item.remarks,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return db_order


# Get order status
@router.get("/api/orders/{order_id}", response_model=OrderModel)
def get_order(order_id: int, db: Session = Depends(get_db)):
    # Use joinedload to load the dish relationship for each order item
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Explicitly load dish information for each order item
    for item in order.items:
        if not hasattr(item, "dish") or item.dish is None:
            dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
            if dish:
                item.dish = dish

    return order


# Get orders by person_id
@router.get("/api/person/{person_id}/orders", response_model=List[OrderModel])
def get_person_orders(person_id: int, db: Session = Depends(get_db)):
    # Get all orders for a specific person
    orders = (
        db.query(Order)
        .filter(Order.person_id == person_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    # Explicitly load dish information for each order item
    for order in orders:
        for item in order.items:
            if not hasattr(item, "dish") or item.dish is None:
                dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
                if dish:
                    item.dish = dish

    return orders


# Request payment for order
@router.put("/api/orders/{order_id}/payment")
def request_payment(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order status to paid directly
    db_order.status = "paid"
    db_order.updated_at = datetime.now(timezone.utc)

    # Mark the table as free
    from ..database import Table

    db_table = (
        db.query(Table).filter(Table.table_number == db_order.table_number).first()
    )
    if db_table:
        db_table.is_occupied = False
        db_table.current_order_id = None
        db_table.updated_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Payment completed successfully"}


# Cancel order
@router.put("/api/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if order is in pending status
    if db_order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be cancelled"
        )

    # Check if order was created within the last 60 seconds
    current_time = datetime.now(timezone.utc)
    order_time = db_order.created_at
    time_difference = current_time - order_time

    if time_difference > timedelta(seconds=60):
        raise HTTPException(
            status_code=400,
            detail="Orders can only be cancelled within 60 seconds of placing"
        )

    # Update order status to cancelled
    db_order.status = "cancelled"
    db_order.updated_at = current_time

    # Mark the table as free if this was the current order
    from ..database import Table

    db_table = db.query(Table).filter(Table.table_number == db_order.table_number).first()
    if db_table and db_table.current_order_id == db_order.id:
        db_table.is_occupied = False
        db_table.current_order_id = None
        db_table.updated_at = current_time

    db.commit()

    return {"message": "Order cancelled successfully"}


# Get person details
@router.get("/api/person/{person_id}", response_model=PersonModel)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


# Phone authentication endpoints
@router.post("/api/phone-auth", response_model=Dict[str, Any])
def phone_auth(auth_request: PhoneAuthRequest, db: Session = Depends(get_db)):
    """
    Initiate phone authentication by sending OTP
    """
    try:
        # Validate phone number format
        if not auth_request.phone_number.startswith("+91"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number must start with +91"
            )

        # Send OTP via Firebase
        result = firebase_auth.verify_phone_number(auth_request.phone_number)

        print(f"Phone auth initiated for: {auth_request.phone_number}, table: {auth_request.table_number}")

        return {
            "success": True,
            "message": "Verification code sent successfully",
            "session_info": result.get("sessionInfo", "firebase-verification-token")
        }
    except HTTPException as e:
        print(f"HTTP Exception in phone_auth: {e.detail}")
        raise e
    except Exception as e:
        print(f"Exception in phone_auth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )


@router.post("/api/verify-otp", response_model=Dict[str, Any])
def verify_otp(verify_request: PhoneVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify OTP and authenticate user
    """
    try:
        print(f"Verifying OTP for phone: {verify_request.phone_number}")

        # Verify OTP via Firebase
        # Note: The actual OTP verification is done on the client side with Firebase
        # This is just a validation step
        firebase_auth.verify_otp(
            verify_request.phone_number,
            verify_request.verification_code
        )

        # Check if user exists in database
        user = db.query(Person).filter(Person.phone_number == verify_request.phone_number).first()

        if user:
            print(f"Existing user found: {user.username}")
            # Existing user - update visit count
            user.visit_count += 1
            user.last_visit = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)

            return {
                "success": True,
                "message": "Authentication successful",
                "user_exists": True,
                "user_id": user.id,
                "username": user.username
            }
        else:
            print(f"New user with phone: {verify_request.phone_number}")
            # New user - return flag to collect username
            return {
                "success": True,
                "message": "Authentication successful, but user not found",
                "user_exists": False
            }

    except HTTPException as e:
        print(f"HTTP Exception in verify_otp: {e.detail}")
        raise e
    except Exception as e:
        print(f"Exception in verify_otp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )


@router.post("/api/register-phone-user", response_model=Dict[str, Any])
def register_phone_user(user_request: UsernameRequest, db: Session = Depends(get_db)):
    """
    Register a new user after phone authentication
    """
    try:
        print(f"Registering new user with phone: {user_request.phone_number}, username: {user_request.username}")

        # Check if username already exists
        existing_user = db.query(Person).filter(Person.username == user_request.username).first()
        if existing_user:
            print(f"Username already exists: {user_request.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if phone number already exists
        phone_user = db.query(Person).filter(Person.phone_number == user_request.phone_number).first()
        if phone_user:
            print(f"Phone number already registered: {user_request.phone_number}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # Create new user
        new_user = Person(
            username=user_request.username,
            password="",  # No password needed for phone auth
            phone_number=user_request.phone_number,
            visit_count=1,
            last_visit=datetime.now(timezone.utc)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"User registered successfully: {new_user.id}, {new_user.username}")

        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": new_user.id,
            "username": new_user.username
        }

    except HTTPException as e:
        print(f"HTTP Exception in register_phone_user: {e.detail}")
        raise e
    except Exception as e:
        print(f"Exception in register_phone_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import os

# Database connection - Using SQLite
DATABASE_URL = "sqlite:///./tabble_new.db"  # Using the new database with offers feature
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database models
class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer, default=0)
    image_path = Column(String, nullable=True)
    discount = Column(Float, default=0)  # Discount amount (percentage)
    is_offer = Column(Integer, default=0)  # 0 = not an offer, 1 = is an offer
    is_special = Column(Integer, default=0)  # 0 = not special, 1 = today's special
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship with OrderItem
    order_items = relationship("OrderItem", back_populates="dish")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer)
    unique_id = Column(String, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    status = Column(String, default="pending")  # pending, completed, paid
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    items = relationship("OrderItem", back_populates="order")
    person = relationship("Person", back_populates="orders")


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(String, unique=True, index=True, nullable=True)  # Added phone number field
    visit_count = Column(Integer, default=1)
    last_visit = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship with Order
    orders = relationship("Order", back_populates="person")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    quantity = Column(Integer, default=1)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order")
    person = relationship("Person")


class LoyaltyProgram(Base):
    __tablename__ = "loyalty_program"

    id = Column(Integer, primary_key=True, index=True)
    visit_count = Column(Integer, unique=True)  # Number of visits required
    discount_percentage = Column(Float)  # Discount percentage
    is_active = Column(Boolean, default=True)  # Whether this loyalty tier is active
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SelectionOffer(Base):
    __tablename__ = "selection_offers"

    id = Column(Integer, primary_key=True, index=True)
    min_amount = Column(Float)  # Minimum order amount to qualify
    discount_amount = Column(Float)  # Fixed discount amount to apply
    is_active = Column(Boolean, default=True)  # Whether this offer is active
    description = Column(String, nullable=True)  # Optional description of the offer
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, unique=True)  # Table number
    is_occupied = Column(
        Boolean, default=False
    )  # Whether the table is currently occupied
    current_order_id = Column(
        Integer, ForeignKey("orders.id"), nullable=True
    )  # Current active order
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to current order
    current_order = relationship("Order", foreign_keys=[current_order_id])


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String, nullable=False, default="Tabble Hotel")
    address = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    logo_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# Create tables
def create_tables():
    # Drop the selection_offers table if it exists to force recreation
    try:
        SelectionOffer.__table__.drop(engine)
        print("Dropped selection_offers table to recreate it with the correct schema")
    except:
        print("Could not drop selection_offers table, it might not exist yet")

    # Create all tables
    Base.metadata.create_all(bind=engine)


# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

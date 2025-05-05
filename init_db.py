from app.database import (
    create_tables,
    SessionLocal,
    Dish,
    Person,
    Base,
    LoyaltyProgram,
    SelectionOffer,
    Table,
)
from sqlalchemy import create_engine
from datetime import datetime, timezone
import os
import sys


def init_db(force_reset=False):
    # Check if force_reset is enabled
    if force_reset:
        # Drop all tables and recreate them
        print("Forcing database reset...")
        Base.metadata.drop_all(
            bind=create_engine(
                "sqlite:///./tabble_new.db", connect_args={"check_same_thread": False}
            )
        )

    # Create tables
    create_tables()

    # Create a database session
    db = SessionLocal()

    # Check if dishes already exist
    existing_dishes = db.query(Dish).count()
    if existing_dishes > 0:
        print("Database already contains data. Skipping initialization.")
        return

    # Add sample dishes
    sample_dishes = [
        # Regular dishes
        Dish(
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce, mozzarella, and basil",
            category="Main Course",
            price=12.99,
            quantity=20,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        Dish(
            name="Caesar Salad",
            description="Fresh romaine lettuce with Caesar dressing, croutons, and parmesan",
            category="Appetizer",
            price=8.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        Dish(
            name="Chocolate Cake",
            description="Rich chocolate cake with ganache frosting",
            category="Dessert",
            price=6.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        Dish(
            name="Iced Tea",
            description="Refreshing iced tea with lemon",
            category="Beverage",
            price=3.99,
            quantity=30,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        Dish(
            name="Chicken Alfredo",
            description="Fettuccine pasta with creamy Alfredo sauce and grilled chicken",
            category="Main Course",
            price=15.99,
            quantity=12,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
        ),
        Dish(
            name="Garlic Bread",
            description="Toasted bread with garlic butter and herbs",
            category="Appetizer",
            price=4.99,
            quantity=25,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=0,
        ),
        # Special offer dishes
        Dish(
            name="Weekend Special Pizza",
            description="Deluxe pizza with premium toppings and extra cheese",
            category="Main Course",
            price=18.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg",
            discount=20,
            is_offer=1,
            is_special=0,
        ),
        Dish(
            name="Seafood Pasta",
            description="Fresh pasta with mixed seafood in a creamy sauce",
            category="Main Course",
            price=22.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg",
            discount=15,
            is_offer=1,
            is_special=0,
        ),
        Dish(
            name="Tiramisu",
            description="Classic Italian dessert with coffee-soaked ladyfingers and mascarpone cream",
            category="Dessert",
            price=9.99,
            quantity=8,
            image_path="/static/images/default-dish.jpg",
            discount=25,
            is_offer=1,
            is_special=0,
        ),
        # Today's special dishes
        Dish(
            name="Chef's Special Steak",
            description="Prime cut steak cooked to perfection with special house seasoning",
            category="Main Course",
            price=24.99,
            quantity=12,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=1,
        ),
        Dish(
            name="Truffle Mushroom Risotto",
            description="Creamy risotto with wild mushrooms and truffle oil",
            category="Main Course",
            price=16.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=1,
        ),
        Dish(
            name="Chocolate Lava Cake",
            description="Warm chocolate cake with a molten center, served with vanilla ice cream",
            category="Dessert",
            price=8.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg",
            discount=0,
            is_offer=0,
            is_special=1,
        ),
    ]

    # Add dishes to database
    for dish in sample_dishes:
        db.add(dish)

    # Add sample users
    sample_users = [
        Person(
            username="john_doe",
            password="password123",
            visit_count=1,
            last_visit=datetime.now(timezone.utc),
        ),
        Person(
            username="jane_smith",
            password="password456",
            visit_count=3,
            last_visit=datetime.now(timezone.utc),
        ),
        Person(
            username="guest",
            password="guest",
            visit_count=5,
            last_visit=datetime.now(timezone.utc),
        ),
    ]

    # Add users to database
    for user in sample_users:
        db.add(user)

    # Add sample loyalty program tiers
    sample_loyalty_tiers = [
        LoyaltyProgram(
            visit_count=3,
            discount_percentage=5.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        LoyaltyProgram(
            visit_count=5,
            discount_percentage=10.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        LoyaltyProgram(
            visit_count=10,
            discount_percentage=15.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        LoyaltyProgram(
            visit_count=20,
            discount_percentage=20.0,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    # Add loyalty tiers to database
    for tier in sample_loyalty_tiers:
        db.add(tier)

    # Add sample selection offers
    sample_selection_offers = [
        SelectionOffer(
            min_amount=50.0,
            discount_amount=5.0,
            is_active=True,
            description="Spend $50, get $5 off",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SelectionOffer(
            min_amount=100.0,
            discount_amount=15.0,
            is_active=True,
            description="Spend $100, get $15 off",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        SelectionOffer(
            min_amount=150.0,
            discount_amount=25.0,
            is_active=True,
            description="Spend $150, get $25 off",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    # Add selection offers to database
    for offer in sample_selection_offers:
        db.add(offer)

    # Add sample tables
    sample_tables = [
        Table(
            table_number=1,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=2,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=3,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=4,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=5,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=6,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=7,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Table(
            table_number=8,
            is_occupied=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    # Add tables to database
    for table in sample_tables:
        db.add(table)

    # Commit changes
    db.commit()

    print("Database initialized with sample data:")
    print("- Added", len(sample_dishes), "sample dishes")
    print("- Added", len(sample_users), "sample users")
    print("- Added", len(sample_loyalty_tiers), "loyalty program tiers")
    print("- Added", len(sample_selection_offers), "selection offers")
    print("- Added", len(sample_tables), "tables")

    # Close session
    db.close()


if __name__ == "__main__":
    # Create static/images directory if it doesn't exist
    os.makedirs("app/static/images", exist_ok=True)

    # Check for force reset flag
    force_reset = "--force-reset" in sys.argv

    # Initialize database
    init_db(force_reset)

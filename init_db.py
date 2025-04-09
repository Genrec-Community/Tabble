from app.database import create_tables, SessionLocal, Dish
import os

def init_db():
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
        Dish(
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce, mozzarella, and basil",
            category="Main Course",
            price=12.99,
            quantity=20,
            image_path="/static/images/default-dish.jpg"
        ),
        Dish(
            name="Caesar Salad",
            description="Fresh romaine lettuce with Caesar dressing, croutons, and parmesan",
            category="Appetizer",
            price=8.99,
            quantity=15,
            image_path="/static/images/default-dish.jpg"
        ),
        Dish(
            name="Chocolate Cake",
            description="Rich chocolate cake with ganache frosting",
            category="Dessert",
            price=6.99,
            quantity=10,
            image_path="/static/images/default-dish.jpg"
        ),
        Dish(
            name="Iced Tea",
            description="Refreshing iced tea with lemon",
            category="Beverage",
            price=3.99,
            quantity=30,
            image_path="/static/images/default-dish.jpg"
        ),
        Dish(
            name="Chicken Alfredo",
            description="Fettuccine pasta with creamy Alfredo sauce and grilled chicken",
            category="Main Course",
            price=15.99,
            quantity=12,
            image_path="/static/images/default-dish.jpg"
        ),
        Dish(
            name="Garlic Bread",
            description="Toasted bread with garlic butter and herbs",
            category="Appetizer",
            price=4.99,
            quantity=25,
            image_path="/static/images/default-dish.jpg"
        )
    ]
    
    # Add dishes to database
    for dish in sample_dishes:
        db.add(dish)
    
    # Commit changes
    db.commit()
    
    print("Database initialized with sample data.")
    
    # Close session
    db.close()

if __name__ == "__main__":
    # Create static/images directory if it doesn't exist
    os.makedirs("app/static/images", exist_ok=True)
    
    # Initialize database
    init_db()

from app.database import SessionLocal, Order, OrderItem, Dish
from datetime import datetime

def create_test_order():
    db = SessionLocal()
    try:
        # First, get a dish from the database
        dish = db.query(Dish).first()
        if not dish:
            print("No dishes found in database")
            return

        # Create a test order
        order = Order(
            table_number=1,
            unique_id="test_order_1",
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        # Add order item
        order_item = OrderItem(
            order_id=order.id,
            dish_id=dish.id,
            quantity=2,
            remarks="Test order item"
        )
        db.add(order_item)
        db.commit()

        print(f"Created test order with ID: {order.id}")

    except Exception as e:
        print(f"Error creating test order: {e}")
    finally:
        db.close()

def list_orders():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        print("\nExisting orders:")
        for order in orders:
            print(f"Order #{order.id}: Table {order.table_number}, Status: {order.status}")
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for item in items:
                dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
                print(f"  - {item.quantity}x {dish.name}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Current orders:")
    list_orders()
    
    create = input("\nCreate a test order? (y/n): ")
    if create.lower() == 'y':
        create_test_order()
        print("\nUpdated order list:")
        list_orders()
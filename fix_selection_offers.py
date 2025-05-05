import sqlite3
import os

def fix_selection_offers():
    db_path = "tabble_new.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    print(f"Fixing selection_offers table in {db_path}...")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the selection_offers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='selection_offers'")
        if not cursor.fetchone():
            print("selection_offers table does not exist! Creating it...")
            
            # Create the selection_offers table with all required columns
            cursor.execute("""
                CREATE TABLE selection_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    min_amount FLOAT NOT NULL,
                    discount_amount FLOAT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    description TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Add sample data
            cursor.execute("""
                INSERT INTO selection_offers (min_amount, discount_amount, is_active, description, created_at, updated_at)
                VALUES 
                (50.0, 5.0, 1, 'Spend $50, get $5 off', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                (100.0, 15.0, 1, 'Spend $100, get $15 off', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                (150.0, 25.0, 1, 'Spend $150, get $25 off', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            
            conn.commit()
            print("Created selection_offers table with sample data.")
        else:
            # Check if the discount_amount column exists
            cursor.execute("PRAGMA table_info(selection_offers)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if "discount_amount" not in column_names:
                print("Adding discount_amount column to selection_offers table...")
                
                # Create a new table with the correct schema
                cursor.execute("""
                    CREATE TABLE selection_offers_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        min_amount FLOAT NOT NULL,
                        discount_amount FLOAT NOT NULL DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1,
                        description TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """)
                
                # Copy data from the old table to the new one
                cursor.execute("""
                    INSERT INTO selection_offers_new (id, min_amount, is_active, description, created_at, updated_at)
                    SELECT id, min_amount, is_active, description, created_at, updated_at FROM selection_offers
                """)
                
                # Update the discount_amount based on min_amount (as a simple rule)
                cursor.execute("""
                    UPDATE selection_offers_new
                    SET discount_amount = CASE
                        WHEN min_amount <= 50 THEN 5.0
                        WHEN min_amount <= 100 THEN 15.0
                        ELSE 25.0
                    END
                """)
                
                # Drop the old table and rename the new one
                cursor.execute("DROP TABLE selection_offers")
                cursor.execute("ALTER TABLE selection_offers_new RENAME TO selection_offers")
                
                conn.commit()
                print("Added discount_amount column and populated with values.")
            else:
                print("discount_amount column already exists. No changes needed.")
        
        # Verify the table structure
        cursor.execute("PRAGMA table_info(selection_offers)")
        columns = cursor.fetchall()
        print("\nCurrent selection_offers table structure:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # Show the data
        cursor.execute("SELECT * FROM selection_offers")
        rows = cursor.fetchall()
        print("\nCurrent selection_offers data:")
        for row in rows:
            print(f"  {row}")
        
        print("\nFix completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_selection_offers()

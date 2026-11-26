
import sqlite3
import os

# Get the project folder location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database file path
DATABASE_PATH = os.path.join(BASE_DIR, "business.db")


# Create or update database
def create_database():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(investigations)")

    columns = [
        column[1] for column in cursor.fetchall()
    ]

    # Add status column if it does not exist
    if "status" not in columns:
        cursor.execute("""
            ALTER TABLE investigations
            ADD COLUMN status TEXT DEFAULT 'Pending'
        """)

    connection.commit()
    connection.close()

    print("Database updated successfully!")


if __name__ == "__main__":
    create_database()

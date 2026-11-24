import sqlite3

def create_database():
    connection = sqlite3.connect("business.db")
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

    # Check whether the status column already exists
    cursor.execute("PRAGMA table_info(investigations)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add status to the existing database without deleting records
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
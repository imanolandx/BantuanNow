import os
from database import Database

# Set environment variables for database credentials
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_DB"] = "bantuannow"

def test_insert_and_show():
    # Initialize the database connection
    db = Database()

    # Insert a new flood center
    try:
        center_name = "Test Center"
        state = "Test State"
        clothes = 100
        food = 200
        medicine_kit = 50
        mineral_water = 300

        query = """
        INSERT INTO flood_centres (centre_name, state, clothes, food, medicine_kit, mineral_water)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (center_name, state, clothes, food, medicine_kit, mineral_water)
        db.cursor.execute(query, values)
        db.conn.commit()
        print("New flood center added successfully!")
    except Exception as e:
        print(f"Failed to add new flood center: {e}")

    # Retrieve and display all flood centers
    try:
        query = "SELECT * FROM flood_centres"
        db.cursor.execute(query)
        rows = db.cursor.fetchall()
        print("Flood Centres:")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Failed to retrieve flood centers: {e}")

    # Close the database connection
    db.close()

if __name__ == "__main__":
    test_insert_and_show()
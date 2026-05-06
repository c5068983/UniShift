from app.db.connection import get_db_connection

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    with open("app/db/schema.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    
    print("✅ DB schema executed successfully")
    
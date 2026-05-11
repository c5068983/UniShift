from app.db.connection import get_db_connection

def create_user(username, email, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (username, email, password, role))

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM users WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()
    
    return user

def update_user_password(user_id, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET password = ? WHERE userId = ?
    """, (new_password, user_id))

    conn.commit()
    conn.close()
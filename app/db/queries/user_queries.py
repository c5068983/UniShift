from app.db import get_db_connection

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM users WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()
    
    return user


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE userId = ?", (user_id,))
    return cursor.fetchone()

def update_user_by_id(user_id, username, mobile_number, post_code,profile_picture):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET username = ?, mobile_number = ?, post_code = ?, profile_picture = ? 
        WHERE userId = ?
    """, (username, mobile_number, post_code, profile_picture, user_id))
    conn.commit()
    conn.close()
    
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def change_rating_by_id(user_id, points):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET rating_points = rating_points + ? 
        WHERE userId = ?
    """, (points, user_id))
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)["rating_points"]
    
    
def change_active_status_by_id(user_id, is_active):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET is_active = ? 
        WHERE userId = ?
    """, (is_active, user_id))
    conn.commit()
    conn.close()
    
def get_all_users_exclude_admins():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role != 'Admin'")
    users = cursor.fetchall()
    conn.close()
    return users
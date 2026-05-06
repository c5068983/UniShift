from werkzeug.security import generate_password_hash
from app.db.connection import get_db_connection

def seed_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    # DEFAULT ADMIN USER
    cursor.execute(""" 
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "admin",
        "admin@unishift.com",
        generate_password_hash("admin123"),
        "Admin"
    ))

    cursor.execute(""" 
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "superadmin",
        "superadmin@unishift.com",
        generate_password_hash("superadmin123"),
        "Admin"
    ))

    cursor.executemany("""
    INSERT INTO users (
        username,
        email,
        password,
        role,
        rating_points,
        mobile_number,
        post_code,
        profile_picture,
        is_active
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [

    # ================= ACTIVE USERS =================
    ("user1", "user1@test.com", generate_password_hash("user123"),
     "User", 85, "0711111111", "S1 1AA", "default_profile.png", 1),

    ("user2", "user2@test.com", generate_password_hash("user123"),
     "User", 78, "0711111112", "S2 2BB", "default_profile.png", 1),

    # ================= INACTIVE USERS (rating < 50) =================
    ("user3", "user3@test.com", generate_password_hash("user123"),
     "User", 35, "0711111117", "S7 7GG", "default_profile.png", 0)
    
    ])

    conn.commit()
    conn.close()
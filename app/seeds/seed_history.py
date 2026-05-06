from app.db.connection import get_db_connection


def seed_history():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("🔥 seed_history() is running")

    try:
        cursor.executemany("""
            INSERT INTO shift_history (
                shiftId,
                userId,
                action
            ) VALUES (?, ?, ?)
        """, [

            (2, 1, "Accepted"),
            (3, 2, "Completed"),
            (6, 2, "Accepted"),
            (9, 1, "Accepted"),
            (11, 3, "Cancelled")
        ])

        conn.commit()
        print("✅ shift_history seeded successfully")

    except Exception as e:
        print("❌ ERROR in seed_history:", e)

    finally:
        conn.close()
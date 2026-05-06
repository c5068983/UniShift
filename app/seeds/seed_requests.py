from app.db.connection import get_db_connection


def seed_requests():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("🔥 seed_requests() is running")

    try:
        cursor.executemany("""
            INSERT INTO shift_requests (
                shiftId,
                requesterId,
                status
            ) VALUES (?, ?, ?)
        """, [

            (2, 3, "Rejected"),
            (6, 2, "Accepted"),
            (9, 1, "Accepted"),
            (11, 3, "Cancelled")
        ])

        conn.commit()
        print("✅ shift_requests seeded successfully")

    except Exception as e:
        print("❌ ERROR in seed_requests:", e)

    finally:
        conn.close()
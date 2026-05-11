from app.db.connection import get_db_connection


# -----------------------------
# 1. Cancel expired OPEN shifts
# -----------------------------
def auto_cancel_expired_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE shifts
            SET status = 'Expired'
            WHERE datetime(end_datetime) <= datetime('now')
            AND status = 'Open'
        """)

        conn.commit()
        print("✅ Open shifts cancelled")

    except Exception as e:
        print("❌ Cancel shifts error:", e)

    finally:
        conn.close()


# -----------------------------------------
# 2. Complete expired ACCEPTED shifts
# + update shift_requests
# -----------------------------------------

def auto_complete_expired_accepted_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # ------------------------
        # 1. Complete shifts
        # ------------------------
        cursor.execute("""
            UPDATE shifts
            SET status = 'Completed'
            WHERE datetime(end_datetime) <= datetime('now')
            AND status = 'Accepted'
        """)

        # ------------------------
        # 2. Get affected shiftIds (IMPORTANT)
        # ------------------------
        cursor.execute("""
            SELECT shiftId FROM shifts
            WHERE datetime(end_datetime) <= datetime('now')
            AND status = 'Completed'
        """)
        completed_shift_ids = [row[0] for row in cursor.fetchall()]

        if completed_shift_ids:
            # ------------------------
            # 3. Increase user rating (+5 per completed request)
            # ------------------------
            cursor.execute(f"""
                UPDATE users
                SET rating_points = MIN(rating_points + 5, 100)
                WHERE userId IN (
                    SELECT requesterId
                    FROM shift_requests
                    WHERE shiftId IN ({','.join(['?']*len(completed_shift_ids))})
                    AND status = 'Completed'
                )
            """, completed_shift_ids)

        conn.commit()

        print("✅ Shifts + Requests completed + rating updated")

    except Exception as e:
        print("❌ Complete shifts error:", e)

    finally:
        conn.close()


# -----------------------------------------
# 3. Reject blocked users requests
# -----------------------------------------
def auto_reject_blocked_user_requests():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE shift_requests
            SET status = 'Rejected',
                updated_at = CURRENT_TIMESTAMP
            WHERE requesterId IN (
                SELECT userId FROM users WHERE isBlocked = 1
            )
            AND status = 'Pending'
        """)

        conn.commit()
        print("🚫 Blocked users requests rejected")

    except Exception as e:
        print("❌ Reject blocked users error:", e)

    finally:
        conn.close()
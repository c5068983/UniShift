from datetime import datetime
from app.db.connection import get_db_connection


def get_shifts_between(start, end):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM shifts
        WHERE start_time <= ?
        AND end_time >= ?
    """, (end, start))

    rows = cursor.fetchall()
    conn.close()

    return rows

def get_all_avaliable_shifts(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM shifts
        WHERE status = 'Open'
        ORDER BY start_datetime ASC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows

def get_shift_by_id(shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            shifts.*,
            users.role
        FROM shifts
        JOIN users ON shifts.userId = users.userId
        WHERE shifts.shiftId = ?
    """, (shift_id,))

    shift = cursor.fetchone()
    conn.close()
    return shift

def update_shift_status(shift_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE shifts SET status = ? WHERE shiftId = ?
    """, (new_status, shift_id))
    
    conn.commit()
    conn.close()
    return get_shift_by_id(shift_id)

def create_shift(user_id, title, job_description, company_name, city, post_code, hourly_rate, start_datetime, end_datetime):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO shifts (
            title,
            job_description,
            company_name,
            city,
            post_code,
            start_datetime,
            end_datetime,
            hourly_rate,
            status,
            userId
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        job_description,
        company_name,
        city,
        post_code,
        start_datetime,
        end_datetime,
        hourly_rate,
        'Open',
        user_id
    ))
    shift_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_shift_by_id(shift_id)

def get_all_posted_shifts_by_user_id_other_than_status(user_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM shifts
        WHERE userId = ? AND status != ?
        ORDER BY start_datetime DESC
    """, (user_id, status))

    rows = cursor.fetchall()
    conn.close()

    return rows

def update_shift_by_id(shift_id, title, job_description, company_name, city, post_code, hourly_rate, start_datetime, end_datetime):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shifts
        SET title = ?, job_description = ?, company_name = ?, city = ?, post_code = ?, hourly_rate = ?, start_datetime = ?, end_datetime = ?
        WHERE shiftId = ?
    """, (
        title,
        job_description,
        company_name,
        city,
        post_code,
        hourly_rate,
        start_datetime,
        end_datetime,
        shift_id
    ))

    conn.commit()
    conn.close()
    return get_shift_by_id(shift_id)

def get_shifts_by_user_id(user_id, status=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if status is not None:
        cursor.execute("""
            SELECT * FROM shifts
            WHERE userId = ? AND status = ?
            ORDER BY start_datetime DESC
        """, (user_id, status))
    else:
        cursor.execute("""
            SELECT * FROM shifts
            WHERE userId = ?
            ORDER BY start_datetime DESC
        """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_shift_by_id_with_poster(shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, u.username AS poster_name, u.email AS poster_email
        FROM shifts s
        JOIN users u ON s.userId = u.userId
        WHERE s.shiftId = ?
    """, (shift_id,))

    shift = cursor.fetchone()
    conn.close()
    return shift


def get_filtered_shifts(city=None, post_code=None, order_by="time_asc", user_id=None):

    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT *
        FROM shifts
        WHERE status = 'Open'
    """

    filters = []
    params = []

    # ================= FILTERS =================
    if city:
        filters.append("city LIKE ?")
        params.append(f"%{city}%")

    if post_code:
        filters.append("post_code LIKE ?")
        params.append(f"%{post_code}%")

    if user_id:
        filters.append("userId != ?")
        params.append(user_id)

    if filters:
        base_query += " AND " + " AND ".join(filters)

    # ================= SORTING MAP =================
    sort_map = {
        "time_asc": "start_datetime ASC",
        "time_desc": "start_datetime DESC",
        "rate_high": "hourly_rate DESC",
        "rate_low": "hourly_rate ASC",
        "hours_long": "(julianday(end_datetime) - julianday(start_datetime)) DESC",
        "hours_short": "(julianday(end_datetime) - julianday(start_datetime)) ASC",
    }

    order_clause = sort_map.get(order_by, "start_datetime ASC")

    base_query += f" ORDER BY {order_clause}"

    cursor.execute(base_query, params)
    rows = cursor.fetchall()

    conn.close()

    return rows

def get_all_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM shifts
        ORDER BY start_datetime DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

from app.db.connection import get_db_connection


def create_shift_request(shift_id, userId):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT requestId, status
        FROM shift_requests
        WHERE shiftId = ? AND requesterId = ?
    """, (shift_id, userId))

    existing = cursor.fetchone()

    # 2. If exists → UPDATE instead of INSERT
    if existing:
        cursor.execute("""
            UPDATE shift_requests
            SET status = 'Pending', updated_at = CURRENT_TIMESTAMP
            WHERE requestId = ?
        """, (existing['requestId'],))

        request_id = existing['requestId']

    # 3. If not exists → INSERT new
    else:
        cursor.execute("""
            INSERT INTO shift_requests (shiftId, requesterId, status)
            VALUES (?, ?, 'Pending')
        """, (shift_id, userId))

        request_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return get_shift_request_by_id(request_id)

def get_shift_request_by_id(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sr.*, u.role
        FROM shift_requests sr
        JOIN users u ON sr.requesterId = u.userId
        WHERE sr.requestId = ?
    """, (request_id,))

    request = cursor.fetchone()

    conn.close()
    return request


def update_shift_request_status_by_id(request_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shift_requests 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE requestId = ?
    """, (new_status, request_id))

    conn.commit()
    conn.close()
    return get_shift_request_by_id(request_id)

def get_shift_requests(shift_id, status=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if status is not None:
        cursor.execute("""
            SELECT sr.*, u.username AS user_name
            FROM shift_requests sr
            JOIN users u ON sr.requesterId = u.userId
            WHERE sr.shiftId = ? AND sr.status = ?
        """, (shift_id, status))
    else:
        cursor.execute("""
            SELECT sr.*, u.username AS user_name
            FROM shift_requests sr
            JOIN users u ON sr.requesterId = u.userId
            WHERE sr.shiftId = ?
        """, (shift_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def reject_other_requests(shift_id, accepted_request_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shift_requests 
        SET status = 'Rejected', updated_at = CURRENT_TIMESTAMP 
        WHERE shiftId = ? AND requestId != ? AND status = 'Pending'
    """, (shift_id, accepted_request_id))

    conn.commit()
    conn.close()
    
def get_shift_requests_by_user_id(user_id, status=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if status is not None:
        cursor.execute("""
            SELECT sr.*, s.title AS shift_title,s.city AS shift_city, s.start_datetime, s.end_datetime, s.hourly_rate, s.status AS shift_status
            FROM shift_requests sr
            JOIN shifts s ON sr.shiftId = s.shiftId
            WHERE sr.requesterId = ? AND sr.status = ?
        """, (user_id, status))
    else:
        cursor.execute("""
            SELECT sr.*, s.title AS shift_title,s.city AS shift_city, s.start_datetime, s.end_datetime, s.hourly_rate, s.status AS shift_status
            FROM shift_requests sr
            JOIN shifts s ON sr.shiftId = s.shiftId
            WHERE sr.requesterId = ?
        """, (user_id,)) 
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_shift_request_by_other_id(shift_id, userId):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sr.*, u.role
        FROM shift_requests sr
        JOIN users u ON sr.requesterId = u.userId
        WHERE sr.shiftId = ? AND sr.requesterId = ?
    """, (shift_id, userId))

    request = cursor.fetchone()

    conn.close()
    return request


def get_accepted_shift_requests(shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sr.*, u.username AS user_name, u.email AS user_email, u.role
        FROM shift_requests sr
        JOIN users u ON sr.requesterId = u.userId
        WHERE sr.shiftId = ? AND sr.status = 'Accepted'
    """, (shift_id,))

    request = cursor.fetchone()

    conn.close()
    return request

def cancel_all_request_by_shift_id(shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shift_requests 
        SET status = 'Cancelled', updated_at = CURRENT_TIMESTAMP 
        WHERE shiftId = ? AND status IN ('Pending', 'Accepted')
    """, (shift_id,))

    conn.commit()
    conn.close()
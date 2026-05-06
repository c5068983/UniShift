import sqlite3
from app.db.connection import get_db_connection

def log_shift_action(shift_id, user_id, action):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO shift_history (shiftId, userId, action)
        VALUES (?, ?, ?)
    """, (shift_id, user_id, action))

    conn.commit()

    history_id = cursor.lastrowid

    conn.close()

    return history_id

def get_shift_history(shift_id, status=None, userId=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            sh.*,
            u.email as user_email,
            u.username as user_name
        FROM shift_history sh
        JOIN users u ON sh.userId = u.userId
        WHERE sh.shiftId = ?
    """

    params = [shift_id]

    # optional filter: status
    if status:
        query += " AND sh.action = ?"
        params.append(status)

    # optional filter: userId
    if userId:
        query += " AND sh.userId = ?"
        params.append(userId)

    query += " ORDER BY sh.updated_at DESC"

    cursor.execute(query, params)

    history = cursor.fetchone()

    conn.close()
    return history

def update_shift_history(history_id, new_action):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE shift_history 
        SET action = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE historyId = ?
    """, (new_action, history_id))

    conn.commit()
    conn.close()
    
def get_shift_history_by_id(history_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM shift_history
        WHERE historyId = ?
    """, (history_id,))

    history = cursor.fetchone()  # ✅ not fetchall

    conn.close()
    return history

def get_all_shift_history(limit=None):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT 
            sh.*,
            u.email AS email,
            u.username AS username,
            s.title AS shift_title,
            s.company_name,
            s.city,
            s.start_datetime,
            s.end_datetime,
            s.status AS shift_status
        FROM shift_history sh
        JOIN users u ON sh.userId = u.userId
        JOIN shifts s ON sh.shiftId = s.shiftId
        ORDER BY sh.updated_at DESC
    """

    params = []

    if limit is not None:
        query += " LIMIT ?"
        params.append(int(limit))

    cursor.execute(query, params)

    history = cursor.fetchall()
    conn.close()

    return history


def get_accepted_shift_history(shift_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sh.*, u.email AS user_email, u.username AS user_name
        FROM shift_history sh
        JOIN users u ON sh.userId = u.userId
        WHERE sh.shiftId = ? AND sh.action = 'Accepted'
    """, (shift_id,))

    row = cursor.fetchone()
    conn.close()
    return row
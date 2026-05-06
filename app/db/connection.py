import sqlite3
import os

# Get current file directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build full path to database file
DB_PATH = os.path.join(BASE_DIR, "unishift.db")
print("USING DB:", DB_PATH)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows column-name access
    return conn
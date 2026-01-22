import sqlite3
from pathlib import Path

DB_PATH = Path("attendance.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT,
            department TEXT,
            designation TEXT,
            biometric_ref TEXT UNIQUE
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time_in TEXT,
            time_out TEXT,
            status TEXT NOT NULL,
            UNIQUE(teacher_id, date),
            FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
        );
        """)

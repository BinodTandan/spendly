import calendar
import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _day_in_current_month(day):
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return date(today.year, today.month, min(day, last_day)).isoformat()


def seed_db():
    conn = get_db()
    try:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        if row["count"] > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        sample_expenses = [
            (user_id, 42.50, "Food", _day_in_current_month(2), "Groceries"),
            (user_id, 18.00, "Transport", _day_in_current_month(4), "Bus pass top-up"),
            (user_id, 120.00, "Bills", _day_in_current_month(6), "Electricity bill"),
            (user_id, 65.75, "Health", _day_in_current_month(9), "Pharmacy"),
            (user_id, 30.00, "Entertainment", _day_in_current_month(12), "Movie night"),
            (user_id, 89.99, "Shopping", _day_in_current_month(15), "New shoes"),
            (user_id, 15.25, "Other", _day_in_current_month(18), "Miscellaneous"),
            (user_id, 22.40, "Food", _day_in_current_month(21), "Lunch with friends"),
        ]
        conn.executemany(
            """INSERT INTO expenses (user_id, amount, category, date, description)
               VALUES (?, ?, ?, ?, ?)""",
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()

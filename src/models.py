"""
models.py — Initializes the SQLite database with all required tables.
Run: python src/models.py
"""

import sqlite3
import os

DB_PATH = "db/expenses.db"


def init_db(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    cur = con.cursor()

    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS categories (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name   TEXT UNIQUE NOT NULL,
            parent TEXT
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_date     TEXT NOT NULL,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            currency    TEXT DEFAULT 'INR',
            account     TEXT,
            category_id INTEGER,
            note        TEXT,
            raw_source  TEXT,
            UNIQUE(tx_date, description, amount, account),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            month          TEXT NOT NULL,
            category_name  TEXT NOT NULL,
            limit_amount   REAL NOT NULL,
            UNIQUE(month, category_name)
        );
    """)

    # Insert default categories
    default_categories = [
        ("Food & Dining", "Living"),
        ("Groceries", "Living"),
        ("Transport", "Living"),
        ("Bills & Utilities", "Living"),
        ("Shopping", "Discretionary"),
        ("Entertainment", "Discretionary"),
        ("Health & Fitness", "Essential"),
        ("Education", "Investment"),
        ("Income", None),
        ("Uncategorized", None),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO categories (name, parent) VALUES (?, ?)",
        default_categories,
    )

    # Insert sample budgets for current month
    sample_budgets = [
        ("2025-11", "Food & Dining", 8500),
        ("2025-11", "Groceries", 9000),
        ("2025-11", "Transport", 6000),
        ("2025-11", "Bills & Utilities", 8000),
        ("2025-11", "Shopping", 5000),
        ("2025-11", "Entertainment", 5000),
        ("2025-11", "Health & Fitness", 3000),
        ("2025-11", "Education", 4000),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO budgets (month, category_name, limit_amount) VALUES (?, ?, ?)",
        sample_budgets,
    )

    con.commit()
    con.close()
    print(f"✅ Database initialized at {path}")


if __name__ == "__main__":
    init_db()

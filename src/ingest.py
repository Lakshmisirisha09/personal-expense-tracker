"""
ingest.py — Loads CSV files into the SQLite database.
Handles any CSV with configurable column names.
Run: python src/ingest.py
"""

import pandas as pd
import sqlite3
import os

DB_PATH = "db/expenses.db"


def read_expense_csv(
    path,
    date_col="Date",
    desc_col="Description",
    amt_col="Amount",
    account_col="Account",
    note_col="Note",
):
    """
    Reads a CSV and normalizes columns to our standard schema.
    Works with bank exports too — just pass the right column names.
    """
    df = pd.read_csv(path)
    out = pd.DataFrame()
    out["tx_date"]     = pd.to_datetime(df[date_col], errors="coerce").dt.date.astype(str)
    out["description"] = df[desc_col].astype(str).str.strip()
    out["amount"]      = pd.to_numeric(df[amt_col], errors="coerce")
    out["account"]     = df[account_col].astype(str) if account_col in df.columns else "Unknown"
    out["note"]        = df[note_col].astype(str) if note_col in df.columns else ""
    out["raw_source"]  = path
    out = out.dropna(subset=["amount", "tx_date"])
    print(f"📂 Loaded {len(out)} rows from {path}")
    return out


def upsert_transactions(df, db_path=DB_PATH):
    """Inserts rows into the DB — silently skips exact duplicates."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    inserted = 0
    skipped = 0

    for row in df.itertuples(index=False):
        try:
            cur.execute(
                """INSERT INTO transactions
                   (tx_date, description, amount, account, note, raw_source)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (row.tx_date, row.description, row.amount,
                 row.account, row.note, row.raw_source),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    con.commit()
    con.close()
    print(f"✅ Inserted {inserted} rows  |  ⏭ Skipped {skipped} duplicates")


def run(csv_path="data/expenses.csv"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}. Run data/generate.py first.")
    df = read_expense_csv(csv_path)
    upsert_transactions(df)


if __name__ == "__main__":
    run()

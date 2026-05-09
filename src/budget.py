"""
budget.py — Set monthly category budgets and check for overspend.
Run: python src/budget.py
"""

import sqlite3
import pandas as pd

DB_PATH = "db/expenses.db"


def set_budget(month: str, category: str, limit: float, db_path=DB_PATH):
    """
    Set/update a budget limit.
    month format: 'YYYY-MM'  e.g. '2025-11'
    """
    con = sqlite3.connect(db_path)
    con.execute(
        """INSERT INTO budgets (month, category_name, limit_amount)
           VALUES (?, ?, ?)
           ON CONFLICT(month, category_name) DO UPDATE SET limit_amount=excluded.limit_amount""",
        (month, category, float(limit)),
    )
    con.commit()
    con.close()
    print(f"✅ Budget set: {category} = ₹{limit:,.0f} for {month}")


def check_budget(month: str, db_path=DB_PATH) -> pd.DataFrame:
    """Returns a dataframe comparing budget vs actual spend per category."""
    con = sqlite3.connect(db_path)

    actual = pd.read_sql_query(
        """
        SELECT c.name AS category, -SUM(t.amount) AS spent
        FROM transactions t
        JOIN categories c ON c.id = t.category_id
        WHERE t.amount < 0
          AND strftime('%Y-%m', t.tx_date) = ?
        GROUP BY c.name
        """,
        con,
        params=[month],
    )

    budgets = pd.read_sql_query(
        "SELECT category_name AS category, limit_amount AS budget FROM budgets WHERE month = ?",
        con,
        params=[month],
    )
    con.close()

    merged = budgets.merge(actual, on="category", how="left").fillna({"spent": 0})
    merged["used_%"]    = (merged["spent"] / merged["budget"] * 100).round(1)
    merged["remaining"] = (merged["budget"] - merged["spent"]).round(2)
    merged["status"]    = merged.apply(
        lambda r: "🔴 Over" if r["spent"] > r["budget"]
        else ("🟡 Warning" if r["used_%"] > 80 else "✅ OK"), axis=1
    )
    return merged.sort_values("used_%", ascending=False).reset_index(drop=True)


def print_budget_report(month: str):
    df = check_budget(month)
    print(f"\n{'='*60}")
    print(f"  BUDGET REPORT — {month}")
    print(f"{'='*60}")
    print(f"{'Category':<22} {'Budget':>8} {'Spent':>8} {'Used%':>6} {'Status'}")
    print("-" * 60)
    for _, r in df.iterrows():
        print(f"{r['category']:<22} ₹{r['budget']:>7,.0f} ₹{r['spent']:>7,.0f}"
              f" {r['used_%']:>5.1f}% {r['status']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Example: update budget and print report
    print_budget_report("2025-11")

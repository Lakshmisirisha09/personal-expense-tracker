"""
analyze.py — Core analysis functions: KPIs, monthly trends, category splits.
Imported by main.py and app_streamlit.py
"""

import sqlite3
import pandas as pd

DB_PATH = "db/expenses.db"


def fetch_frame(db_path=DB_PATH) -> pd.DataFrame:
    """Loads all transactions joined with category names."""
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT t.tx_date,
               t.description,
               t.amount,
               t.account,
               t.note,
               COALESCE(c.name, 'Uncategorized') AS category
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
        ORDER BY t.tx_date DESC
        """,
        con,
        parse_dates=["tx_date"],
    )
    con.close()
    df["month"] = df["tx_date"].dt.to_period("M").astype(str)
    df["week"]  = df["tx_date"].dt.isocalendar().week.astype(str)
    return df


def kpis(df: pd.DataFrame) -> dict:
    """Calculates top-level KPIs from a filtered dataframe."""
    expenses = df[df["amount"] < 0]
    income   = df[df["amount"] > 0]

    total_spend = -expenses["amount"].sum()
    total_income = income["amount"].sum()
    savings = total_income - total_spend
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    # Daily spend (unique dates with expenses)
    days = expenses["tx_date"].nunique()
    avg_daily = total_spend / days if days > 0 else 0

    top_categories = (
        -expenses.groupby("category")["amount"].sum()
        .sort_values(ascending=False)
        .head(6)
    )

    monthly_trend = (
        -expenses.groupby("month")["amount"].sum()
        .sort_index()
    )

    payment_split = (
        -expenses.groupby("account")["amount"].sum()
        .sort_values(ascending=False)
    )

    return {
        "total_spend":    round(total_spend, 2),
        "total_income":   round(total_income, 2),
        "savings":        round(savings, 2),
        "savings_rate":   round(savings_rate, 1),
        "avg_daily":      round(avg_daily, 2),
        "n_transactions": len(df),
        "top_categories": top_categories,
        "monthly_trend":  monthly_trend,
        "payment_split":  payment_split,
    }


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns month-by-month income, spend, and savings."""
    expenses = -df[df["amount"] < 0].groupby("month")["amount"].sum()
    income   =  df[df["amount"] > 0].groupby("month")["amount"].sum()
    summary  = pd.DataFrame({"Income": income, "Expenses": expenses}).fillna(0)
    summary["Savings"] = summary["Income"] - summary["Expenses"]
    summary["Savings %"] = (summary["Savings"] / summary["Income"] * 100).round(1)
    return summary.sort_index()


def top_merchants(df: pd.DataFrame, n=10) -> pd.DataFrame:
    """Returns top N merchants by total spend."""
    expenses = df[df["amount"] < 0].copy()
    return (
        -expenses.groupby("description")["amount"].sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
        .rename(columns={"description": "Merchant", "amount": "Total Spent (₹)"})
    )


def print_summary(df: pd.DataFrame):
    """Prints a readable analysis to the terminal."""
    k = kpis(df)
    months = df["month"].nunique()

    print("\n" + "=" * 50)
    print("  PERSONAL EXPENSE TRACKER — ANALYSIS REPORT")
    print("=" * 50)
    print(f"\n📅 Months analysed  : {months}")
    print(f"📊 Total transactions: {k['n_transactions']}")
    print(f"💰 Total Income      : ₹{k['total_income']:,.2f}")
    print(f"💸 Total Spend       : ₹{k['total_spend']:,.2f}")
    print(f"🏦 Net Savings       : ₹{k['savings']:,.2f}")
    print(f"📈 Savings Rate      : {k['savings_rate']}%")
    print(f"📆 Avg Daily Spend   : ₹{k['avg_daily']:,.2f}")

    print("\n--- Top Spending Categories ---")
    for cat, amt in k["top_categories"].items():
        bar = "█" * int(amt / k["top_categories"].max() * 20)
        print(f"  {cat:<22} ₹{amt:>8,.0f}  {bar}")

    print("\n--- Monthly Trend ---")
    for month, amt in k["monthly_trend"].items():
        bar = "█" * int(amt / k["monthly_trend"].max() * 20)
        print(f"  {month}  ₹{amt:>8,.0f}  {bar}")

    print("\n--- Payment Methods ---")
    for acc, amt in k["payment_split"].items():
        print(f"  {acc:<25} ₹{amt:>8,.0f}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    df = fetch_frame()
    print_summary(df)

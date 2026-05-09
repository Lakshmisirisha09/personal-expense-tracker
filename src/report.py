"""
report.py — Exports a monthly Excel report with multiple sheets.
Run: python src/report.py
Report saved to reports/ folder.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH   = "db/expenses.db"
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def export_monthly_report(month: str, db_path=DB_PATH) -> str:
    """
    Generates a multi-sheet Excel report for the given month.
    month: 'YYYY-MM' e.g. '2025-11'
    Returns path to saved file.
    """
    con = sqlite3.connect(db_path)

    # Sheet 1: All transactions for the month
    transactions = pd.read_sql_query(
        """
        SELECT t.tx_date AS Date,
               t.description AS Description,
               c.name AS Category,
               t.account AS Account,
               t.amount AS Amount,
               t.note AS Note
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
        WHERE strftime('%Y-%m', t.tx_date) = ?
        ORDER BY t.tx_date
        """,
        con, params=[month],
    )

    # Sheet 2: Category summary
    cat_summary = pd.read_sql_query(
        """
        SELECT c.name AS Category,
               COUNT(*) AS Transactions,
               -SUM(t.amount) AS Total_Spent
        FROM transactions t
        JOIN categories c ON c.id = t.category_id
        WHERE t.amount < 0
          AND strftime('%Y-%m', t.tx_date) = ?
        GROUP BY c.name
        ORDER BY Total_Spent DESC
        """,
        con, params=[month],
    )

    # Sheet 3: Budget vs actual
    budget_check = pd.read_sql_query(
        """
        SELECT b.category_name AS Category,
               b.limit_amount AS Budget,
               COALESCE(-SUM(t.amount), 0) AS Spent
        FROM budgets b
        LEFT JOIN categories c ON c.name = b.category_name
        LEFT JOIN transactions t ON t.category_id = c.id
            AND strftime('%Y-%m', t.tx_date) = b.month
            AND t.amount < 0
        WHERE b.month = ?
        GROUP BY b.category_name
        ORDER BY Spent DESC
        """,
        con, params=[month],
    )
    budget_check["Remaining"] = budget_check["Budget"] - budget_check["Spent"]
    budget_check["Used_%"]    = (budget_check["Spent"] / budget_check["Budget"] * 100).round(1)

    # Sheet 4: Monthly overview
    overview = pd.read_sql_query(
        """
        SELECT strftime('%Y-%m', tx_date) AS Month,
               SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS Income,
               -SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS Expenses
        FROM transactions
        GROUP BY Month ORDER BY Month
        """,
        con,
    )
    overview["Savings"]    = overview["Income"] - overview["Expenses"]
    overview["Savings_%"]  = (overview["Savings"] / overview["Income"] * 100).round(1)
    con.close()

    path = os.path.join(REPORT_DIR, f"expense_report_{month}.xlsx")

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        wb = writer.book

        # Formats
        header_fmt = wb.add_format({
            "bold": True, "bg_color": "#378ADD", "font_color": "white",
            "border": 1, "align": "center"
        })
        money_fmt  = wb.add_format({"num_format": "₹#,##0.00", "border": 1})
        pct_fmt    = wb.add_format({"num_format": "0.0%", "border": 1})
        cell_fmt   = wb.add_format({"border": 1})
        red_fmt    = wb.add_format({"bg_color": "#FFCCCC", "border": 1, "num_format": "₹#,##0.00"})
        green_fmt  = wb.add_format({"bg_color": "#CCFFCC", "border": 1, "num_format": "₹#,##0.00"})

        def write_sheet(df, sheet_name, col_widths=None):
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
            ws = writer.sheets[sheet_name]
            for col_num, col_name in enumerate(df.columns):
                ws.write(0, col_num, col_name, header_fmt)
            if col_widths:
                for i, w in enumerate(col_widths):
                    ws.set_column(i, i, w)
            return ws

        write_sheet(transactions, "Transactions",     [12, 30, 18, 20, 14, 20])
        write_sheet(cat_summary,  "Category Summary", [22, 15, 15])
        write_sheet(budget_check, "Budget Check",     [22, 14, 14, 14, 10])
        write_sheet(overview,     "Monthly Overview", [12, 14, 14, 14, 12])

    print(f"✅ Report saved: {path}")
    return path


def export_summary_txt(month: str, db_path=DB_PATH) -> str:
    """Also saves a plain text summary."""
    con = sqlite3.connect(db_path)
    income  = con.execute(
        "SELECT SUM(amount) FROM transactions WHERE amount > 0 AND strftime('%Y-%m', tx_date) = ?",
        [month]).fetchone()[0] or 0
    spend   = -con.execute(
        "SELECT SUM(amount) FROM transactions WHERE amount < 0 AND strftime('%Y-%m', tx_date) = ?",
        [month]).fetchone()[0] or 0
    con.close()

    txt = f"""
===================================================
  PERSONAL EXPENSE TRACKER — MONTHLY SUMMARY
  Period: {month}
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
===================================================
  Total Income   : ₹{income:>12,.2f}
  Total Expenses : ₹{spend:>12,.2f}
  Net Savings    : ₹{income-spend:>12,.2f}
  Savings Rate   : {(income-spend)/income*100 if income else 0:.1f}%
===================================================
"""
    path = os.path.join(REPORT_DIR, f"summary_{month}.txt")
    with open(path, "w") as f:
        f.write(txt)
    print(f"✅ Summary saved: {path}")
    print(txt)
    return path


if __name__ == "__main__":
    month = "2025-11"
    export_monthly_report(month)
    export_summary_txt(month)

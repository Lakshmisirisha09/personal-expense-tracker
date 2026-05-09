"""
main.py — Master orchestrator. Runs the full pipeline end-to-end.

Usage:
    python main.py              # Full pipeline (generate → ingest → analyze → charts)
    python main.py --no-charts  # Skip charts (faster)
    python main.py --report     # Also export monthly Excel report
"""

import sys
import os

# Add src/ to path so all modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.models     import init_db
from src.analyze    import fetch_frame, print_summary
from src.budget     import print_budget_report


def main():
    show_charts = "--no-charts" not in sys.argv
    make_report = "--report" in sys.argv
    month       = "2025-11"

    print("\n" + "=" * 55)
    print("  💸 Personal Expense Tracker — Full Pipeline")
    print("=" * 55)

    # Step 1: Init DB
    print("\n[1/6] Initializing database...")
    init_db()

    # Step 2: Generate synthetic data if CSV doesn't exist
    print("\n[2/6] Generating synthetic expense data...")
    if not os.path.exists("data/expenses.csv"):
        from data.generate import generate_expenses
        generate_expenses()
    else:
        print("  ℹ️  data/expenses.csv already exists — skipping generation")
        print("     (Delete it to regenerate fresh data)")

    # Step 3: Ingest CSV into DB
    print("\n[3/6] Ingesting CSV into database...")
    from src.ingest import run as ingest_run
    ingest_run()

    # Step 4: Categorize transactions
    print("\n[4/6] Auto-categorizing transactions...")
    from src.categorize import run as categorize_run
    categorize_run()

    # Step 5: Print analysis
    print("\n[5/6] Running analysis...")
    df = fetch_frame()
    print_summary(df)
    print_budget_report(month)

    # Step 6: Generate charts
    if show_charts:
        print("\n[6/6] Generating charts...")
        from src.plots import run_all
        run_all(df)
    else:
        print("\n[6/6] Skipping charts (--no-charts flag set)")

    # Optional: Export report
    if make_report:
        print("\n📄 Exporting monthly report...")
        from src.report import export_monthly_report, export_summary_txt
        export_monthly_report(month)
        export_summary_txt(month)

    print("\n" + "=" * 55)
    print("  ✅ Pipeline complete!")
    print("=" * 55)
    print("\nNext steps:")
    print("  • View charts      → open outputs/ folder")
    print("  • Launch dashboard → streamlit run src/app_streamlit.py")
    print("  • Export report    → python main.py --report")
    print()


if __name__ == "__main__":
    main()

"""
categorize.py — Auto-assigns categories to transactions using keyword rules.
Run: python src/categorize.py
"""

import re
import sqlite3

DB_PATH = "db/expenses.db"

# Keyword rules: category → list of regex patterns (case-insensitive)
RULES = {
    "Food & Dining": [
        r"swiggy|zomato|dominos|pizza|mcdonald|burger|cafe|coffee|restaurant"
        r"|haldiram|subway|starbucks|biryani|dhaba|dine|canteen"
    ],
    "Groceries": [
        r"d-mart|dmart|reliance fresh|big bazaar|spencer|more super|nature.?s basket"
        r"|lulu|grocery|supermarket|vegetables|fruits|kirana"
    ],
    "Transport": [
        r"uber|ola|rapido|metro|irctc|redbus|makemytrip|petrol|diesel|fuel"
        r"|bus ticket|train|auto|cab|flight"
    ],
    "Bills & Utilities": [
        r"electricity|electric|tata power|bescom|bsnl|jio|airtel|vodafone|vi\b"
        r"|broadband|wifi|water board|dth|recharge|postpaid|bill payment"
    ],
    "Shopping": [
        r"amazon|flipkart|myntra|ajio|nykaa|meesho|snapdeal|h&m|zara|lifestyle"
        r"|shopping|online order|jabong|tatacliq"
    ],
    "Entertainment": [
        r"netflix|amazon prime|spotify|bookmyshow|pvr|inox|hotstar|sonyliv|zee5"
        r"|apple music|gaming|game|cinema|theatre"
    ],
    "Health & Fitness": [
        r"apollo|medplus|netmeds|1mg|pharmeasy|pharmacy|gym|cult.?fit"
        r"|doctor|clinic|hospital|lab test|health|medicine|diagnostic"
    ],
    "Education": [
        r"udemy|coursera|youtube premium|o.reilly|internshala|unacademy|byju"
        r"|course|tutorial|book|subscription|skillshare|linkedin learning"
    ],
    "Income": [
        r"salary|credit|payout|refund|reimbursement|cashback|reward"
    ],
}


def classify(description: str, amount: float) -> str:
    """Returns category name for a transaction."""
    # Positive amounts are income
    if amount > 0:
        return "Income"
    d = description.lower()
    for cat, patterns in RULES.items():
        if cat == "Income":
            continue
        if any(re.search(p, d) for p in patterns):
            return cat
    return "Uncategorized"


def run(db_path=DB_PATH):
    con = sqlite3.connect(db_path)

    # Get category name → id mapping
    cats = con.execute("SELECT id, name FROM categories").fetchall()
    name_to_id = {name: cid for cid, name in cats}

    # Get uncategorized transactions
    rows = con.execute(
        "SELECT id, description, amount FROM transactions WHERE category_id IS NULL"
    ).fetchall()

    updated = 0
    for tx_id, desc, amount in rows:
        cat_name = classify(desc, amount)
        cat_id = name_to_id.get(cat_name, name_to_id.get("Uncategorized"))
        con.execute(
            "UPDATE transactions SET category_id = ? WHERE id = ?", (cat_id, tx_id)
        )
        updated += 1

    con.commit()
    con.close()

    # Show summary
    con2 = sqlite3.connect(db_path)
    summary = con2.execute("""
        SELECT c.name, COUNT(*) as count
        FROM transactions t
        JOIN categories c ON c.id = t.category_id
        GROUP BY c.name ORDER BY count DESC
    """).fetchall()
    con2.close()

    print(f"✅ Categorized {updated} transactions\n")
    print(f"{'Category':<25} {'Count':>6}")
    print("-" * 33)
    for name, count in summary:
        print(f"{name:<25} {count:>6}")


if __name__ == "__main__":
    run()

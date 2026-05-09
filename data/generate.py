"""
generate.py — Creates a realistic synthetic expense dataset.
Run this first: python data/generate.py
"""

import pandas as pd
import numpy as np
import random
from datetime import date, timedelta

random.seed(42)
np.random.seed(42)

# Category → (min_amount, max_amount, sample_merchants)
CATEGORIES = {
    "Food & Dining": {
        "range": (80, 800),
        "merchants": ["Swiggy", "Zomato", "Dominos", "McDonald's", "Cafe Coffee Day",
                      "Haldiram's", "Pizza Hut", "Starbucks", "Local Restaurant", "Subway"],
    },
    "Groceries": {
        "range": (200, 2500),
        "merchants": ["D-Mart", "Reliance Fresh", "Big Bazaar", "Spencer's",
                      "More Supermarket", "Nature's Basket", "Lulu Hypermarket"],
    },
    "Transport": {
        "range": (40, 600),
        "merchants": ["Uber", "Ola", "Rapido", "Metro Card Recharge",
                      "IRCTC Ticket", "RedBus", "MakeMyTrip Flight", "Petrol Pump"],
    },
    "Bills & Utilities": {
        "range": (300, 4000),
        "merchants": ["Tata Power Bill", "BSNL Broadband", "Jio Recharge",
                      "Airtel Postpaid", "BESCOM Electricity", "Water Board", "DTH Recharge"],
    },
    "Shopping": {
        "range": (299, 5000),
        "merchants": ["Amazon", "Flipkart", "Myntra", "Ajio", "Nykaa",
                      "Meesho", "Snapdeal", "H&M", "Zara", "Lifestyle"],
    },
    "Entertainment": {
        "range": (99, 1500),
        "merchants": ["Netflix", "Amazon Prime", "Spotify", "BookMyShow",
                      "PVR Cinemas", "Hotstar", "SonyLiv", "ZEE5", "Apple Music"],
    },
    "Health & Fitness": {
        "range": (100, 3000),
        "merchants": ["Apollo Pharmacy", "Medplus", "Cult.fit Gym",
                      "Netmeds", "1mg", "Dr Consultation", "Lab Tests"],
    },
    "Education": {
        "range": (199, 5000),
        "merchants": ["Udemy Course", "Coursera", "YouTube Premium",
                      "O'Reilly Books", "Internshala", "Unacademy", "Byju's"],
    },
}

ACCOUNTS = ["HDFC Savings", "UPI-GPay", "UPI-PhonePe", "Cash", "ICICI Credit Card"]
ACCOUNT_WEIGHTS = [0.30, 0.30, 0.20, 0.10, 0.10]


def generate_expenses(n_months=11, base_spend=38000):
    rows = []
    start_date = date(2025, 1, 1)

    for month_offset in range(n_months):
        month_start = date(start_date.year, start_date.month + month_offset
                           if start_date.month + month_offset <= 12
                           else (start_date.month + month_offset) % 12,
                           1)

        # Salary credit on 1st of every month
        rows.append({
            "Date": month_start.isoformat(),
            "Description": "Salary Credit - Employer",
            "Category": "Income",
            "Amount": 65000,
            "Account": "HDFC Savings",
            "Note": "Monthly salary",
        })

        # Random number of transactions per month (20–30)
        n_tx = random.randint(20, 30)
        # Seasonal spending boost in Oct/Nov
        spend_multiplier = 1.15 if month_offset >= 9 else 1.0

        for _ in range(n_tx):
            cat_name = random.choice(list(CATEGORIES.keys()))
            cat = CATEGORIES[cat_name]
            lo, hi = cat["range"]
            merchant = random.choice(cat["merchants"])
            amount = round(random.uniform(lo, hi) * spend_multiplier, 2)
            tx_day = random.randint(1, 28)

            rows.append({
                "Date": month_start.replace(day=tx_day).isoformat(),
                "Description": merchant,
                "Category": cat_name,
                "Amount": -amount,
                "Account": random.choices(ACCOUNTS, ACCOUNT_WEIGHTS)[0],
                "Note": "",
            })

    df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
    df.to_csv("data/expenses.csv", index=False)
    print(f"✅ Generated {len(df)} transactions → data/expenses.csv")
    print(df.groupby("Category")["Amount"].agg(["count", "sum"]).rename(
        columns={"count": "Transactions", "sum": "Total (₹)"}))
    return df


if __name__ == "__main__":
    generate_expenses()

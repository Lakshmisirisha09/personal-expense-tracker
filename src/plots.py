"""
plots.py — Generates and saves all visualization charts.
Run: python src/plots.py
Charts saved to outputs/ folder.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

os.makedirs("outputs", exist_ok=True)

# ─── Style Setup ────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#FAFAF9",
    "axes.facecolor":    "#FAFAF9",
    "axes.grid":         True,
    "grid.color":        "#E5E5E0",
    "grid.linewidth":    0.6,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
})

PALETTE = ["#378ADD", "#E24B4A", "#EF9F27", "#1D9E75",
           "#534AB7", "#D4537E", "#5DCAA5", "#BA7517"]


# ─── 1. Category Bar Chart ───────────────────────────────────────
def plot_category_bar(df: pd.DataFrame, save=True):
    expenses = df[df["amount"] < 0].copy()
    cat_spend = (
        -expenses.groupby("category")["amount"].sum()
        .sort_values(ascending=True)
        .tail(8)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(cat_spend.index, cat_spend.values,
                   color=PALETTE[:len(cat_spend)], edgecolor="none", height=0.55)

    for bar, val in zip(bars, cat_spend.values):
        ax.text(val + 200, bar.get_y() + bar.get_height() / 2,
                f"₹{val:,.0f}", va="center", fontsize=10, color="#444")

    ax.set_xlabel("Total Spent (₹)")
    ax.set_title("Category-Wise Spending")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    plt.tight_layout()
    if save:
        path = "outputs/01_category_bar.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved {path}")
    plt.show()
    plt.close()


# ─── 2. Monthly Spending Line Chart ─────────────────────────────
def plot_monthly_trend(df: pd.DataFrame, save=True):
    expenses = df[df["amount"] < 0].copy()
    monthly  = -expenses.groupby("month")["amount"].sum().sort_index()
    income   =  df[df["amount"] > 0].groupby("month")["amount"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly.index, monthly.values, color="#E24B4A", marker="o",
            linewidth=2.5, markersize=6, label="Expenses")
    ax.plot(income.index, income.values, color="#1D9E75", marker="s",
            linewidth=2.5, markersize=6, linestyle="--", label="Income")
    ax.fill_between(monthly.index, monthly.values, alpha=0.08, color="#E24B4A")

    ax.set_title("Monthly Income vs Expenses Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))
    ax.legend()
    ax.set_xticklabels(monthly.index, rotation=45, ha="right")
    plt.tight_layout()
    if save:
        path = "outputs/02_monthly_trend.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved {path}")
    plt.show()
    plt.close()


# ─── 3. Payment Method Pie Chart ────────────────────────────────
def plot_payment_pie(df: pd.DataFrame, save=True):
    expenses = df[df["amount"] < 0].copy()
    pay_split = -expenses.groupby("account")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 6))
    wedges, texts, autotexts = ax.pie(
        pay_split.values,
        labels=pay_split.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=PALETTE[:len(pay_split)],
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
        pctdistance=0.75,
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_color("white")
        t.set_fontweight("bold")

    ax.set_title("Spending by Payment Method", pad=20)
    plt.tight_layout()
    if save:
        path = "outputs/03_payment_pie.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved {path}")
    plt.show()
    plt.close()


# ─── 4. Daily Spending Trend ─────────────────────────────────────
def plot_daily_trend(df: pd.DataFrame, month=None, save=True):
    expenses = df[df["amount"] < 0].copy()
    if month:
        expenses = expenses[expenses["month"] == month]
    daily = -expenses.groupby("tx_date")["amount"].sum()

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(range(len(daily)), daily.values, color="#378ADD", alpha=0.7, edgecolor="none")
    ax.axhline(daily.mean(), color="#E24B4A", linewidth=1.5,
               linestyle="--", label=f"Avg ₹{daily.mean():,.0f}")
    ax.set_title(f"Daily Spending Pattern{' — ' + month if month else ''}")
    ax.set_xlabel("Day")
    ax.set_ylabel("Amount (₹)")
    ax.legend()
    ax.set_xticks([])
    plt.tight_layout()
    if save:
        path = "outputs/04_daily_trend.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved {path}")
    plt.show()
    plt.close()


# ─── 5. Category Heatmap (month × category) ──────────────────────
def plot_heatmap(df: pd.DataFrame, save=True):
    expenses = df[df["amount"] < 0].copy()
    pivot = (-expenses.groupby(["month", "category"])["amount"]
             .sum()
             .unstack(fill_value=0))
    pivot = pivot[[c for c in pivot.columns if c != "Income"]]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        pivot / 1000,
        ax=ax,
        cmap="YlOrRd",
        linewidths=0.4,
        linecolor="#eee",
        annot=True,
        fmt=".1f",
        cbar_kws={"label": "₹ (thousands)"},
    )
    ax.set_title("Spending Heatmap — Month × Category (₹ thousands)")
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    if save:
        path = "outputs/05_heatmap.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved {path}")
    plt.show()
    plt.close()


def run_all(df: pd.DataFrame):
    print("\n🎨 Generating all charts...\n")
    plot_category_bar(df)
    plot_monthly_trend(df)
    plot_payment_pie(df)
    plot_daily_trend(df, month="2025-11")
    plot_heatmap(df)
    print("\n✅ All charts saved to outputs/")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from analyze import fetch_frame
    df = fetch_frame()
    run_all(df)

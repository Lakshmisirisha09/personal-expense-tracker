"""
app_streamlit.py — Interactive Streamlit Dashboard
Run: streamlit run src/app_streamlit.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analyze import fetch_frame, kpis, monthly_summary, top_merchants
from budget import check_budget, set_budget
from ingest import read_expense_csv, upsert_transactions
from report import export_monthly_report

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💸",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #F8F8F6;
        border: 1px solid #E5E5E0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.5rem;
    }
    .insight { 
        background: #EAF3DE; 
        border-left: 4px solid #639922;
        padding: 0.6rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .alert {
        background: #FCEBEB;
        border-left: 4px solid #E24B4A;
        padding: 0.6rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────
st.title("💸 Personal Expense Tracker")
st.caption("Track • Analyze • Optimize your finances")
st.divider()

# ─── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    # CSV upload
    st.subheader("📂 Upload CSV")
    uploaded = st.file_uploader("Bank export / custom CSV", type=["csv"])
    if uploaded:
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            df_up = read_expense_csv(tmp_path)
            upsert_transactions(df_up)
            st.success(f"✅ Loaded {len(df_up)} rows")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    # Load data
    df_all = fetch_frame()

    # Month filter
    months = sorted(df_all["month"].unique())
    selected_month = st.selectbox("📅 Month", options=months[::-1])

    # Account filter
    accounts = sorted(df_all["account"].unique())
    selected_accounts = st.multiselect("🏦 Accounts", accounts, default=accounts)

    st.divider()
    st.subheader("💰 Set Budget")
    b_cat   = st.selectbox("Category", [
        "Food & Dining", "Groceries", "Transport", "Bills & Utilities",
        "Shopping", "Entertainment", "Health & Fitness", "Education"
    ])
    b_limit = st.number_input("Limit (₹)", min_value=100, max_value=100000,
                               value=5000, step=500)
    if st.button("Save Budget"):
        set_budget(selected_month, b_cat, b_limit)
        st.success(f"Budget saved for {b_cat}")

    st.divider()
    if st.button("📄 Export Monthly Report"):
        path = export_monthly_report(selected_month)
        st.success(f"Saved: {path}")

# ─── Filter Data ────────────────────────────────────────────────
df = df_all[
    (df_all["month"] == selected_month) &
    (df_all["account"].isin(selected_accounts))
]
k = kpis(df)

# ─── KPI Metrics ────────────────────────────────────────────────
st.subheader(f"📊 Summary — {selected_month}")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Spend",    f"₹{k['total_spend']:,.0f}")
c2.metric("Income",         f"₹{k['total_income']:,.0f}")
c3.metric("Savings",        f"₹{k['savings']:,.0f}")
c4.metric("Savings Rate",   f"{k['savings_rate']}%",
          delta="Good" if k['savings_rate'] >= 20 else "Low")
c5.metric("Avg Daily Spend",f"₹{k['avg_daily']:,.0f}")
st.divider()

# ─── Charts Row 1 ───────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📊 Category Spending")
    cat_df = k["top_categories"].reset_index()
    cat_df.columns = ["Category", "Amount"]
    fig_bar = px.bar(
        cat_df.sort_values("Amount"),
        x="Amount", y="Category", orientation="h",
        color="Amount", color_continuous_scale="Blues",
        labels={"Amount": "₹ Spent"},
    )
    fig_bar.update_layout(showlegend=False, coloraxis_showscale=False,
                          plot_bgcolor="#FAFAF9", paper_bgcolor="#FAFAF9",
                          height=350, margin=dict(l=0, r=0, t=0, b=0))
    fig_bar.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("💳 Payment Methods")
    pay_df = k["payment_split"].reset_index()
    pay_df.columns = ["Account", "Amount"]
    fig_pie = px.pie(pay_df, values="Amount", names="Account",
                     hole=0.5, color_discrete_sequence=px.colors.qualitative.Set2)
    fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0),
                          paper_bgcolor="#FAFAF9")
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── Monthly Trend ──────────────────────────────────────────────
st.subheader("📈 Monthly Trend")
ms = monthly_summary(df_all).reset_index()
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=ms["month"], y=ms["Income"],
                              name="Income", line=dict(color="#1D9E75", width=2.5),
                              mode="lines+markers"))
fig_line.add_trace(go.Scatter(x=ms["month"], y=ms["Expenses"],
                              name="Expenses", line=dict(color="#E24B4A", width=2.5),
                              mode="lines+markers", fill="tozeroy",
                              fillcolor="rgba(226,75,74,0.08)"))
fig_line.update_layout(plot_bgcolor="#FAFAF9", paper_bgcolor="#FAFAF9",
                       height=300, margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="", yaxis_tickprefix="₹")
st.plotly_chart(fig_line, use_container_width=True)

# ─── Budget Check ───────────────────────────────────────────────
st.subheader("🎯 Budget vs Actual")
budget_df = check_budget(selected_month)
if not budget_df.empty:
    st.dataframe(
        budget_df.style
            .applymap(lambda v: "background-color: #FFCCCC" if "Over" in str(v) else
                                "background-color: #CCFFCC" if "OK" in str(v) else "",
                      subset=["status"])
            .format({"budget": "₹{:,.0f}", "spent": "₹{:,.0f}",
                     "remaining": "₹{:,.0f}", "used_%": "{:.1f}%"}),
        use_container_width=True,
    )
else:
    st.info("No budgets set for this month. Use the sidebar to add budgets.")

# ─── Top Merchants ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏪 Top Merchants")
    merchants_df = top_merchants(df)
    st.dataframe(merchants_df, use_container_width=True, height=300)

with col2:
    st.subheader("📋 Recent Transactions")
    recent = df[df["amount"] < 0].head(15)[
        ["tx_date", "description", "category", "account", "amount"]
    ].copy()
    recent["amount"] = recent["amount"].apply(lambda x: f"₹{abs(x):,.0f}")
    st.dataframe(recent, use_container_width=True, height=300)

# ─── Insights ───────────────────────────────────────────────────
st.subheader("💡 Smart Insights")
cat_series = k["top_categories"]
if not cat_series.empty:
    top_cat = cat_series.index[0]
    top_amt = cat_series.iloc[0]
    pct = (top_amt / k["total_spend"] * 100) if k["total_spend"] > 0 else 0

    st.markdown(f"""
    <div class="insight">
        📊 <b>{top_cat}</b> is your top spending category at <b>₹{top_amt:,.0f}</b> ({pct:.0f}% of total spend).
    </div>
    <div class="{'insight' if k['savings_rate'] >= 20 else 'alert'}">
        {'✅' if k['savings_rate'] >= 20 else '⚠️'} Your savings rate is <b>{k['savings_rate']}%</b>.
        {'Great job! Above the 20% benchmark.' if k['savings_rate'] >= 20 else 'Try to reach 20% savings rate.'}
    </div>
    <div class="insight">
        📆 You spent an average of <b>₹{k['avg_daily']:,.0f}/day</b> this month 
        across <b>{k['n_transactions']}</b> transactions.
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("Personal Expense Tracker · Built with Python, Pandas, SQLite & Streamlit")

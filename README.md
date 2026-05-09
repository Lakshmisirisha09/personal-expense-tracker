# 💸 Personal Expense Tracker with Data Visualization

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-orange)](https://pandas.pydata.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)](https://sqlite.org)

A full Python project that ingests transaction data, auto-categorizes it, stores it in SQLite, and visualizes spending patterns through charts and an interactive Streamlit dashboard.

---

## 🎯 Problem Statement

Most people have no clear picture of where their money goes each month. This tracker solves that by:
- Auto-categorizing transactions using keyword rules
- Showing monthly trends, category breakdowns, and payment method splits
- Alerting when spending exceeds your budget limits
- Exporting monthly Excel reports for record-keeping

---

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| Pandas | Data loading, cleaning, aggregation |
| SQLite | Persistent transaction storage |
| Matplotlib / Seaborn | Static charts |
| Plotly | Interactive charts in Streamlit |
| Streamlit | Interactive dashboard UI |
| XlsxWriter | Excel report export |

---

## 📂 Folder Structure

```
personal-expense-tracker/
│
├── data/
│   ├── generate.py        ← Creates synthetic expense CSV
│   └── expenses.csv       ← Generated after running generate.py
│
├── db/
│   └── expenses.db        ← SQLite database (auto-created)
│
├── src/
│   ├── models.py          ← DB schema initialization
│   ├── ingest.py          ← CSV → SQLite loader
│   ├── categorize.py      ← Keyword-based auto-tagger
│   ├── analyze.py         ← KPIs, trends, aggregations
│   ├── budget.py          ← Budget CRUD and alerts
│   ├── plots.py           ← Matplotlib/Seaborn charts
│   ├── report.py          ← Excel/text report export
│   └── app_streamlit.py   ← Streamlit dashboard
│
├── outputs/               ← Saved chart images (.png)
├── reports/               ← Monthly Excel reports
├── images/                ← Screenshots for README
├── docs/                  ← Additional documentation
│
├── main.py                ← Full pipeline runner
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/personal-expense-tracker.git
cd personal-expense-tracker
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the full pipeline
```bash
python main.py
```
This will: generate data → init DB → ingest → categorize → analyze → save charts.

### 5. Launch the Streamlit dashboard
```bash
streamlit run src/app_streamlit.py
```
Open your browser at **http://localhost:8501**

### 6. Export monthly report
```bash
python main.py --report
```

---

## 📊 Sample Outputs

### Category Spending Bar Chart
![Category Chart](images/01_category_bar.png)

### Monthly Trend Line Chart
![Monthly Trend](images/02_monthly_trend.png)

### Payment Method Pie Chart
![Payment Pie](images/03_payment_pie.png)

### Streamlit Dashboard
![Dashboard](images/dashboard.png)

---

## ✨ Features

- ✅ Synthetic 200+ transaction dataset (no real bank access needed)
- ✅ Auto-categorization using regex keyword rules
- ✅ SQLite storage with deduplication
- ✅ Monthly KPIs: income, spend, savings rate, avg daily spend
- ✅ 5 chart types: bar, line, pie, daily trend, heatmap
- ✅ Interactive Streamlit dashboard with filters
- ✅ Budget setting and overspend alerts
- ✅ Excel + text report export
- ✅ CSV upload for real bank data

---

## 📚 Learning Outcomes

- Python data pipeline design
- Pandas for cleaning, groupby, pivoting
- SQLite with foreign keys and upsert patterns
- Matplotlib/Seaborn/Plotly visualization
- Streamlit for data apps
- Modular, beginner-friendly code structure

---

## 🔭 Roadmap

- [ ] OCR receipt scanner (Tesseract)
- [ ] Email/SMS budget alerts (Twilio/SMTP)
- [ ] ML-based auto-categorization (Naive Bayes)
- [ ] Multi-currency support with FX rates
- [ ] Recurring transaction detection

---

## 👤 Author

Lakshmi Sirisha 
[GitHub](https://github.com/Lakshmisirisha09) · [LinkedIn](www.linkedin.com/in/lakshmisirisha-kuppala-a7524931a)

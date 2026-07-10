# 📊 Business Intelligence & Sales Analytics Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?style=flat-square&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat-square&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Visualizations-3F4F75?style=flat-square&logo=plotly)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQL_Analytics-336791?style=flat-square&logo=postgresql)

**[🚀 Live Demo](#)** · **[GitHub](https://github.com/chahatthakur24/bi-sales-analytics-platform)**

*Built by [Chahat Thakur](https://www.linkedin.com/in/chahat-thakur-0a36b5334/)*

</div>

---

## 📌 Project Overview

An end-to-end Business Intelligence platform analyzing **5,000+ sales orders** across **799 customers**, **3 years**, and **5 regions**. Covers the full analytics stack — from raw data exploration to RFM customer segmentation, cohort retention analysis, time series forecasting, and an interactive 5-page Streamlit dashboard.

---

## 🎯 Key Results

| Metric | Value |
|---|---|
| Total Revenue Analyzed | ₹19M+ |
| Customers Segmented | 799 |
| RFM Segments | 8 |
| Forecast Accuracy | 83.8% |
| SQL Queries | 20 |
| Dashboard Pages | 5 |

---

## 🚀 Live Demo

**https://bi-sales-analytics-platform-hz929ans7e4oe86hfjmwpg.streamlit.app/(#)** ← Add your Streamlit Cloud URL here after deployment

**5 Dashboard Pages:**
- 🏠 **Executive Summary** — KPIs, revenue trend, region breakdown
- 📈 **Sales Performance** — Category, sub-category, discount impact
- 👥 **Customer Analytics** — RFM segmentation, cohort retention, CLV
- 📦 **Product Intelligence** — Top products, margin heatmap, return rates
- 🔮 **Revenue Forecast** — Holt-Winters 6-month forecast with confidence intervals

---

## 🗂️ Project Structure

```
bi-sales-analytics-platform/
│
├── 📁 data/
│   ├── generate_data.py          # Synthetic dataset generator (5,000 orders)
│   ├── superstore.csv            # Generated sales dataset
│   ├── rfm_scores.csv            # RFM scores per customer
│   ├── customers_enriched.csv    # Customer CLV and enriched data
│   └── revenue_forecast.csv      # 6-month revenue forecast
│
├── 📁 notebooks/
│   ├── 01_EDA.py                 # Exploratory data analysis (7 charts)
│   ├── 02_customer_analytics.py  # RFM segmentation + cohort analysis
│   └── 03_forecasting.py         # Holt-Winters forecasting + decomposition
│
├── 📁 sql/
│   └── analytics_queries.sql     # 20 PostgreSQL analytical queries
│
├── 📁 streamlit_app/
│   └── app.py                    # 5-page Streamlit dashboard
│
├── 📁 models/
│   └── holt_winters_model.pkl    # Trained forecasting model
│
├── 📁 reports/                   # Generated charts (PNG)
├── 📁 .streamlit/
│   └── config.toml               # Dashboard theme config
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/chahatthakur24/bi-sales-analytics-platform.git
cd bi-sales-analytics-platform
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate       # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the pipeline
```bash
# Generate synthetic dataset
python data/generate_data.py

# Run in order
python notebooks/01_EDA.py
python notebooks/02_customer_analytics.py
python notebooks/03_forecasting.py
```

### 5. Launch the dashboard
```bash
streamlit run streamlit_app/app.py
```

---

## 🧠 Analytics Components

### RFM Segmentation
Customers scored on Recency, Frequency, and Monetary value (1–5 each) and classified into 8 segments: Champions, Loyal Customers, Potential Loyalists, New Customers, At Risk, Can't Lose Them, Hibernating, Lost.

### Cohort Analysis
Month-over-month retention heatmap tracking what percentage of each acquisition cohort is still active over time — the standard tool for measuring customer loyalty in e-commerce and fintech.

### Holt-Winters Forecasting
Triple exponential smoothing model capturing trend and seasonality components, with 90% confidence intervals on 6-month forward projections.

### Discount Impact Analysis
Quantifying the relationship between discount tiers and profit margins — showing at what discount level transactions become unprofitable.

---

## 📊 SQL Analytics (20 Queries)

| Category | Queries |
|---|---|
| Revenue & Profit | Annual YoY growth, monthly rolling average, quarterly cumulative, region ranking |
| Customer Analytics | RFM scoring, CLV, cohort retention, top customers, frequency distribution |
| Product & Discount | Discount impact, negative margin products, return rate analysis |
| Operations | Shipping performance, late shipment detection |
| Advanced | Pareto decile analysis, MoM growth, segment contribution, running totals, KPI summary |

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Forecasting | Statsmodels (Holt-Winters) |
| Dashboard | Streamlit |
| Database | PostgreSQL |
| DevOps | Git, GitHub, Streamlit Cloud |

---

## 👤 Author

**Chahat Thakur**
- GitHub: [@chahatthakur24](https://github.com/chahatthakur24)
- LinkedIn: [chahat-thakur](https://www.linkedin.com/in/chahat-thakur-0a36b5334/)
- Email: chahat2404@gmail.com

---

<div align="center">
⭐ If you found this project useful, please consider giving it a star!
</div>

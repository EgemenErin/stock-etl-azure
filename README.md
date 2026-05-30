# 📈 US Equity Volatility Monitor

> A fully automated ETL pipeline that pulls live stock data from Alpha Vantage, loads it into Azure SQL, and surfaces volatility analytics in a Power BI dashboard — **rebuilt daily via GitHub Actions**.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Azure SQL](https://img.shields.io/badge/Azure%20SQL-Database-0078D4?logo=microsoftazure&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)

---

<img width="1434" height="802" alt="image" src="https://github.com/user-attachments/assets/dbaf4789-92de-4c7a-b83c-c2e8ef4f8381" />


## 📌 Project Overview

This project tracks daily price movements and volatility risk across 5 US equities — **AAPL, GOOGL, JNJ, MSFT, NVDA** — using a production-style data pipeline:

```
Alpha Vantage API → Python ETL → Azure SQL Database → Power BI
```

The pipeline runs automatically on a schedule via **GitHub Actions**, keeping the dashboard current without any manual intervention. The result is a live volatility monitor that answers: *which tickers carry the most risk, and where is the money moving?*

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Alpha Vantage  │────▶│  Python ETL      │────▶│  Azure SQL DB   │────▶│   Power BI   │
│  Stock API      │     │  (src/etl.py)    │     │  (price data)   │     │  Dashboard   │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └──────────────┘
                                 ▲
                        ┌────────┴────────┐
                        │  GitHub Actions │
                        │  (scheduled)    │
                        └─────────────────┘
```

---

## 📊 Dashboard

![US Equity Volatility Monitor](docs/docs/dashboard.png)

The Power BI dashboard has three core views:

**Price Trends** — Daily close prices over time across all 5 tickers. NVDA leads growth since January; JNJ is the most stable; MSFT shows a consistent upward trend entering Q2.

**Volatility Analysis** — Daily return volatility by ticker and a 7-day rolling volatility risk score. NVDA carries ~3x the volatility of JNJ, confirming its high-risk, high-reward profile. Key insight: daily returns cluster near 0% for all tickers, with NVDA showing the widest spike range.

**Volume & Risk** — Total trading volume by ticker (NVDA dominates at 17bn) alongside interactive KPI cards showing total volume, avg 7D volatility, and avg close price filtered by date range and ticker.

---

## ⚙️ ETL Pipeline

### Extract
- Fetches daily OHLCV data for each ticker from the **Alpha Vantage API**
- Handles API rate limiting and response validation

### Transform
- Parses and normalizes JSON responses into a flat tabular structure using **Pandas**
- Computes **daily return** `(close - prev_close) / prev_close`
- Computes **7-day rolling volatility** as standard deviation of daily returns
- Deduplicates records to prevent double-loading on re-runs

### Load
- Connects to **Azure SQL** via `pyodbc` + `SQLAlchemy`
- Upserts transformed records into the `stock_prices` table
- Schema managed via SQL scripts in `/sql`

---

## 🗂️ Repository Structure

```
├── .github/
│   └── workflows/
│       └── etl.yml             # GitHub Actions scheduled pipeline
├── docs/
│   └── docs/                   # Dashboard screenshots
├── sql/                        # Table creation & schema scripts
├── src/                        # Python ETL source code
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Source | Alpha Vantage REST API |
| ETL | Python, Pandas, Requests |
| Database | Azure SQL (pyodbc, SQLAlchemy) |
| Orchestration | GitHub Actions (scheduled CRON) |
| Visualization | Power BI (DirectQuery / import) |
| Config | python-dotenv (env-based secrets) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Azure SQL Database instance
- Alpha Vantage API key (free tier works)
- Power BI Desktop

### Installation

```bash
git clone https://github.com/EgemenErin/stock-etl-azure.git
cd stock-etl-azure
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
ALPHA_VANTAGE_API_KEY=your_api_key
AZURE_SQL_SERVER=your_server.database.windows.net
AZURE_SQL_DATABASE=your_database
AZURE_SQL_USERNAME=your_username
AZURE_SQL_PASSWORD=your_password
```

### Run the pipeline manually

```bash
python src/etl.py
```

### GitHub Actions (Automated)

The pipeline is configured to run on a schedule. To enable it in your fork, add the environment variables above as **GitHub Secrets** under `Settings → Secrets and variables → Actions`.

---

## 📐 SQL Schema

```sql
CREATE TABLE stock_prices (
    id          INT IDENTITY PRIMARY KEY,
    ticker      VARCHAR(10)    NOT NULL,
    price_date  DATE           NOT NULL,
    open_price  DECIMAL(10,4),
    high_price  DECIMAL(10,4),
    low_price   DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume      BIGINT,
    daily_return    DECIMAL(10,6),
    volatility_7d   DECIMAL(10,6),
    loaded_at   DATETIME DEFAULT GETDATE(),
    UNIQUE (ticker, price_date)
);
```

---

## 🔗 Links

- 🌐 [Portfolio — egemenerin.com](https://www.egemenerin.com)
- 📊 [Live Power BI Dashboard](https://m365ht-my.sharepoint.com/:u:/r/personal/pzx114222_student_poznan_merito_pl/Documents/US%20Equity%20Volatility%20Monitor.pbix?csf=1&web=1&e=cYFvZu) 
- 📧 egemeneriin@protonmail.com

---

## 👤 Author

**Egemen Erin** — Data Analyst  
*2025*

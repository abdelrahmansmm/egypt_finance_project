# 🇪🇬 Egypt Finance — End-to-End Data Engineering Project

A production-grade data engineering pipeline that collects, stores, transforms, and orchestrates real Egyptian financial data using a modern open-source stack.

---

## 🏗️ Architecture

```
[Data Sources]
CBE / EGX / World Bank / IMF
        |
        v
[Ingestion Layer]
Python scripts (requests, yfinance, BeautifulSoup)
        |
        +--------> [MongoDB] (raw JSON documents)
        |
        v
[Staging Layer]
PostgreSQL (structured relational tables)
        |
        v
[Transformation Layer]
dbt (staging views + mart tables)
        |
        v
[Orchestration Layer]
Apache Airflow (scheduled DAGs)
        |
        v
[Infrastructure]
Docker (all services containerized)
```

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Data ingestion & scripting |
| PostgreSQL | 15 | Primary data warehouse |
| MongoDB | 6 | Raw document storage |
| dbt | 1.11 | Data transformation |
| Apache Airflow | 2.8 | Pipeline orchestration |
| Docker | Latest | Containerization |

---

## 📊 Data Sources

| Source | Data | Method |
|---|---|---|
| open.er-api.com | USD/EGP & major currency rates | Free REST API |
| Yahoo Finance (yfinance) | EGX-listed stock prices | Python library |
| World Bank API | Egypt GDP, inflation, unemployment | Free REST API |
| IMF DataMapper API | Egypt macro indicators | Free REST API |

---

## 📁 Project Structure

```
egypt_finance_project/
├── .env                        # Environment variables (not committed)
├── docker-compose.yml          # All services definition
├── requirements.txt            # Python dependencies
├── postgres/
│   └── init.sql                # Database schema
├── ingestion/
│   ├── cbe_rates.py            # Exchange rates ingestion
│   ├── egx_stocks.py           # EGX stock prices ingestion
│   └── world_bank.py           # World Bank indicators ingestion
├── mongodb/
│   └── store_raw.py            # Raw document storage + IMF ingestion
├── dbt_project/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/            # Cleaning & standardization views
│   │   └── marts/              # Business metric tables
└── airflow/
    └── dags/
        └── egypt_finance_pipeline.py  # Main orchestration DAG
```

---

## 🗄️ Database Schema

### Raw Tables (PostgreSQL)
| Table | Records | Description |
|---|---|---|
| cbe_exchange_rates | 30 | Daily currency rates vs EGP |
| egx_stocks | 1,690 | EGX stock OHLCV data (1 year) |
| worldbank_indicators | 2,265 | Egypt macro indicators (2000-2024) |
| imf_data | 227 | IMF Egypt economic indicators |

### dbt Models
| Model | Type | Description |
|---|---|---|
| stg_egx_stocks | View | Cleaned stock data + daily returns |
| stg_cbe_rates | View | Cleaned exchange rates + spread |
| stg_worldbank | View | Cleaned World Bank indicators |
| stg_imf_data | View | Cleaned IMF indicators |
| mart_daily_market_summary | Table | Daily EGX market sentiment |
| mart_stock_performance | Table | Stock performance metrics |
| mart_egypt_macro | Table | Combined macro indicators |

### MongoDB Collections
| Collection | Documents | Description |
|---|---|---|
| imf_raw | 5 | Raw IMF API responses |
| market_summary | 1 | Daily EGX market snapshot |

---

## 🚀 Getting Started

### Prerequisites
- Windows with WSL2 (Ubuntu)
- Docker Desktop
- Python 3.12+

### Setup

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/egypt_finance_project.git
cd egypt_finance_project
```

**2. Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Create `.env` file:**
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=egypt_finance
POSTGRES_USER=egfinanceuser
POSTGRES_PASSWORD=your_password

MONGO_URI=mongodb://localhost:27017/
MONGO_DB=egypt_finance_raw
```

**4. Start all services:**
```bash
docker compose up -d
sleep 15
sudo systemctl stop postgresql  # Stop system PostgreSQL if running
```

**5. Run ingestion scripts:**
```bash
python ingestion/world_bank.py
python ingestion/egx_stocks.py
python ingestion/cbe_rates.py
python mongodb/store_raw.py
```

**6. Run dbt transformations:**
```bash
cd dbt_project
dbt run
dbt test
```

**7. Access services:**
| Service | URL |
|---|---|
| Airflow UI | http://localhost:8080 |
| PostgreSQL | localhost:5432 |
| MongoDB | localhost:27017 |

---

## 🔄 Pipeline DAG

The Airflow DAG `egypt_finance_pipeline` runs every weekday at 8am:

```
ingest_worldbank  ┐
ingest_egx_stocks ├──► store_mongodb ──► dbt_staging ──► dbt_marts ──► dbt_tests
ingest_rates      ┘
```

---

## 📈 Sample Insights

```sql
-- Top performing EGX stocks
SELECT ticker, company_name, avg_daily_return_pct, volatility
FROM dbt_egypt_marts.mart_stock_performance
ORDER BY avg_daily_return_pct DESC;

-- Egypt macro trends
SELECT year, inflation_pct, gdp_growth_pct, usd_egp_rate
FROM dbt_egypt_marts.mart_egypt_macro
ORDER BY year DESC;

-- Daily market sentiment
SELECT trade_date, market_sentiment, avg_market_return_pct
FROM dbt_egypt_marts.mart_daily_market_summary
ORDER BY trade_date DESC
LIMIT 10;
```

---

## 👨‍💻 Author

Built as a hands-on data engineering learning project covering the full modern data stack.

---

## 📄 License

MIT License

import yfinance as yf
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

EGX_TICKERS = [
    'COMI.CA',   # Commercial International Bank
    'HRHO.CA',   # EFG Hermes
    'TMGH.CA',   # Talaat Moustafa Group
    'ETEL.CA',   # Telecom Egypt
    'SWDY.CA',   # El Sewedy Electric
    'OCDI.CA',   # Orascom Development
    'PHDC.CA',   # Palm Hills
    'ESRS.CA',
]

def fetch_egx_data(tickers, period='1y'):
    all_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                print(f'No data for {ticker}')
                continue
            df.reset_index(inplace=True)
            df['ticker'] = ticker
            df['company_name'] = stock.info.get('longName', ticker)
            all_data.append(df)
            print(f'Fetched {len(df)} records for {ticker}')
        except Exception as e:
            print(f'Error fetching {ticker}: {e}')
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def load_to_postgres(df):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    conn.autocommit = False
    cursor = conn.cursor()
    insert_sql = """
        INSERT INTO egx_stocks (ticker, company_name, open_price, close_price, high_price, low_price, volume, trade_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker, trade_date) DO NOTHING
    """
    count = 0
    skipped = 0
    for _, row in df.iterrows():
        try:
            cursor.execute(insert_sql, (
                row['ticker'],
                row.get('company_name', ''),
                float(row['Open']),
                float(row['Close']),
                float(row['High']),
                float(row['Low']),
                int(row['Volume']),
                row['Date'].date() if hasattr(row['Date'], 'date') else row['Date'] 
            ))
            count += 1
        except Exception as e:
            conn.rollback()
            skipped += 1
            print(f'Skipping row: {e}')
            continue
    
    conn.commit()
    print(f'Inserted {count} EGX records.')
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print('Fetching EGX records ...')
    df = fetch_egx_data(EGX_TICKERS, period='1y')
    if not df.empty:
        load_to_postgres(df)
    else:
        print('No data fetched.')
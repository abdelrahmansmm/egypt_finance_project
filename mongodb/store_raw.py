from pymongo import MongoClient
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import json
import yfinance as yf
import psycopg2


load_dotenv()

def get_mongo_collection(collection):
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
    db = client[os.getenv('MONGO_DB', 'egypt_finance_raw')]
    return db[collection]

def fetch_imf_data():
    """
    Fetch Egypt macroeconomic data from IMF DataMapper API.
    Free, no key required.
    """
    indicators = {
        'NGDP_RPCH':'GDP Growth Rate (%)',
        'PCPIPCH':'Inflation Rate (%)',
        'LUR':'Unemployment Rate (%)',
        'BCA_NGDPD':'Current Account Balance (% of GDP)',
        'GGXWDG_NGDP':'Government Debt (% of GDP)',
    }

    collection = get_mongo_collection('imf_raw')
    all_records = []

    for code, name in indicators.items():
        try:
            url = f'https://www.imf.org/external/datamapper/api/v1/{code}/EGY'
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            doc = {
                'source':'IMF',
                'indicator':code,
                'indicator_name':name,
                'country':'EGY',
                'fetched_at':datetime.now(timezone.utc),
                'raw_data':data
            }

            collection.update_one(
                {'source':'IMF', 'indicator':code, 'country':'EGY'},
                {'$set':doc},
                 upsert=True
            )
            print(f'IMF stored document: {name}')
            all_records.append({'code':code, 'name':name, 'data':data})
        except Exception as e:
            print(f'Error fetching {name}: {e}')

    return all_records

def fetch_egx_summary():
    """
    Store daily market summary
    """
    collection = get_mongo_collection('market_summary')

    tickers = ['COMI.CA', 'HRHO.CA', 'TMGH.CA', 'ETEL.CA', 'SWDY.CA']
    summary = {
        'source':'EGX',
        'date':datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'fetched_at':datetime.now(timezone.utc),
        'stocks':[]
    }
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            summary['stocks'].append({
                'ticker':ticker,
                'company':info.get('longName', ticker),
                'current_price':info.get('currentPrice'),
                'market_cap':info.get('marketCap'),
                'pe_ratio':info.get('trailingPE'),
                '52w_high':info.get('fiftyTwoWeekHigh'),
                '52w_low':info.get('fiftyTwoWeekLow'),
            })
            print(f'Fetched summary for {ticker}')
        except Exception as e:
            print(f'Skipping {ticker}: {e}')

    collection.update_one(
        {'source':'EGX', 'date':summary['date']},
        {'$set':summary},
        upsert=True
    )
    date_str = summary['date']
    print(f'EGX market summary stored for {date_str}')

def move_imf_data_to_postgres(records):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    cursor = conn.cursor()
    insert_sql = """
        INSERT INTO imf_data (indicator, period, value, unit)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (indicator, period) DO NOTHING
    """

    count = 0
    for record in records:
        try:
            code = record['code']
            name = record['name']
            data = record['data']

            # Navigate IMF API response structure
            values = data.get('values', {})
            egy_values = values.get(code, {}).get('EGY', {})

            for year, value in egy_values.items():
                if value is not None:
                    cursor.execute(insert_sql, (
                        name,
                        str(year),
                        float(value),
                        '%'
                    ))
                    count += 1
        except Exception as e:
            conn.rollback()
            print(f'Skipping record: {e}')
            continue

    conn.commit()
    print(f'Loaded {count} IMF records to PostgreSQL')
    cursor.close()
    conn.close()

def query_mongo(collection_name, limit=3):
    collection = get_mongo_collection(collection_name)
    docs = list(collection.find().sort('fetched_at', -1).limit(limit))
    for doc in docs:
        doc.pop('_id', None)
        doc.pop('raw_data', None)
        print(json.dumps(docs, default=str, indent=2))

if __name__ == '__main__':
    print('Fetching IMF data ...')
    records = fetch_imf_data()

    print('Fetching EGX summary ...')
    fetch_egx_summary()

    print('Moving IMF data to Postgres ...')
    move_imf_data_to_postgres(records)

    print('Raw data')
    query_mongo('imf_raw')

    print('Market summary')
    query_mongo('market_summary')
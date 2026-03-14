import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

INDICATORS = {
    'NY.GDP.MKTP.CD':'GDP (current US$)',
    'FP.CPI.TOTL.ZG':'Inflation, consumer prices (annual %)',
    'SL.UEM.TOTL.ZS':'Unemployment, total (% of labor force)',
    'BN.CAB.XOKA.CD':'Current account balance (BoP, current US$)',
    'GC.DOD.TOTL.GD.ZS':'Central government debt (% of GDP)',
    'PA.NUS.FCRF':'Official exchange rate (LCU per USD)',
    'FR.INR.RINR':'Real interest rate (%)',
}

def fetch_worldbank(indicator_code, country='EG', start=2000, end=2024):
    url = f'https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}'
    params = {
        'format':'json',
        'per_page':100,
        'date':f'{start}:{end}'
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    if len(data) < 2:
        return []
    return [{'year': int(item['date']), 'value':item['value']} for item in data [1] if item['value'] is not None]

def load_to_postgres(records, code, name):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    cursor = conn.cursor()
    insert_sql = """
        INSERT INTO worldbank_indicators (indicator_code, indicator_name, year, value, country)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """

    for record in records:
        cursor.execute(insert_sql, (code, name, record['year'], record['value'], 'EG'))
    
    conn.commit()
    print(f'Loaded {len(records)} for {name}')
    
    cursor.close()
    conn.close()


if __name__ == '__main__':
    print('Fetching world bank indicators for Egypt.')
    for code, name in INDICATORS.items():
        try: 
            records = fetch_worldbank(code)
            if records:
                load_to_postgres(records, code, name)
            else:
                print(f'No data for {name}')
        except Exception as e:
            print(f'Error fetching {name}: {e}')
    print('Done fetching data.')
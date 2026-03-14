import requests
import psycopg2
from datetime import date, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

BASE_CURRENCIES = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'SAR': 'Saudi Riyal',
    'AED': 'UAE Dirham',
    'KWD': 'Kuwaiti Dinar',
    'QAR': 'Qatari Riyal',
    'JPY': 'Japanese Yen',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
}

def get_db_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def fetch_rates():
    """
    Fetch latest rates using USD as base,
    then calculate EGP per unit for each currency.
    """
    url = 'https://open.er-api.com/v6/latest/USD'
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data['result'] != 'success':
        print('API returned error')
        return []

    usd_to_egp = data['rates']['EGP']
    all_rates   = data['rates']
    rate_date   = date.today()

    rates = []
    for code, name in BASE_CURRENCIES.items():
        if code in all_rates:
            # Convert: 1 unit of currency = EGP
            egp_per_unit = round(usd_to_egp / all_rates[code], 4)
            rates.append({
                'currency_code': code,
                'currency_name': name,
                'buy_rate':      egp_per_unit,
                'sell_rate':     round(egp_per_unit * 1.005, 4),
                'rate_date':     rate_date
            })
            print(f'  {code}: 1 {code} = {egp_per_unit} EGP')

    return rates

def load_to_postgres(rates):
    conn = get_db_conn()
    cursor = conn.cursor()
    insert_sql = '''
        INSERT INTO cbe_exchange_rates
        (currency_code, currency_name, buy_rate, sell_rate, rate_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (currency_code, rate_date) DO NOTHING
    '''
    count = 0
    for rate in rates:
        try:
            cursor.execute(insert_sql, (
                rate['currency_code'],
                rate['currency_name'],
                rate['buy_rate'],
                rate['sell_rate'],
                rate['rate_date']
            ))
            count += 1
        except Exception as e:
            conn.rollback()
            print(f'Skipping {rate["currency_code"]}: {e}')
            continue
    conn.commit()
    print(f'Inserted {count} exchange rate records for {date.today()}')
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print('Fetching exchange rates...')
    rates = fetch_rates()
    if rates:
        load_to_postgres(rates)
    else:
        print('No rates fetched.')
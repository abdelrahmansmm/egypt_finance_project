import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    print('Connected successfully!')
    print('Tables found:')
    for t in tables:
        print(f'   - {t[0]}')

    # Check row counts
    for table in ['cbe_exchange_rates', 'egx_stocks', 'worldbank_indicators', 'imf_data']:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'   {table}: {count} rows')

    cursor.close()
    conn.close()

except Exception as e:
    print(f'Connection failed: {e}')
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'egypt_de_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_DIR = '/opt/egypt_project'
DBT_BIN = '/home/airflow/.local/bin/dbt'

DOCKER_ENV = {
    'POSTGRES_HOST':     'postgres',
    'POSTGRES_PORT':     '5432',
    'POSTGRES_DB':       'egypt_finance',
    'POSTGRES_USER':     'egfinanceuser',
    'POSTGRES_PASSWORD': 'egpassword123',
    'MONGO_URI':         'mongodb://mongodb:27017/',
    'MONGO_DB':          'egypt_finance_raw',
}

with DAG(
    dag_id='egypt_finance_pipeline',
    default_args=default_args,
    description='End-to-End Egypt Finance Data Pipeline',
    schedule_interval='0 8 * * 1-5',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['egypt', 'finance', 'production'],
) as dag:

    ingest_worldbank = BashOperator(
        task_id='ingest_worldbank',
        bash_command=f'python {PROJECT_DIR}/ingestion/world_bank.py',
        env=DOCKER_ENV,
    )

    ingest_egx = BashOperator(
        task_id='ingest_egx_stocks',
        bash_command=f'python {PROJECT_DIR}/ingestion/egx_stocks.py',
        env=DOCKER_ENV,
    )

    ingest_rates = BashOperator(
        task_id='ingest_exchange_rates',
        bash_command=f'python {PROJECT_DIR}/ingestion/cbe_rates.py',
        env=DOCKER_ENV,
    )

    store_mongodb = BashOperator(
        task_id='store_raw_to_mongodb',
        bash_command=f'python {PROJECT_DIR}/mongodb/store_raw.py',
        env=DOCKER_ENV,
    )

    dbt_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command=f'cd {PROJECT_DIR}/dbt_project && {DBT_BIN} run --select staging',
    )

    dbt_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command=f'cd {PROJECT_DIR}/dbt_project && {DBT_BIN} run --select marts',
    )

    dbt_tests = BashOperator(
        task_id='dbt_tests',
        bash_command=f'cd {PROJECT_DIR}/dbt_project && {DBT_BIN} test',
    )

    # Pipeline flow
    [ingest_worldbank, ingest_egx, ingest_rates] >> store_mongodb
    store_mongodb >> dbt_staging
    dbt_staging >> dbt_marts
    dbt_marts >> dbt_tests
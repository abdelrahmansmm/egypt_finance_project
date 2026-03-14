{{ config(materialized='table') }}

WITH stock_data AS (
    SELECT * FROM {{ ref('stg_egx_stocks') }}
)

SELECT
    ticker,
    company_name,
    COUNT(*) AS trading_days,
    ROUND(AVG(close_price), 2) AS avg_close_price,
    ROUND(MAX(close_price), 2) AS all_time_high,
    ROUND(MIN(close_price), 2) AS all_time_low,
    ROUND(AVG(daily_return_pct), 4) AS avg_daily_return_pct,
    ROUND(STDDEV(daily_return_pct)::NUMERIC, 4) AS volatility,
    SUM(volume) AS total_volume,
    ROUND(AVG(volume), 0) AS avg_daily_volume,
    MIN(trade_date) AS first_date,
    MAX(trade_date) AS last_date
FROM stock_data
GROUP BY ticker, company_name
ORDER BY avg_daily_return_pct DESC
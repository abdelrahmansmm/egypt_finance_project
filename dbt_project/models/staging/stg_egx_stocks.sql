{{ config(materialized='view') }}

SELECT
    id,
    UPPER(TRIM(ticker)) AS ticker,
    TRIM(company_name) AS company_name,
    ROUND(open_price::NUMERIC, 2) AS open_price,
    ROUND(close_price::NUMERIC, 2) AS close_price,
    ROUND(high_price::NUMERIC, 2) AS high_price,
    ROUND(low_price::NUMERIC, 2) AS low_price,
    volume,
    trade_date,
    -- Derived fields
    ROUND(((close_price - open_price) / NULLIF(open_price, 0)) * 100, 2)  AS daily_return_pct,
    ROUND(high_price - low_price, 2) AS daily_range
FROM {{ source('raw', 'egx_stocks') }}
WHERE
    close_price > 0
    AND trade_date IS NOT NULL
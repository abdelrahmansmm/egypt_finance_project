{{ config(materialized='view') }}

SELECT
    id,
    UPPER(TRIM(currency_code)) AS currency_code,
    TRIM(currency_name) AS currency_name,
    ROUND(buy_rate::NUMERIC, 4) AS buy_rate_egp,
    ROUND(sell_rate::NUMERIC, 4) AS sell_rate_egp,
    ROUND((buy_rate + sell_rate) / 2.0, 4) AS mid_rate_egp,
    ROUND(sell_rate - buy_rate, 4) AS spread,
    rate_date
FROM {{ source('raw', 'cbe_exchange_rates') }}
WHERE
    buy_rate > 0
    AND sell_rate > 0
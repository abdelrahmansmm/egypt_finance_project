{{ config(materialized='table') }}

WITH stock_data AS (
    SELECT * FROM {{ ref('stg_egx_stocks') }}
),

daily_agg AS (
    SELECT
        trade_date,
        COUNT(DISTINCT ticker) AS stocks_traded,
        SUM(volume) AS total_volume,
        ROUND(AVG(daily_return_pct), 4) AS avg_market_return_pct,
        MAX(daily_return_pct) AS top_gainer_pct,
        MIN(daily_return_pct) AS top_loser_pct,
        SUM(close_price * volume) AS approx_market_cap_egp
    FROM stock_data
    GROUP BY trade_date
)

SELECT
    trade_date,
    stocks_traded,
    total_volume,
    avg_market_return_pct,
    top_gainer_pct,
    top_loser_pct,
    ROUND(approx_market_cap_egp / 1000000, 2) AS market_cap_millions_egp,
    CASE
        WHEN avg_market_return_pct > 0 THEN 'Bullish'
        WHEN avg_market_return_pct < 0 THEN 'Bearish'
        ELSE 'Neutral'
    END AS market_sentiment
FROM daily_agg
ORDER BY trade_date DESC
{{ config(materialized='table') }}

WITH worldbank AS (
    SELECT
        year,
        MAX(CASE WHEN indicator_code = 'FP.CPI.TOTL.ZG'
            THEN value END) AS inflation_pct,
        MAX(CASE WHEN indicator_code = 'NY.GDP.MKTP.CD'
            THEN value END) AS gdp_usd,
        MAX(CASE WHEN indicator_code = 'SL.UEM.TOTL.ZS'
            THEN value END) AS unemployment_pct,
        MAX(CASE WHEN indicator_code = 'PA.NUS.FCRF'
            THEN value END) AS usd_egp_rate
    FROM {{ ref('stg_worldbank') }}
    GROUP BY year
),

imf AS (
    SELECT
        year,
        MAX(CASE WHEN indicator_name = 'GDP Growth Rate (%)'
            THEN value END) AS gdp_growth_pct,
        MAX(CASE WHEN indicator_name = 'Government Debt (% of GDP)'
            THEN value END) AS govt_debt_pct
    FROM {{ ref('stg_imf_data') }}
    GROUP BY year
)

SELECT
    w.year,
    ROUND(w.inflation_pct::NUMERIC, 2) AS inflation_pct,
    ROUND(w.gdp_usd / 1000000000, 2) AS gdp_billions_usd,
    ROUND(w.unemployment_pct::NUMERIC, 2) AS unemployment_pct,
    ROUND(w.usd_egp_rate::NUMERIC, 4) AS usd_egp_rate,
    ROUND(i.gdp_growth_pct::NUMERIC, 2) AS gdp_growth_pct,
    ROUND(i.govt_debt_pct::NUMERIC, 2) AS govt_debt_pct
FROM worldbank w
LEFT JOIN imf i ON w.year = i.year
WHERE w.year >= 2000
ORDER BY w.year DESC
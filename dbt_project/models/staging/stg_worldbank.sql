{{ config(materialized='view') }}

SELECT
    id,
    TRIM(indicator_code) AS indicator_code,
    TRIM(indicator_name) AS indicator_name,
    year,
    ROUND(value::NUMERIC, 4) AS value,
    country
FROM {{ source('raw', 'worldbank_indicators') }}
WHERE
    value IS NOT NULL
    AND year IS NOT NULL
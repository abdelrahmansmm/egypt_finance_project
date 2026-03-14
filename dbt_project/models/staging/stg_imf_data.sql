{{ config(materialized='view') }}

SELECT
    id,
    TRIM(indicator) AS indicator_name,
    period::INT AS year,
    ROUND(value::NUMERIC, 4) AS value,
    unit
FROM {{ source('raw', 'imf_data') }}
WHERE
    value IS NOT NULL
    AND period IS NOT NULL
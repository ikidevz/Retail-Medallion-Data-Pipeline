-- Populate gold_dim_date for any dates not yet present
-- Covers the last 3 years through 1 year ahead
INSERT INTO gold.dim_date (
    date_key, full_date, year, month, day,
    weekday, weekday_name, is_weekend, quarter, fiscal_year
)
SELECT
    TO_CHAR(d::DATE, 'YYYYMMDD')::INT                AS date_key,
    d::DATE                                           AS full_date,
    EXTRACT(YEAR  FROM d)::INT                        AS year,
    EXTRACT(MONTH FROM d)::INT                        AS month,
    EXTRACT(DAY   FROM d)::INT                        AS day,
    EXTRACT(DOW   FROM d)::INT                        AS weekday,
    TO_CHAR(d, 'Day')                                 AS weekday_name,
    EXTRACT(DOW FROM d) IN (0, 6)                     AS is_weekend,
    EXTRACT(QUARTER FROM d)::INT                      AS quarter,
    -- Philippine fiscal year: Jan–Dec same as calendar year
    EXTRACT(YEAR FROM d)::INT                         AS fiscal_year
FROM generate_series(
    CURRENT_DATE - INTERVAL '3 years',
    CURRENT_DATE + INTERVAL '1 year',
    INTERVAL '1 day'
) AS g(d)
ON CONFLICT (date_key) DO NOTHING;
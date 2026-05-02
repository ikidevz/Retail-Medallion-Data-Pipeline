-- Upsert stores discovered in Silver data not yet in Gold
INSERT INTO gold.dim_store (
    store_id, store_name, region, province, city, store_type,
    opening_date, size_sqm
)
SELECT DISTINCT
    s.store_id,
    CONCAT('Store ', s.store_id)              AS store_name,
    CASE
        WHEN s.store_id BETWEEN 'STR-001' AND 'STR-015' THEN 'NCR'
        WHEN s.store_id BETWEEN 'STR-016' AND 'STR-030' THEN 'Visayas'
        WHEN s.store_id BETWEEN 'STR-031' AND 'STR-045' THEN 'Mindanao'
        ELSE 'Luzon'
    END                                       AS region,
    NULL::VARCHAR                             AS province,
    NULL::VARCHAR                             AS city,
    'Supermarket'                             AS store_type,
    DATE '2020-01-01'                         AS opening_date,
    FLOOR(RANDOM() * 1500 + 500)::INT         AS size_sqm
FROM silver.sales_cleaned s
WHERE NOT EXISTS (
    SELECT 1 FROM gold.dim_store g WHERE g.store_id = s.store_id
)
ON CONFLICT DO NOTHING;
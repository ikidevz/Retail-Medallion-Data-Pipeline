INSERT INTO gold.dim_supplier (
    supplier_id, supplier_name, country,
    lead_time_days, credit_terms_days, is_active
)
SELECT DISTINCT
    sm.supplier_id,
    CONCAT('Supplier ', sm.supplier_id) AS supplier_name,
    'Philippines'                        AS country,
    FLOOR(RANDOM() * 14 + 1)::INT        AS lead_time_days,
    30                                   AS credit_terms_days,
    TRUE
FROM silver.stock_movement_cleaned sm
WHERE sm.supplier_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM gold.dim_supplier g WHERE g.supplier_id = sm.supplier_id
    )
ON CONFLICT DO NOTHING;
INSERT INTO gold.fact_stock_movement (
    date_key, product_key, store_key, supplier_key,
    movement_type, quantity, reason, reference_id
)
SELECT
    TO_CHAR(DATE(sm.movement_ts), 'YYYYMMDD')::INT AS date_key,
    p.product_key,
    st.store_key,
    sup.supplier_key,
    sm.movement_type,
    sm.quantity,
    sm.reason,
    sm.reference_id
FROM silver.stock_movement_cleaned sm
JOIN gold.dim_product  p   ON p.product_id   = sm.product_id   AND p.valid_to = '9999-12-31'
JOIN gold.dim_store    st  ON st.store_id    = sm.store_id
LEFT JOIN gold.dim_supplier sup ON sup.supplier_id = sm.supplier_id
WHERE DATE(sm.movement_ts) = CURRENT_DATE - INTERVAL '1 day'
    AND sm.is_valid = TRUE
    AND NOT EXISTS (
        SELECT 1 FROM gold.fact_stock_movement gf
        WHERE gf.reference_id = sm.reference_id
    );
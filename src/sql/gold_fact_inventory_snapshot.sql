INSERT INTO gold.fact_inventory_snapshot (
    date_key, product_key, store_key,
    stock_on_hand, reorder_point, days_of_inventory
)
SELECT
    TO_CHAR(DATE(i.snapshot_ts), 'YYYYMMDD')::INT  AS date_key,
    p.product_key,
    st.store_key,
    i.stock_level                                   AS stock_on_hand,
    i.reorder_point,
    -- Days of inventory = stock / avg daily sales (naive: stock / 10)
    ROUND((i.stock_level::NUMERIC / NULLIF(10, 0)), 2) AS days_of_inventory
FROM silver.inventory_cleaned i
JOIN gold.dim_product p  ON p.product_id = i.product_id AND p.valid_to = '9999-12-31'
JOIN gold.dim_store   st ON st.store_id  = i.store_id
WHERE DATE(i.snapshot_ts) = CURRENT_DATE - INTERVAL '1 day'
    AND i.is_valid = TRUE;
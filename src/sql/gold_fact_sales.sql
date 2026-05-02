-- Load yesterday's Silver sales into gold_fact_sales
INSERT INTO gold.fact_sales (
    date_key, product_key, store_key,
    customer_key, promo_key,
    sale_ts, quantity, gross_amount, discount_amount, net_amount,
    transaction_id
)
SELECT
    TO_CHAR(DATE(s.sale_ts), 'YYYYMMDD')::INT  AS date_key,
    p.product_key,
    st.store_key,
    c.customer_key,
    pr.promo_key,
    s.sale_ts,
    s.quantity,
    s.amount                                    AS gross_amount,
    s.discount_amount,
    s.net_amount,
    s.transaction_id
FROM silver.sales_cleaned s
JOIN gold.dim_product  p  ON p.product_id = s.product_id  AND p.valid_to = '9999-12-31'
JOIN gold.dim_store    st ON st.store_id  = s.store_id
JOIN gold.dim_customer c  ON c.customer_id = 'UNKNOWN'
JOIN gold.dim_promotion pr ON pr.promo_id  = 'NO_PROMO'
WHERE DATE(s.sale_ts) = CURRENT_DATE - INTERVAL '1 day'
    AND s.is_valid = TRUE
    AND NOT EXISTS (
        SELECT 1 FROM gold.fact_sales gf
        WHERE gf.transaction_id = s.transaction_id
    );
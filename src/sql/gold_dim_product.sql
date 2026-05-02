-- Insert new products not yet tracked in Gold
-- SCD Type 2: valid_from = today, valid_to = '9999-12-31' (open record)
INSERT INTO gold.dim_product (
    product_id, product_name, brand, category, subcategory,
    unit_cost, unit_price, supplier_key,
    is_active, valid_from, valid_to
)
SELECT DISTINCT
    s.product_id,
    CONCAT('Product ', s.product_id)           AS product_name,
    'Generic Brand'                             AS brand,
    CASE
        WHEN s.product_id BETWEEN 'PRD-0001' AND 'PRD-0100' THEN 'Food & Beverage'
        WHEN s.product_id BETWEEN 'PRD-0101' AND 'PRD-0200' THEN 'Personal Care'
        WHEN s.product_id BETWEEN 'PRD-0201' AND 'PRD-0300' THEN 'Household'
        WHEN s.product_id BETWEEN 'PRD-0301' AND 'PRD-0400' THEN 'Electronics'
        ELSE 'General Merchandise'
    END                                         AS category,
    NULL::VARCHAR                               AS subcategory,
    ROUND((RANDOM() * 400 + 50)::NUMERIC, 2)   AS unit_cost,
    ROUND((RANDOM() * 600 + 100)::NUMERIC, 2)  AS unit_price,
    NULL::INT                                   AS supplier_key,
    TRUE,
    CURRENT_DATE                                AS valid_from,
    '9999-12-31'::DATE                          AS valid_to
FROM silver.sales_cleaned s
WHERE NOT EXISTS (
    SELECT 1 FROM gold.dim_product g
    WHERE g.product_id = s.product_id
        AND g.valid_to = '9999-12-31'
)
ON CONFLICT DO NOTHING;
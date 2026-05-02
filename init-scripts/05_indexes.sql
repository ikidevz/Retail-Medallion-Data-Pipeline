-- =============================================
-- INDEXES
-- =============================================

\c retail_pipeline

-- Bronze
CREATE INDEX IF NOT EXISTS idx_bronze_sales_batch      ON bronze.sales_raw(batch_id);
CREATE INDEX IF NOT EXISTS idx_bronze_sales_sale_ts    ON bronze.sales_raw(sale_ts);

CREATE INDEX IF NOT EXISTS idx_bronze_inventory_batch  ON bronze.inventory_raw(batch_id);
CREATE INDEX IF NOT EXISTS idx_bronze_mvmt_batch       ON bronze.stock_movement_raw(batch_id);

-- Silver
CREATE INDEX IF NOT EXISTS idx_silver_sales_product    ON silver.sales_cleaned(product_id);
CREATE INDEX IF NOT EXISTS idx_silver_sales_batch      ON silver.sales_cleaned(batch_id);
CREATE INDEX IF NOT EXISTS idx_silver_sales_valid      ON silver.sales_cleaned(is_valid);

-- Gold
CREATE INDEX IF NOT EXISTS idx_gold_sales_date         ON gold.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_gold_sales_product      ON gold.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_gold_sales_store        ON gold.fact_sales(store_key);
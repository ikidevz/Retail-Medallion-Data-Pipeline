-- =============================================
-- COMMENTS
-- =============================================

COMMENT ON SCHEMA bronze IS 'Raw ingestion layer';
COMMENT ON SCHEMA silver IS 'Cleaned and validated layer';
COMMENT ON SCHEMA gold   IS 'Business-level dimensional model';

COMMENT ON TABLE bronze.sales_raw IS 'Raw sales transactions from POS systems';
COMMENT ON TABLE silver.sales_cleaned IS 'Validated and cleaned sales data';
COMMENT ON TABLE gold.fact_sales IS 'Sales fact table (1 row per transaction)';

COMMENT ON TABLE gold.dim_product IS 'SCD Type 2 product dimension';
-- =============================================
-- BRONZE LAYER (Raw)
-- =============================================

\c retail_pipeline

CREATE TABLE IF NOT EXISTS bronze.sales_raw (
    raw_id              SERIAL PRIMARY KEY,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50),
    transaction_id      VARCHAR(100),
    sale_ts             TIMESTAMP,
    product_id          VARCHAR(50),
    store_id            VARCHAR(50),
    quantity            INTEGER,
    amount              NUMERIC(12,2),
    discount_amount     NUMERIC(12,2),
    payment_method      VARCHAR(50),
    source_system       VARCHAR(50),
    raw_json            JSONB
);

CREATE TABLE IF NOT EXISTS bronze.inventory_raw (
    raw_id              SERIAL PRIMARY KEY,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50),
    snapshot_ts         TIMESTAMP,
    product_id          VARCHAR(50),
    store_id            VARCHAR(50),
    stock_level         INTEGER,
    reorder_point       INTEGER,
    source_system       VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS bronze.stock_movement_raw (
    raw_id              SERIAL PRIMARY KEY,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50),
    movement_ts         TIMESTAMP,
    product_id          VARCHAR(50),
    store_id            VARCHAR(50),
    supplier_id         VARCHAR(50),
    movement_type       VARCHAR(50),
    quantity            INTEGER,
    reason              TEXT,
    reference_id        VARCHAR(100)
);
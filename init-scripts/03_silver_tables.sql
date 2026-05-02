-- =============================================
-- SILVER LAYER (Cleaned)
-- =============================================

CREATE TABLE IF NOT EXISTS silver.sales_cleaned (
    sale_id             BIGSERIAL PRIMARY KEY,
    ingestion_timestamp TIMESTAMP,
    cleaned_ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50),
    transaction_id      VARCHAR(100) UNIQUE,
    sale_ts             TIMESTAMP,
    product_id          VARCHAR(50),
    store_id            VARCHAR(50),
    quantity            INTEGER,
    amount              NUMERIC(12,2),
    discount_amount     NUMERIC(12,2),
    net_amount          NUMERIC(12,2),
    payment_method      VARCHAR(50),
    is_valid            BOOLEAN DEFAULT TRUE,
    error_reason        TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.inventory_cleaned (
    inventory_id        BIGSERIAL PRIMARY KEY,
    ingestion_timestamp TIMESTAMP,
    cleaned_ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50),
    snapshot_ts         TIMESTAMP,
    product_id          VARCHAR(50),
    store_id            VARCHAR(50),
    stock_level         INTEGER,
    reorder_point       INTEGER,
    is_valid            BOOLEAN DEFAULT TRUE,
    error_reason        TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.stock_movement_cleaned (
    movement_id         BIGSERIAL PRIMARY KEY,
    ingestion_timestamp TIMESTAMP,
    cleaned_ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50),
    movement_ts         TIMESTAMP,
    product_id          VARCHAR(50),
    store_id            VARCHAR(50),
    supplier_id         VARCHAR(50),
    movement_type       VARCHAR(50),
    quantity            INTEGER,
    reason              TEXT,
    reference_id        VARCHAR(100),
    is_valid            BOOLEAN DEFAULT TRUE,
    error_reason        TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
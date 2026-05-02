-- =============================================
-- GOLD LAYER (Star Schema)
-- =============================================

-- Dimensions

CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_key     INTEGER PRIMARY KEY,
    full_date    DATE NOT NULL,
    year         INTEGER,
    month        INTEGER,
    day          INTEGER,
    weekday      INTEGER,
    weekday_name VARCHAR(10),
    is_weekend   BOOLEAN,
    quarter      INTEGER,
    fiscal_year  INTEGER
);

CREATE TABLE IF NOT EXISTS gold.dim_product (
    product_key  SERIAL PRIMARY KEY,
    product_id   VARCHAR(50),
    product_name VARCHAR(200),
    brand        VARCHAR(100),
    category     VARCHAR(100),
    subcategory  VARCHAR(100),
    unit_cost    NUMERIC(12,2),
    unit_price   NUMERIC(12,2),
    supplier_key INTEGER,
    is_active    BOOLEAN DEFAULT TRUE,
    valid_from   DATE,
    valid_to     DATE DEFAULT '9999-12-31'
);

CREATE TABLE IF NOT EXISTS gold.dim_store (
    store_key    SERIAL PRIMARY KEY,
    store_id     VARCHAR(50) UNIQUE,
    store_name   VARCHAR(200),
    region       VARCHAR(50),
    province     VARCHAR(100),
    city         VARCHAR(100),
    store_type   VARCHAR(50),
    opening_date DATE,
    size_sqm     INTEGER
);

CREATE TABLE IF NOT EXISTS gold.dim_supplier (
    supplier_key       SERIAL PRIMARY KEY,
    supplier_id        VARCHAR(50) UNIQUE,
    supplier_name      VARCHAR(200),
    country            VARCHAR(100),
    lead_time_days     INTEGER,
    credit_terms_days  INTEGER,
    is_active          BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS gold.dim_customer (
    customer_key    SERIAL PRIMARY KEY,
    customer_id     VARCHAR(50) UNIQUE,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    membership_tier VARCHAR(50),
    join_date       DATE,
    city            VARCHAR(100),
    region          VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS gold.dim_promotion (
    promo_key     SERIAL PRIMARY KEY,
    promo_id      VARCHAR(50) UNIQUE,
    promo_name    VARCHAR(200),
    promo_type    VARCHAR(50),
    discount_rate NUMERIC(5,2),
    start_date    DATE,
    end_date      DATE
);

-- Facts

CREATE TABLE IF NOT EXISTS gold.fact_sales (
    sale_key        BIGSERIAL PRIMARY KEY,
    date_key        INTEGER REFERENCES gold.dim_date(date_key),
    product_key     INTEGER REFERENCES gold.dim_product(product_key),
    store_key       INTEGER REFERENCES gold.dim_store(store_key),
    customer_key    INTEGER REFERENCES gold.dim_customer(customer_key),
    promo_key       INTEGER REFERENCES gold.dim_promotion(promo_key),
    sale_ts         TIMESTAMP,
    quantity        INTEGER,
    gross_amount    NUMERIC(12,2),
    discount_amount NUMERIC(12,2),
    net_amount      NUMERIC(12,2),
    transaction_id  VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS gold.fact_inventory_snapshot (
    snapshot_key    BIGSERIAL PRIMARY KEY,
    date_key        INTEGER REFERENCES gold.dim_date(date_key),
    product_key     INTEGER REFERENCES gold.dim_product(product_key),
    store_key       INTEGER REFERENCES gold.dim_store(store_key),
    stock_on_hand   INTEGER,
    reorder_point   INTEGER,
    days_of_inventory NUMERIC(6,2)
);

CREATE TABLE IF NOT EXISTS gold.fact_stock_movement (
    movement_key  BIGSERIAL PRIMARY KEY,
    date_key      INTEGER REFERENCES gold.dim_date(date_key),
    product_key   INTEGER REFERENCES gold.dim_product(product_key),
    store_key     INTEGER REFERENCES gold.dim_store(store_key),
    supplier_key  INTEGER REFERENCES gold.dim_supplier(supplier_key),
    movement_type VARCHAR(50),
    quantity      INTEGER,
    reason        TEXT,
    reference_id  VARCHAR(100)
);
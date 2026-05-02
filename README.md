# Retail Medallion Pipeline

> **Production-Grade Retail Data Pipeline | Medallion Architecture (Bronze → Silver → Gold)**
> Simulating a large Philippine retail company's sales and inventory data platform.

---

## Overview

End-to-end data engineering project built on the **Medallion Architecture**. Handles raw sales and inventory data from 50 Philippine retail stores, applies Polars-based cleaning and validation, and builds a Star Schema dimensional model ready for analytics and reporting.

---

## Tech Stack

| Layer            | Tool                         |
| ---------------- | ---------------------------- |
| Language         | Python 3.12                  |
| Orchestration    | Apache Airflow 3.2.1         |
| Database         | PostgreSQL 16                |
| Data Processing  | Polars (Silver) + SQL (Gold) |
| Containerization | Docker + Docker Compose      |
| DB Admin         | pgAdmin 4                    |
| Version Control  | Git                          |

---

## Architecture

```
RAW SOURCES
    │
    ▼
┌─────────────────────────────────────────────┐
│  BRONZE LAYER — Raw Landing Zone            │
│  • Append-only, no transformation           │
│  • Includes ingestion metadata & batch_id   │
│  Schema: bronze.*                           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  SILVER LAYER — Cleaned & Validated         │
│  • Polars-based transformation              │
│  • Data quality checks (is_valid flag)      │
│  • Incremental: resolves unprocessed batches│
│  Schema: silver.*                           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  GOLD LAYER — Star Schema (Analytics-Ready) │
│  • 6 Dimension Tables (SCD Type 2)          │
│  • 3 Fact Tables (idempotent loads)         │
│  • Validated via SQLCheckOperator           │
│  Schema: gold.*                             │
└─────────────────────────────────────────────┘
```

---

## Data Model

| Layer      | Tables                                                                                                                       |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Bronze     | `bronze.sales_raw`, `bronze.inventory_raw`, `bronze.stock_movement_raw`                                                      |
| Silver     | `silver.sales_cleaned`, `silver.inventory_cleaned`, `silver.stock_movement_cleaned`                                          |
| Gold Dims  | `gold.dim_date`, `gold.dim_product` (SCD2), `gold.dim_store`, `gold.dim_supplier`, `gold.dim_customer`, `gold.dim_promotion` |
| Gold Facts | `gold.fact_sales`, `gold.fact_inventory_snapshot`, `gold.fact_stock_movement`                                                |
| **Total**  | **15 tables**                                                                                                                |

---

## Project Structure

```
retail-medallion-pipeline/
│
├── dags/
│   ├── tasks.py                        # All DAG callable functions (centralized)
│   ├── bronze_ingestion_dag.py         # DAG 1: Hourly — generate & load raw data
│   ├── silver_cleaning_dag.py          # DAG 2: Hourly +30m — clean & validate
│   └── gold_marts_dag.py               # DAG 3: Daily 02:00 — build Star Schema
│
├── src/
│   ├── generators/
│   │   ├── sales_generator.py          # Synthetic sales (200–500 rows/hr)
│   │   ├── inventory_generator.py      # Synthetic inventory (40–80 rows/hr)
│   │   └── stock_movement_generator.py # Synthetic movements (80–150 rows/hr)
│   ├── bronze/
│   │   └── loader.py                   # Bulk insert → bronze.*
│   ├── silver/
│   │   ├── clean_sales.py              # Polars cleaning → silver.sales_cleaned
│   │   ├── clean_inventory.py          # Polars cleaning → silver.inventory_cleaned
│   │   └── clean_stock_movement.py     # Polars cleaning → silver.stock_movement_cleaned
│   ├── gold/
│   │   ├── dim_loader.py               # Python wrappers for all dim upserts
│   │   └── fact_loader.py              # Python wrappers for all fact loads
│   └── utils/
│       ├── db.py                       # PostgreSQL connection helper
│       ├── logger.py                   # Structured logging
│       └── batch.py                    # Batch ID generation
│
├── sql/
│   ├── ddl/
│   │   └── full_ddl.sql                # All 15 CREATE TABLE statements
│   └── gold/
│       ├── dim_date_populate.sql       # Standalone dim_date seed script
│       └── fact_sales_load.sql         # Standalone fact_sales load script
│
├── init-scripts/                       # Auto-run by PostgreSQL on first startup
│   ├── 01_create_schemas.sql           # Creates bronze/silver/gold schemas
│   ├── 02_bronze_tables.sql            # Bronze table DDL
│   ├── 03_silver_tables.sql            # Silver table DDL
│   └── 04_gold_tables.sql              # Gold table DDL
│
├── config/
│   ├── setup_conn.py                   # Registers postgres_pipeline Airflow connection
│   ├── settings.py                     # Env-based config
│   └── pgadmin/
│       ├── servers.json                # Auto-registers postgres servers in pgAdmin
│       └── pgpass                      # Auto-login credentials for pgAdmin
│
├── tests/
│   └── test_generators.py              # Unit tests for synthetic generators
│
├── Dockerfile.airflow                  # Custom Airflow image with dependencies
├── docker-compose.yml                  # Full stack: Airflow + PostgreSQL + pgAdmin
├── airflow_local_settings.py           # Adds src/ to PYTHONPATH for local dev
├── conftest.py                         # pytest path setup
├── setup.py                            # pip install -e . for local dev
├── requirements.txt                    # Pinned Python dependencies
└── README.md
```

---

## DAG Schedule

| DAG                         | Schedule     | Description                                   |
| --------------------------- | ------------ | --------------------------------------------- |
| `1-retail_bronze_ingestion` | `0 * * * *`  | Generate synthetic data → load to `bronze.*`  |
| `2-retail_silver_cleaning`  | `30 * * * *` | Clean unprocessed Bronze batches → `silver.*` |
| `3-retail_gold_marts`       | `0 2 * * *`  | Build dimensions & facts → `gold.*`           |

### DAG Task Flow

```
Bronze:  db_health → gen_batch_id → [ingest_sales || ingest_inventory || ingest_movements] → summary

Silver:  db_health → resolve_batch → [clean_sales || clean_inventory || clean_movements] → quality_gate → summary

Gold:    [6 dims in parallel] → [3 facts in parallel] → validate_gold (SQLCheckOperator)
```

---

## Databases

| Database          | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| `airflow`         | Airflow metadata (managed by Airflow internally) |
| `retail_pipeline` | Pipeline data — bronze, silver, gold schemas     |

---

## Services

| Service    | URL                   |
| ---------- | --------------------- |
| Airflow UI | http://localhost:8080 |
| pgAdmin    | http://localhost:5050 |

**pgAdmin credentials:** `admin@admin.com` / `admin123`
**Airflow credentials:** `airflow` / `airflow`

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/youruser/retail-medallion-pipeline.git
cd retail-medallion-pipeline

# 2. Set environment variables
cp .env.example .env

# 3. Build and start all services
docker compose up --build

# 4. Access Airflow UI
open http://localhost:8080

# 5. Access pgAdmin
open http://localhost:5050
```

---

## Environment Variables

```dotenv
# PostgreSQL
POSTGRES_USER=retail_user
POSTGRES_PASSWORD=retail_password
POSTGRES_DB=airflow
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

PIPELINE_DB_NAME=retail_pipeline

# Airflow
AIRFLOW_UID=50000
FERNET_KEY=your_fernet_key
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://retail_user:retail_password@postgres/airflow
AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://retail_user:retail_password@postgres/airflow
AIRFLOW__CELERY__BROKER_URL=redis://:@redis:6379/0
```

---

## Data Volume (Synthetic)

| Entity              | Volume per Hourly Run        |
| ------------------- | ---------------------------- |
| Stores              | 50 Philippine retail stores  |
| Products            | 500 SKUs across 5 categories |
| Suppliers           | 30 suppliers                 |
| Sales transactions  | 200–500 rows                 |
| Inventory snapshots | 40–80 rows                   |
| Stock movements     | 80–150 rows                  |

---

## Key Design Decisions

| Decision                               | Rationale                                                          |
| -------------------------------------- | ------------------------------------------------------------------ |
| Separate DAG per layer                 | Different schedules, independent failure blast radius              |
| Polars for Silver                      | Faster than pandas for columnar validation at scale                |
| `SQLCheckOperator` for Gold validation | Native Airflow — no Python overhead, clean DAG                     |
| SCD Type 2 on `dim_product`            | Tracks price/category changes over time                            |
| Idempotent fact loads                  | `NOT EXISTS` guard prevents duplicate inserts on re-runs           |
| `batch_id` tracking                    | Silver resolves only unprocessed Bronze batches                    |
| Schema-per-layer                       | `bronze.*` / `silver.*` / `gold.*` — explicit, production standard |

---

_Portfolio project by **ikigami** — Philippine Retail Data Engineering Showcase_

"""
dags/gold_marts_dag.py

DAG 3 — Gold Layer: Star Schema Mart Build
Loads Silver-cleaned data into the Gold dimensional model.
Runs daily at 02:00 (after Silver has accumulated a full day of data).

Build order:
  1. Dimensions (can run in parallel)
  2. Fact tables (depend on all dimensions being populated)
  3. Validation
"""

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime

from tasks import validate_gold_layer, default_args

_CONN = "retail_pipeline_db"


# ── DAG ───────────────────────────────────────────────────────────────────────

with DAG(
    "3-retail_gold_marts",
    default_args=default_args,
    start_date=datetime(2026, 5, 1),
    description="Build Gold dimensional model (Star Schema) from Silver layer",
    schedule="0 2 * * *",      # Daily at 02:00
    catchup=False,
    tags=["gold", "marts", "retail"],
) as dag:

    # ── DIMENSION: Date ───────────────────────────────────────────────────────
    build_dim_date = SQLExecuteQueryOperator(
        task_id="build_dim_date",
        conn_id=_CONN,
        sql="src/sql/gold_dim_date.sql",
    )

    # ── DIMENSION: Store ──────────────────────────────────────────────────────
    build_dim_store = SQLExecuteQueryOperator(
        task_id="build_dim_store",
        conn_id=_CONN,
        sql="src/sql/gold_dim_store.sql",
    )

    # ── DIMENSION: Supplier ───────────────────────────────────────────────────
    build_dim_supplier = SQLExecuteQueryOperator(
        task_id="build_dim_supplier",
        conn_id=_CONN,
        sql="src/sql/gold_dim_supplier.sql",
    )

    # ── DIMENSION: Product (SCD Type 2) ───────────────────────────────────────
    build_dim_product = SQLExecuteQueryOperator(
        task_id="build_dim_product",
        conn_id=_CONN,
        sql="src/sql/gold_dim_product.sql",
    )

    # ── DIMENSION: Customer ───────────────────────────────────────────────────
    build_dim_customer = SQLExecuteQueryOperator(
        task_id="build_dim_customer",
        conn_id=_CONN,
        sql="src/sql/gold_dim_customer.sql",
    )

    # ── DIMENSION: Promotion ─────────────────────────────────────────────────
    build_dim_promotion = SQLExecuteQueryOperator(
        task_id="build_dim_promotion",
        conn_id=_CONN,
        sql="src/sql/gold_dim_promotion.sql",
    )

    # ── FACT: Sales ───────────────────────────────────────────────────────────
    build_fact_sales = SQLExecuteQueryOperator(
        task_id="build_fact_sales",
        conn_id=_CONN,
        sql="src/sql/gold_fact_sales.sql",
    )

    # ── FACT: Inventory Snapshot ──────────────────────────────────────────────
    build_fact_inventory = SQLExecuteQueryOperator(
        task_id="build_fact_inventory_snapshot",
        conn_id=_CONN,
        sql="src/sql/gold_fact_inventory_snapshot.sql",
    )

    # ── FACT: Stock Movement ──────────────────────────────────────────────────
    build_fact_stock_movement = SQLExecuteQueryOperator(
        task_id="build_fact_stock_movement",
        conn_id=_CONN,
        sql="src/sql/gold_fact_stock_movement.sql",
    )

    # ── Validation ────────────────────────────────────────────────────────────
    validate_gold = PythonOperator(
        task_id="validate_gold_layer",
        python_callable=validate_gold_layer,
    )

    dims = [
        build_dim_date,
        build_dim_store,
        build_dim_supplier,
        build_dim_product,
        build_dim_customer,
        build_dim_promotion,
    ]

    facts = [
        build_fact_sales,
        build_fact_inventory,
        build_fact_stock_movement,
    ]

    for dim in dims:
        for fact in facts:
            dim >> fact

    for fact in facts:
        fact >> validate_gold

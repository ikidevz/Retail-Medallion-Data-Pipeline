"""
dags/silver_cleaning_dag.py

DAG 2 — Silver Layer Cleaning
Reads the latest unprocessed Bronze batch, applies Polars-based
data quality validation, and writes clean records to Silver tables.

Schedule: 30 minutes after every hour (runs after Bronze finishes)
"""

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime

from tasks import (
    silver_check_db_health,
    resolve_latest_batch,
    clean_sales,
    clean_inventory,
    clean_stock_movements,
    validate_silver_quality,
    silver_log_summary,
    default_args
)


with DAG(
    "2-retail_silver_cleaning",
    default_args=default_args,
    start_date=datetime(2025, 11, 1),
    description="Clean and validate Bronze records into Silver layer using Polars",
    schedule="30 * * * *",     # 30 min after Bronze runs
    catchup=False,
    tags=["silver", "cleaning", "retail"],
) as dag:

    db_health = PythonOperator(
        task_id="check_db_health",
        python_callable=silver_check_db_health,
    )

    resolve_batch = PythonOperator(
        task_id="resolve_latest_batch",
        python_callable=resolve_latest_batch,
    )

    clean_sales_task = PythonOperator(
        task_id="clean_sales",
        python_callable=clean_sales,
    )

    clean_inventory_task = PythonOperator(
        task_id="clean_inventory",
        python_callable=clean_inventory,
    )

    clean_movements_task = PythonOperator(
        task_id="clean_stock_movements",
        python_callable=clean_stock_movements,
    )

    quality_gate = PythonOperator(
        task_id="validate_silver_quality",
        python_callable=validate_silver_quality,
    )

    summary = PythonOperator(
        task_id="log_summary",
        python_callable=silver_log_summary,
    )

    db_health >> resolve_batch >> [
        clean_sales_task,
        clean_inventory_task,
        clean_movements_task,
    ] >> quality_gate >> summary

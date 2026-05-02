"""
dags/bronze_ingestion_dag.py

DAG 1 — Bronze Layer Ingestion
Generates synthetic retail data (sales, inventory, stock movements)
and loads raw records into the Bronze PostgreSQL tables.

Schedule: every hour on the hour
"""

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime


from tasks import (
    bronze_check_db_health,
    generate_batch_id_task,
    ingest_sales,
    ingest_inventory,
    ingest_stock_movements,
    bronze_log_summary,
    default_args
)


with DAG(
    "1-retail_bronze_ingestion",
    default_args=default_args,
    start_date=datetime(2026, 5, 1),
    description="Generate synthetic retail data and load into Bronze layer",
    schedule="0 * * * *",      # Every hour on the hour
    catchup=False,
    tags=["bronze", "ingestion", "retail"],
) as dag:

    db_health = PythonOperator(
        task_id="check_db_health",
        python_callable=bronze_check_db_health,
    )

    gen_batch_id = PythonOperator(
        task_id="generate_batch_id",
        python_callable=generate_batch_id_task,
    )

    ingest_sales_task = PythonOperator(
        task_id="ingest_sales",
        python_callable=ingest_sales,
    )

    ingest_inventory_task = PythonOperator(
        task_id="ingest_inventory",
        python_callable=ingest_inventory,
    )

    ingest_movements_task = PythonOperator(
        task_id="ingest_stock_movements",
        python_callable=ingest_stock_movements,
    )

    summary = PythonOperator(
        task_id="log_summary",
        python_callable=bronze_log_summary,
    )

    db_health >> gen_batch_id >> [
        ingest_sales_task,
        ingest_inventory_task,
        ingest_movements_task,
    ] >> summary

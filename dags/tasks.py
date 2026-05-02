from src.utils.db import get_cursor, check_health
from src.utils.batch import generate_batch_id
from src.utils.logger import get_logger

from datetime import datetime


from src.generators.sales_generator import (
    generate_sales_batch,
    records_as_tuples as sales_tuples,
)
from src.generators.inventory_generator import (
    generate_inventory_batch,
    records_as_tuples as inventory_tuples,
)
from src.generators.stock_movement_generator import (
    generate_stock_movement_batch,
    records_as_tuples as movement_tuples,
)
from src.bronze.loader import load_sales, load_inventory, load_stock_movements

from src.silver.clean_sales import clean_sales_batch
from src.silver.clean_inventory import clean_inventory_batch
from src.silver.clean_stock_movement import clean_stock_movement_batch

bronze_logger = get_logger("bronze_ingestion_dag")
silver_logger = get_logger("silver_cleaning_dag")
gold_logger = get_logger("gold_marts_dag")

default_args = {
    "owner": "ikidevz",
}


def bronze_check_db_health(**context):
    ok = check_health()
    if not ok:
        raise RuntimeError(
            "❌ Database health check failed. Aborting Bronze ingestion.")
    bronze_logger.info("✅ DB health check passed")


def generate_batch_id_task(**context):
    batch_id = generate_batch_id(prefix="BRONZE")
    context["ti"].xcom_push(key="batch_id", value=batch_id)
    bronze_logger.info(f"📦 Batch ID created: {batch_id}")


def ingest_sales(**context):
    batch_id = context["ti"].xcom_pull(
        key="batch_id", task_ids="generate_batch_id")
    logical_date = context.get("logical_date", datetime.utcnow())

    records = generate_sales_batch(
        batch_id=batch_id, logical_date=logical_date)
    tuples = sales_tuples(records)
    count = load_sales(tuples)

    context["ti"].xcom_push(key="sales_count", value=count)
    bronze_logger.info(f"📊 Ingested {count} sales records | batch={batch_id}")


def ingest_inventory(**context):
    batch_id = context["ti"].xcom_pull(
        key="batch_id", task_ids="generate_batch_id")
    logical_date = context.get("logical_date", datetime.utcnow())

    records = generate_inventory_batch(
        batch_id=batch_id, logical_date=logical_date)
    tuples = inventory_tuples(records)
    count = load_inventory(tuples)

    context["ti"].xcom_push(key="inventory_count", value=count)
    bronze_logger.info(
        f"📊 Ingested {count} inventory snapshots | batch={batch_id}")


def ingest_stock_movements(**context):
    batch_id = context["ti"].xcom_pull(
        key="batch_id", task_ids="generate_batch_id")
    logical_date = context.get("logical_date", datetime.utcnow())

    records = generate_stock_movement_batch(
        batch_id=batch_id, logical_date=logical_date)
    tuples = movement_tuples(records)
    count = load_stock_movements(tuples)

    context["ti"].xcom_push(key="movement_count", value=count)
    bronze_logger.info(
        f"📊 Ingested {count} stock movement records | batch={batch_id}")


def bronze_log_summary(**context):
    ti = context["ti"]
    batch_id = ti.xcom_pull(
        key="batch_id",        task_ids="generate_batch_id")
    sales = ti.xcom_pull(key="sales_count",      task_ids="ingest_sales")
    inventory = ti.xcom_pull(key="inventory_count",
                             task_ids="ingest_inventory")
    movements = ti.xcom_pull(key="movement_count",
                             task_ids="ingest_stock_movements")

    bronze_logger.info("=" * 50)
    bronze_logger.info("📋 BRONZE INGESTION SUMMARY")
    bronze_logger.info(f"   Batch ID      : {batch_id}")
    bronze_logger.info(f"   Sales rows    : {sales}")
    bronze_logger.info(f"   Inventory rows: {inventory}")
    bronze_logger.info(f"   Movement rows : {movements}")
    bronze_logger.info(
        f"   Total rows    : {(sales or 0) + (inventory or 0) + (movements or 0)}")
    bronze_logger.info("=" * 50)


def silver_check_db_health(**context):
    ok = check_health()
    if not ok:
        raise RuntimeError(
            "❌ DB health check failed. Aborting Silver cleaning.")


def resolve_latest_batch(**context):
    """
    Finds the most recent batch_id from Bronze that has NOT yet been
    written to Silver. Pushes the batch_id to XCom.
    """
    sql = """
        SELECT DISTINCT b.batch_id
        FROM bronze_sales_raw b
        WHERE NOT EXISTS (
            SELECT 1 FROM silver_sales_cleaned s
            WHERE s.batch_id = b.batch_id
        )
        ORDER BY b.batch_id DESC
        LIMIT 1
    """
    with get_cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()

    if not row:
        silver_logger.warning(
            "⚠️  No unprocessed Bronze batches found — skipping Silver run.")
        context["ti"].xcom_push(key="batch_id", value=None)
        return

    batch_id = row["batch_id"]
    silver_logger.info(f"🎯 Resolved batch to clean: {batch_id}")
    context["ti"].xcom_push(key="batch_id", value=batch_id)


def clean_sales(**context):
    batch_id = context["ti"].xcom_pull(
        key="batch_id", task_ids="resolve_latest_batch")
    if not batch_id:
        silver_logger.info("No batch to process — skipping sales cleaning.")
        return
    result = clean_sales_batch(batch_id)
    context["ti"].xcom_push(key="sales_result", value=result)


def clean_inventory(**context):
    batch_id = context["ti"].xcom_pull(
        key="batch_id", task_ids="resolve_latest_batch")
    if not batch_id:
        silver_logger.info(
            "No batch to process — skipping inventory cleaning.")
        return
    result = clean_inventory_batch(batch_id)
    context["ti"].xcom_push(key="inventory_result", value=result)


def clean_stock_movements(**context):
    batch_id = context["ti"].xcom_pull(
        key="batch_id", task_ids="resolve_latest_batch")
    if not batch_id:
        silver_logger.info(
            "No batch to process — skipping stock movement cleaning.")
        return
    result = clean_stock_movement_batch(batch_id)
    context["ti"].xcom_push(key="movement_result", value=result)


def validate_silver_quality(**context):
    """
    Post-clean quality gate: checks invalid rate across all three datasets.
    Raises if invalid rate > 5% on any table.
    """
    ti = context["ti"]
    batch_id = ti.xcom_pull(
        key="batch_id",        task_ids="resolve_latest_batch")
    sales_result = ti.xcom_pull(key="sales_result",    task_ids="clean_sales")
    inv_result = ti.xcom_pull(key="inventory_result",
                              task_ids="clean_inventory")
    movement_result = ti.xcom_pull(
        key="movement_result", task_ids="clean_stock_movements")

    if not batch_id:
        silver_logger.info("No batch processed — skipping quality gate.")
        return

    THRESHOLD = 0.05  # 5% max invalid rate

    for name, result in [
        ("sales", sales_result),
        ("inventory", inv_result),
        ("stock_movements", movement_result),
    ]:
        if not result or result["total"] == 0:
            continue
        invalid_rate = result["invalid"] / result["total"]
        silver_logger.info(
            f"   {name}: total={result['total']} | valid={result['valid']} "
            f"| invalid={result['invalid']} | rate={invalid_rate:.1%}"
        )
        if invalid_rate > THRESHOLD:
            raise ValueError(
                f"❌ Silver quality gate FAILED for {name}: "
                f"invalid rate {invalid_rate:.1%} exceeds threshold {THRESHOLD:.0%}"
            )

    silver_logger.info("✅ Silver quality gate passed for all tables")


def silver_log_summary(**context):
    ti = context["ti"]
    batch_id = ti.xcom_pull(
        key="batch_id",        task_ids="resolve_latest_batch")
    sales_result = ti.xcom_pull(key="sales_result",    task_ids="clean_sales")
    inv_result = ti.xcom_pull(key="inventory_result",
                              task_ids="clean_inventory")
    movement_result = ti.xcom_pull(
        key="movement_result", task_ids="clean_stock_movements")

    silver_logger.info("=" * 55)
    silver_logger.info("📋 SILVER CLEANING SUMMARY")
    silver_logger.info(f"   Batch ID : {batch_id or 'N/A'}")
    for name, r in [("Sales", sales_result), ("Inventory", inv_result), ("Stock Mvmt", movement_result)]:
        if r:
            silver_logger.info(
                f"   {name:<12}: total={r['total']:>5} | valid={r['valid']:>5} | invalid={r['invalid']:>4}"
            )
    silver_logger.info("=" * 55)


def validate_gold_layer(**context):

    checks = {
        "gold_dim_date":             "SELECT COUNT(*) AS cnt FROM gold_dim_date",
        "gold_dim_product":          "SELECT COUNT(*) AS cnt FROM gold_dim_product",
        "gold_dim_store":            "SELECT COUNT(*) AS cnt FROM gold_dim_store",
        "gold_fact_sales":           "SELECT COUNT(*) AS cnt FROM gold_fact_sales WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INT",
        "gold_fact_inventory_snap":  "SELECT COUNT(*) AS cnt FROM gold_fact_inventory_snapshot WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INT",
        "gold_fact_stock_movement":  "SELECT COUNT(*) AS cnt FROM gold_fact_stock_movement WHERE date_key = TO_CHAR(CURRENT_DATE - 1, 'YYYYMMDD')::INT",
    }

    failed = []
    with get_cursor() as cur:
        for table, sql in checks.items():
            cur.execute(sql)
            row = cur.fetchone()
            cnt = row["cnt"]
            gold_logger.info(f"   {table:<35}: {cnt} rows")
            if "fact" in table and cnt == 0:
                failed.append(table)

    if failed:
        raise ValueError(
            f"❌ Gold validation failed — empty fact tables: {failed}")

    gold_logger.info("✅ Gold layer validation passed")

"""
silver/clean_inventory.py

Cleans Bronze inventory snapshots using Polars and writes to Silver.
"""

import polars as pl
from src.utils.db import get_connection, execute_many
from src.utils.logger import get_logger

logger = get_logger(__name__)

_FETCH_SQL = """
    SELECT ingestion_timestamp, batch_id, snapshot_ts,
           product_id, store_id, stock_level, reorder_point, source_system
    FROM bronze.inventory_raw
    WHERE batch_id = %s
"""

_INSERT_SQL = """
    INSERT INTO silver.inventory_cleaned (
        ingestion_timestamp, batch_id, snapshot_ts,
        product_id, store_id, stock_level, reorder_point,
        is_valid, error_reason
    ) VALUES %s
"""


def clean_inventory_batch(batch_id: str) -> dict:
    logger.info(f"🔄 Cleaning inventory batch: {batch_id}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_FETCH_SQL, (batch_id,))
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

    if not rows:
        logger.warning(f"No Bronze inventory records for batch {batch_id}")
        return {"batch_id": batch_id, "total": 0, "valid": 0, "invalid": 0}

    df = pl.DataFrame(rows, schema=cols, orient="row")

    df = df.with_columns([
        pl.col("stock_level").cast(pl.Int32),
        pl.col("reorder_point").cast(pl.Int32),
    ])

    error_expr = (
        pl.when(pl.col("stock_level") < 0).then(pl.lit("stock_level < 0"))
        .when(pl.col("reorder_point") < 0).then(pl.lit("reorder_point < 0"))
        .when(pl.col("product_id").is_null()).then(pl.lit("null product_id"))
        .when(pl.col("store_id").is_null()).then(pl.lit("null store_id"))
        .otherwise(pl.lit(None).cast(pl.Utf8))
        .alias("error_reason")
    )

    df = df.with_columns([
        error_expr,
        (error_expr.is_null()).alias("is_valid"),
    ])

    records = [
        (
            r["ingestion_timestamp"], r["batch_id"], r["snapshot_ts"],
            r["product_id"], r["store_id"], r["stock_level"],
            r["reorder_point"], r["is_valid"], r["error_reason"],
        )
        for r in df.to_dicts()
    ]

    execute_many(_INSERT_SQL, records)

    valid = df.filter(pl.col("is_valid")).height
    invalid = df.filter(~pl.col("is_valid")).height
    logger.info(
        f"✅ Inventory cleaned | total={len(records)} | valid={valid} | invalid={invalid}")
    return {"batch_id": batch_id, "total": len(records), "valid": valid, "invalid": invalid}

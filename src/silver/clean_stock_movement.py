"""
silver/clean_stock_movement.py

Cleans Bronze stock movement records using Polars and writes to Silver.
"""

import polars as pl
from src.utils.db import get_connection, execute_many
from src.utils.logger import get_logger

logger = get_logger(__name__)

VALID_MOVEMENT_TYPES = {"PURCHASE", "SALE", "RETURN", "ADJUSTMENT", "TRANSFER"}

_FETCH_SQL = """
    SELECT ingestion_timestamp, batch_id, movement_ts,
           product_id, store_id, supplier_id, movement_type,
           quantity, reason, reference_id
    FROM bronze.stock_movement_raw
    WHERE batch_id = %s
"""

_INSERT_SQL = """
    INSERT INTO silver.stock_movement_cleaned (
        ingestion_timestamp, batch_id, movement_ts,
        product_id, store_id, supplier_id, movement_type,
        quantity, reason, reference_id,
        is_valid, error_reason
    ) VALUES %s
"""


def clean_stock_movement_batch(batch_id: str) -> dict:
    logger.info(f"🔄 Cleaning stock movement batch: {batch_id}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_FETCH_SQL, (batch_id,))
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

    if not rows:
        logger.warning(
            f"No Bronze stock movement records for batch {batch_id}")
        return {"batch_id": batch_id, "total": 0, "valid": 0, "invalid": 0}

    df = pl.DataFrame(rows, schema=cols, orient="row")

    df = df.with_columns(pl.col("quantity").cast(pl.Int32))

    valid_types = list(VALID_MOVEMENT_TYPES)

    error_expr = (
        pl.when(pl.col("quantity") <= 0).then(pl.lit("quantity <= 0"))
        .when(~pl.col("movement_type").is_in(valid_types)).then(pl.lit("invalid movement_type"))
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
            r["ingestion_timestamp"], r["batch_id"], r["movement_ts"],
            r["product_id"], r["store_id"], r["supplier_id"],
            r["movement_type"], r["quantity"], r["reason"],
            r["reference_id"], r["is_valid"], r["error_reason"],
        )
        for r in df.to_dicts()
    ]

    execute_many(_INSERT_SQL, records)

    valid = df.filter(pl.col("is_valid")).height
    invalid = df.filter(~pl.col("is_valid")).height
    logger.info(
        f"✅ Stock movement cleaned | total={len(records)} | valid={valid} | invalid={invalid}")
    return {"batch_id": batch_id, "total": len(records), "valid": valid, "invalid": invalid}

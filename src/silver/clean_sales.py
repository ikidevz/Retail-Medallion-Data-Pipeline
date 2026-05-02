"""
silver/clean_sales.py

Reads unprocessed Bronze sales records for a given batch_id,
applies Polars-based cleaning / validation, and upserts to Silver.
"""

import polars as pl

from src.utils.db import get_connection, execute_many
from src.utils.logger import get_logger

logger = get_logger(__name__)

_FETCH_SQL = """
    SELECT
        raw_id,
        ingestion_timestamp,
        batch_id,
        transaction_id,
        sale_ts,
        product_id,
        store_id,
        quantity,
        amount,
        discount_amount,
        payment_method,
        source_system
    FROM bronze.sales_raw
    WHERE batch_id = %s
"""

_INSERT_SQL = """
    INSERT INTO silver.sales_cleaned (
        ingestion_timestamp, batch_id, transaction_id, sale_ts,
        product_id, store_id, quantity, amount,
        discount_amount, net_amount, payment_method,
        is_valid, error_reason
    ) VALUES %s
    ON CONFLICT (transaction_id) DO NOTHING
"""


def _validate(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add is_valid and error_reason columns based on business rules.
    Rules:
        - quantity must be > 0
        - amount must be > 0
        - discount_amount must be >= 0 and <= amount
        - transaction_id must not be null
        - sale_ts must not be null
    """
    df = df.with_columns([
        pl.lit(True).alias("is_valid"),
        pl.lit(None).cast(pl.Utf8).alias("error_reason"),
    ])

    # Build error messages per row
    errors = (
        pl.when(pl.col("quantity") <= 0).then(pl.lit("quantity <= 0"))
        .when(pl.col("amount") <= 0).then(pl.lit("amount <= 0"))
        .when(pl.col("discount_amount") < 0).then(pl.lit("discount_amount < 0"))
        .when(pl.col("discount_amount") > pl.col("amount")).then(pl.lit("discount > amount"))
        .when(pl.col("transaction_id").is_null()).then(pl.lit("null transaction_id"))
        .when(pl.col("sale_ts").is_null()).then(pl.lit("null sale_ts"))
        .otherwise(pl.lit(None).cast(pl.Utf8))
        .alias("error_reason")
    )

    df = df.with_columns([
        errors,
        (errors.is_null()).alias("is_valid"),
    ])
    return df


def clean_sales_batch(batch_id: str) -> dict:
    """
    Full clean pipeline for a single batch.
    Returns a summary dict with counts.
    """
    logger.info(f"🔄 Cleaning sales batch: {batch_id}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_FETCH_SQL, (batch_id,))
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

    if not rows:
        logger.warning(f"No Bronze sales records found for batch {batch_id}")
        return {"batch_id": batch_id, "total": 0, "valid": 0, "invalid": 0}

    df = pl.DataFrame(rows, schema=cols, orient="row")

    # Cast types
    df = df.with_columns([
        pl.col("quantity").cast(pl.Int32),
        pl.col("amount").cast(pl.Float64),
        pl.col("discount_amount").cast(pl.Float64),
    ])

    df = _validate(df)

    # Compute net_amount
    df = df.with_columns(
        (pl.col("amount") - pl.col("discount_amount")).alias("net_amount")
    )

    # Build tuples for insert
    records = [
        (
            row["ingestion_timestamp"],
            row["batch_id"],
            row["transaction_id"],
            row["sale_ts"],
            row["product_id"],
            row["store_id"],
            row["quantity"],
            row["amount"],
            row["discount_amount"],
            row["net_amount"],
            row["payment_method"],
            row["is_valid"],
            row["error_reason"],
        )
        for row in df.to_dicts()
    ]

    execute_many(_INSERT_SQL, records)

    valid_count = df.filter(pl.col("is_valid")).height
    invalid_count = df.filter(~pl.col("is_valid")).height

    logger.info(
        f"✅ Sales cleaned | total={len(records)} | valid={valid_count} | invalid={invalid_count}"
    )
    return {
        "batch_id": batch_id,
        "total": len(records),
        "valid": valid_count,
        "invalid": invalid_count,
    }

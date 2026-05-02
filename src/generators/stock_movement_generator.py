"""
generators/stock_movement_generator.py

Generates synthetic stock movement records (purchases, sales, returns, adjustments,
transfers). Produces 80–150 records per batch by default.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

STORES = [f"STR-{i:03d}" for i in range(1, 51)]
PRODUCTS = [f"PRD-{i:04d}" for i in range(1, 501)]
SUPPLIERS = [f"SUP-{i:03d}" for i in range(1, 31)]       # 30 suppliers

MOVEMENT_TYPES = ["PURCHASE", "SALE", "RETURN", "ADJUSTMENT", "TRANSFER"]

# Realistic distribution — SALE dominates
MOVEMENT_WEIGHTS = [20, 50, 10, 10, 10]

ADJUSTMENT_REASONS = [
    "Shrinkage", "Damaged goods", "Cycle count correction",
    "Promotional give-away", "Write-off", "Found stock",
]

RETURN_REASONS = [
    "Defective item", "Wrong item delivered",
    "Customer changed mind", "Expired product",
]


def _movement_qty(movement_type: str) -> int:
    if movement_type == "PURCHASE":
        return random.randint(10, 200)
    elif movement_type == "SALE":
        return random.randint(1, 10)
    elif movement_type in ("RETURN", "ADJUSTMENT"):
        return random.randint(1, 20)
    else:  # TRANSFER
        return random.randint(5, 50)


def _reason(movement_type: str) -> Optional[str]:
    if movement_type == "ADJUSTMENT":
        return random.choice(ADJUSTMENT_REASONS)
    if movement_type == "RETURN":
        return random.choice(RETURN_REASONS)
    return None


def generate_stock_movement_batch(
    batch_id: str,
    logical_date: Optional[datetime] = None,
    n_records: Optional[int] = None,
) -> list[dict]:
    """
    Return a list of stock movement dicts for Bronze insertion.

    Parameters
    ----------
    batch_id     : Unique identifier for this ingestion run.
    logical_date : Reference datetime. Defaults to utcnow().
    n_records    : Records to generate. Defaults to random 80–150.
    """
    if logical_date is None:
        logical_date = datetime.utcnow()
    if n_records is None:
        n_records = random.randint(80, 150)

    records = []
    for _ in range(n_records):
        jitter = random.randint(0, 3599)
        movement_ts = logical_date.replace(
            minute=0, second=0, microsecond=0
        ) + timedelta(seconds=jitter)

        movement_type = random.choices(MOVEMENT_TYPES, weights=MOVEMENT_WEIGHTS, k=1)[0]

        # Supplier only makes sense for PURCHASE movements
        supplier_id = random.choice(SUPPLIERS) if movement_type == "PURCHASE" else None

        records.append({
            "batch_id":      batch_id,
            "movement_ts":   movement_ts.isoformat(),
            "product_id":    random.choice(PRODUCTS),
            "store_id":      random.choice(STORES),
            "supplier_id":   supplier_id,
            "movement_type": movement_type,
            "quantity":      _movement_qty(movement_type),
            "reason":        _reason(movement_type),
            "reference_id":  f"REF-{uuid.uuid4().hex[:12].upper()}",
        })

    return records


def records_as_tuples(records: list[dict]) -> list[tuple]:
    return [
        (
            r["batch_id"],
            r["movement_ts"],
            r["product_id"],
            r["store_id"],
            r["supplier_id"],
            r["movement_type"],
            r["quantity"],
            r["reason"],
            r["reference_id"],
        )
        for r in records
    ]

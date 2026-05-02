"""
generators/inventory_generator.py

Generates synthetic inventory snapshots: one record per (product × store) sample.
Produces ~50 snapshots per batch (a random 10% sample of the 500-product catalog
across all 50 stores avoids overwhelming the DB with 25,000 rows per hour).
"""

import random
from datetime import datetime
from typing import Optional

STORES = [f"STR-{i:03d}" for i in range(1, 51)]
PRODUCTS = [f"PRD-{i:04d}" for i in range(1, 501)]


def generate_inventory_batch(
    batch_id: str,
    logical_date: Optional[datetime] = None,
    n_records: Optional[int] = None,
) -> list[dict]:
    """
    Return a list of inventory snapshot dicts for Bronze insertion.

    Parameters
    ----------
    batch_id     : Unique identifier for this ingestion run.
    logical_date : Snapshot timestamp. Defaults to utcnow().
    n_records    : Records to generate. Defaults to random 40–80.
    """
    if logical_date is None:
        logical_date = datetime.utcnow()
    if n_records is None:
        n_records = random.randint(40, 80)

    snapshot_ts = logical_date.replace(minute=0, second=0, microsecond=0)

    # Sample unique (store, product) pairs
    pairs = random.sample(
        [(s, p) for s in STORES for p in PRODUCTS],
        k=min(n_records, len(STORES) * len(PRODUCTS)),
    )

    records = []
    for store_id, product_id in pairs[:n_records]:
        stock_level = random.randint(0, 500)
        # Reorder point is typically 10–20 % of max expected stock
        reorder_point = random.randint(10, 60)
        records.append({
            "batch_id":      batch_id,
            "snapshot_ts":   snapshot_ts.isoformat(),
            "product_id":    product_id,
            "store_id":      store_id,
            "stock_level":   stock_level,
            "reorder_point": reorder_point,
            "source_system": "WMS_v3",
        })

    return records


def records_as_tuples(records: list[dict]) -> list[tuple]:
    return [
        (
            r["batch_id"],
            r["snapshot_ts"],
            r["product_id"],
            r["store_id"],
            r["stock_level"],
            r["reorder_point"],
            r["source_system"],
        )
        for r in records
    ]

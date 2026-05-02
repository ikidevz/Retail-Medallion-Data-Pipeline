"""
generators/sales_generator.py

Generates realistic synthetic sales transactions for Philippine retail stores.
Produces between 200–500 records per batch by default.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Generator

# ── Philippine Retail Reference Data ────────────────────────────────────────

STORES = [f"STR-{i:03d}" for i in range(1, 51)]          # 50 stores

PRODUCTS = [f"PRD-{i:04d}" for i in range(1, 501)]        # 500 SKUs

PAYMENT_METHODS = [
    "CASH", "GCASH", "MAYA", "CREDIT_CARD",
    "DEBIT_CARD", "INSTALLMENT", "POINTS_REDEMPTION",
]

PAYMENT_WEIGHTS = [35, 25, 15, 12, 8, 3, 2]               # % share each

SOURCE_SYSTEMS = ["POS_V2", "MOBILE_APP", "KIOSK", "WEB"]

# Price bands per product segment (₱ amounts)
AMOUNT_BANDS = [
    (50,   500),    # fast-moving consumer goods
    (500,  2_000),  # personal care / household
    (2_000, 8_000), # electronics accessories
    (8_000, 50_000),# appliances / gadgets
]

BAND_WEIGHTS = [55, 25, 15, 5]


def _random_amount() -> float:
    band = random.choices(AMOUNT_BANDS, weights=BAND_WEIGHTS, k=1)[0]
    raw = random.uniform(*band)
    # Philippine retail: round to nearest 0.25
    return round(raw * 4) / 4


def _random_discount(amount: float) -> float:
    """10 % chance of a discount; discount is 5–30 % of the gross."""
    if random.random() < 0.10:
        pct = random.uniform(0.05, 0.30)
        return round(amount * pct, 2)
    return 0.0


def generate_sales_batch(
    batch_id: str,
    logical_date: datetime | None = None,
    n_records: int | None = None,
) -> list[dict]:
    """
    Return a list of raw sales dictionaries ready for Bronze insertion.

    Parameters
    ----------
    batch_id    : Unique identifier for this ingestion run.
    logical_date: The business date to generate records for.
                  Defaults to utcnow().
    n_records   : Number of records to generate.
                  If None, randomly picks 200–500.
    """
    if logical_date is None:
        logical_date = datetime.utcnow()
    if n_records is None:
        n_records = random.randint(200, 500)

    records: list[dict] = []

    for _ in range(n_records):
        # Scatter transactions across the hour
        jitter_seconds = random.randint(0, 3599)
        sale_ts = logical_date.replace(
            minute=0, second=0, microsecond=0
        ) + timedelta(seconds=jitter_seconds)

        amount = _random_amount()
        discount = _random_discount(amount)
        qty = random.randint(1, 6)

        records.append({
            "batch_id":       batch_id,
            "transaction_id": f"TXN-{uuid.uuid4().hex[:16].upper()}",
            "sale_ts":        sale_ts.isoformat(),
            "product_id":     random.choice(PRODUCTS),
            "store_id":       random.choice(STORES),
            "quantity":       qty,
            "amount":         amount,
            "discount_amount": discount,
            "payment_method": random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS, k=1)[0],
            "source_system":  random.choice(SOURCE_SYSTEMS),
        })

    return records


def records_as_tuples(records: list[dict]) -> list[tuple]:
    """Convert dicts to ordered tuples for executemany insert."""
    return [
        (
            r["batch_id"],
            r["transaction_id"],
            r["sale_ts"],
            r["product_id"],
            r["store_id"],
            r["quantity"],
            r["amount"],
            r["discount_amount"],
            r["payment_method"],
            r["source_system"],
        )
        for r in records
    ]

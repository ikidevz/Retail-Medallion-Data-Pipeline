"""
bronze/loader.py

Handles bulk insertion of generated records into the Bronze layer tables.
Each function is idempotent on batch_id (duplicate batch IDs simply append
new rows; the Bronze layer is append-only by design).
"""

from src.utils.db import execute_many
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── INSERT statements ────────────────────────────────────────────────────────

_SQL_SALES = """
    INSERT INTO bronze.sales_raw (
        batch_id, transaction_id, sale_ts,
        product_id, store_id, quantity,
        amount, discount_amount, payment_method, source_system
    ) VALUES %s
"""

_SQL_INVENTORY = """
    INSERT INTO bronze.inventory_raw (
        batch_id, snapshot_ts, product_id,
        store_id, stock_level, reorder_point, source_system
    ) VALUES %s
"""

_SQL_STOCK_MOVEMENT = """
    INSERT INTO bronze.stock_movement_raw (
        batch_id, movement_ts, product_id,
        store_id, supplier_id, movement_type,
        quantity, reason, reference_id
    ) VALUES %s
"""


def load_sales(records: list[tuple]) -> int:
    if not records:
        logger.warning("No sales records to load.")
        return 0
    count = execute_many(_SQL_SALES, records)
    logger.info(f"✅ Loaded {count} rows → bronze_sales_raw")
    return count


def load_inventory(records: list[tuple]) -> int:
    if not records:
        logger.warning("No inventory records to load.")
        return 0
    count = execute_many(_SQL_INVENTORY, records)
    logger.info(f"✅ Loaded {count} rows → bronze_inventory_raw")
    return count


def load_stock_movements(records: list[tuple]) -> int:
    if not records:
        logger.warning("No stock movement records to load.")
        return 0
    count = execute_many(_SQL_STOCK_MOVEMENT, records)
    logger.info(f"✅ Loaded {count} rows → bronze_stock_movement_raw")
    return count

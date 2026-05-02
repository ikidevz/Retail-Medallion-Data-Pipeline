import uuid
from datetime import datetime, UTC


def generate_batch_id(prefix: str = "BATCH") -> str:
    """
    Generate a unique batch ID.
    Format: BATCH-20251101T143000-a1b2c3d4
    """
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    short_uuid = str(uuid.uuid4()).split("-")[0]
    return f"{prefix}-{timestamp}-{short_uuid}"

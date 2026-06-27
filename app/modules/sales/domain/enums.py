"""Sales module domain — enums."""
from __future__ import annotations

from enum import StrEnum


class BatchStatus(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"

"""Forecasting module domain — enums."""
from __future__ import annotations

from enum import StrEnum


class RunStatus(StrEnum):
    """Status of a forecast run.

    Aligned with JobStatus from shared infrastructure ports but kept as a
    separate domain enum since the domain should not depend on infrastructure.
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

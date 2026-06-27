"""Data preparation module domain — value objects."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SeriesPoint:
    """A single data point in a prepared time series."""

    period_date: date
    demand: Decimal
    is_stockout: bool = False

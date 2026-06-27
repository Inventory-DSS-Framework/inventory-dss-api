"""Forecasting module domain — value objects."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ForecastPoint:
    """A single forecasted demand point."""

    period_date: date
    predicted_demand: Decimal
    lower_bound: Decimal | None = None
    upper_bound: Decimal | None = None

"""Forecasting module — application ports.

The FTGM Engine is an external service. The application depends on this port; the
concrete HTTP adapter lives in infrastructure/adapters.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.modules.data_preparation.domain.entities import PreparedTimeSeries
from app.modules.forecasting.domain.value_objects import ForecastPoint


@dataclass
class ProductForecast:
    """Forecast + accuracy metrics for a single product, as returned by the engine."""

    product_id: UUID
    points: list[ForecastPoint]
    mape: Decimal
    mae: Decimal
    rmse: Decimal


class ForecastEnginePort(Protocol):
    """Port for the external FTGM forecasting engine."""

    def forecast(
        self,
        *,
        series: list[PreparedTimeSeries],
        horizon_days: int,
        model_name: str,
    ) -> list[ProductForecast]: ...

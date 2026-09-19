"""Forecasting module — application ports.

The FTGM Engine is an external service. The application depends on this port; the
concrete HTTP adapter lives in infrastructure/adapters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Protocol
from uuid import UUID

from app.modules.data_preparation.domain.entities import PreparedTimeSeries
from app.modules.forecasting.domain.value_objects import ForecastPoint, HistoryPoint


@dataclass
class ProductForecast:
    """Forecast + accuracy metrics for a single product, as returned by the engine.

    Carries the full engine output: point forecast with interval, in-sample history
    (observed/cleaned/fitted), scaled metrics (MASE/RMSSE), the Fourier order chosen
    by Algorithm 1, which model actually ran, per-product status/reason, and the
    diagnostics (frequency decision, cleaning, hold-out validation, explanations).
    """

    product_id: UUID
    points: list[ForecastPoint]
    mape: Decimal
    mae: Decimal
    rmse: Decimal
    mase: Decimal | None = None
    rmsse: Decimal | None = None
    history: list[HistoryPoint] = field(default_factory=list)
    order_selected: int = 0
    model_used: str = ""
    status: str = "ok"
    fallback_reason: str | None = None
    validation_rmse: Decimal | None = None
    frequency: str | None = None
    period: int | None = None
    warnings: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)


class ForecastEnginePort(Protocol):
    """Port for the external FTGM forecasting engine."""

    def forecast(
        self,
        *,
        series: list[PreparedTimeSeries],
        horizon_days: int,
        model_name: str,
        frequency: str | None = None,
        as_of: date | None = None,
    ) -> list[ProductForecast]: ...

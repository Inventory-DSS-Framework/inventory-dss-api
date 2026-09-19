"""FTGM Engine HTTP adapter (implements ForecastEnginePort).

Sends prepared series to the external FTGM Engine and parses its response. Network
or protocol failures propagate as exceptions so the calling use case can mark the run
as failed.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

import math

import httpx

from app.config import settings
from app.modules.data_preparation.domain.entities import PreparedTimeSeries
from app.modules.forecasting.application.ports import ProductForecast
from app.modules.forecasting.domain.value_objects import ForecastPoint, HistoryPoint

# Approximate calendar length of one seasonal period, used to convert a horizon
# expressed in days into the number of periods the engine forecasts (legacy contract).
_DAYS_PER_PERIOD = {12: 30, 4: 91, 52: 7}


class FtgmHttpAdapter:
    """Calls POST {ftgm_engine_base_url}/forecast.

    Two contracts:

    * **frequency-aware** (``frequency`` given, used by ERP-scoped runs): sends
      ``frequency`` (auto/monthly/weekly), ``horizon_days`` and the ``as_of`` cut-off; the
      engine picks the bucket size per product and drops the period in progress.
    * **legacy** (CSV datasets): a fixed seasonal ``period`` and ``horizon`` in periods.

    Each series carries the stock-out flag so the engine can repair censored demand.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        period: int | None = None,
    ) -> None:
        self._base_url = (base_url or settings.ftgm_engine_base_url).rstrip("/")
        # Rolling-origin validation re-fits the model several times per product.
        self._timeout = max(timeout or float(settings.ftgm_engine_timeout_seconds), 180.0)
        self._period = period or settings.ftgm_seasonal_period

    def forecast(
        self,
        *,
        series: list[PreparedTimeSeries],
        horizon_days: int,
        model_name: str,
        frequency: str | None = None,
        as_of: date | None = None,
    ) -> list[ProductForecast]:
        payload: dict[str, Any] = {
            "model": model_name,
            "period": self._period,
            "series": [
                {
                    "product_id": str(s.product_id),
                    "points": [
                        {
                            "date": p.period_date.isoformat(),
                            "demand": str(p.demand),
                            "stockout_flag": p.is_stockout,
                        }
                        for p in s.points
                    ],
                }
                for s in series
            ],
        }
        if frequency:
            payload["frequency"] = frequency
            payload["horizon_days"] = horizon_days
            if as_of is not None:
                payload["as_of"] = as_of.isoformat()
        else:
            payload["horizon"] = self._days_to_periods(horizon_days)

        response = httpx.post(f"{self._base_url}/forecast", json=payload, timeout=self._timeout)
        response.raise_for_status()
        return [self._parse(item) for item in response.json().get("forecasts", [])]

    def _days_to_periods(self, horizon_days: int) -> int:
        """Convert a day horizon into a (rounded up) number of seasonal periods."""
        days_per_period = _DAYS_PER_PERIOD.get(self._period, 30)
        return max(1, math.ceil(horizon_days / days_per_period))

    @staticmethod
    def _metric(metrics: dict[str, Any], key: str) -> Decimal:
        """Read a metric, treating a missing or null value as 0."""
        value = metrics.get(key)
        return Decimal(str(value)) if value is not None else Decimal("0")

    @staticmethod
    def _optional_metric(metrics: dict[str, Any], key: str) -> Decimal | None:
        """Read a metric that may legitimately be absent (e.g. undefined MASE)."""
        value = metrics.get(key)
        return Decimal(str(value)) if value is not None else None

    @staticmethod
    def _optional_decimal(value: Any) -> Decimal | None:
        return Decimal(str(value)) if value is not None else None

    @staticmethod
    def _parse(item: dict[str, Any]) -> ProductForecast:
        metrics = item.get("metrics", {})
        diagnostics = item.get("diagnostics") or {}
        return ProductForecast(
            product_id=UUID(str(item["product_id"])),
            points=[
                ForecastPoint(
                    period_date=date.fromisoformat(str(p["date"])),
                    predicted_demand=Decimal(str(p["predicted_demand"])),
                    lower_bound=(
                        Decimal(str(p["lower_bound"])) if p.get("lower_bound") is not None else None
                    ),
                    upper_bound=(
                        Decimal(str(p["upper_bound"])) if p.get("upper_bound") is not None else None
                    ),
                )
                for p in item.get("points", [])
            ],
            history=[
                HistoryPoint(
                    period_date=date.fromisoformat(str(h["date"])),
                    observed=Decimal(str(h["observed"])),
                    cleaned=Decimal(str(h["cleaned"])),
                    fitted=FtgmHttpAdapter._optional_decimal(h.get("fitted")),
                    is_stockout=bool(h.get("is_stockout", False)),
                    is_outlier=bool(h.get("is_outlier", False)),
                )
                for h in item.get("history", [])
            ],
            mape=FtgmHttpAdapter._metric(metrics, "mape"),
            mae=FtgmHttpAdapter._metric(metrics, "mae"),
            rmse=FtgmHttpAdapter._metric(metrics, "rmse"),
            mase=FtgmHttpAdapter._optional_metric(metrics, "mase"),
            rmsse=FtgmHttpAdapter._optional_metric(metrics, "rmsse"),
            order_selected=int(item.get("order_selected", 0)),
            model_used=str(item.get("model", "")),
            status=str(item.get("status", "ok")),
            fallback_reason=(str(item["fallback_reason"])[:500] if item.get("fallback_reason") else None),
            validation_rmse=FtgmHttpAdapter._optional_decimal(diagnostics.get("validation_rmse")),
            frequency=item.get("frequency"),
            period=item.get("period"),
            warnings=list(item.get("warnings") or []),
            diagnostics=diagnostics,
        )

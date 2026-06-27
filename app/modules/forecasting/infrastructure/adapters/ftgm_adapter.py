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

import httpx

from app.config import settings
from app.modules.data_preparation.domain.entities import PreparedTimeSeries
from app.modules.forecasting.application.ports import ProductForecast
from app.modules.forecasting.domain.value_objects import ForecastPoint


class FtgmHttpAdapter:
    """Calls POST {ftgm_engine_base_url}/forecast."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self._base_url = (base_url or settings.ftgm_engine_base_url).rstrip("/")
        self._timeout = timeout or float(settings.ftgm_engine_timeout_seconds)

    def forecast(
        self,
        *,
        series: list[PreparedTimeSeries],
        horizon_days: int,
        model_name: str,
    ) -> list[ProductForecast]:
        payload = {
            "model": model_name,
            "horizon_days": horizon_days,
            "series": [
                {
                    "product_id": str(s.product_id),
                    "points": [
                        {"date": p.period_date.isoformat(), "demand": str(p.demand)}
                        for p in s.points
                    ],
                }
                for s in series
            ],
        }
        response = httpx.post(
            f"{self._base_url}/forecast", json=payload, timeout=self._timeout
        )
        response.raise_for_status()
        return [self._parse(item) for item in response.json().get("forecasts", [])]

    @staticmethod
    def _parse(item: dict[str, Any]) -> ProductForecast:
        metrics = item.get("metrics", {})
        return ProductForecast(
            product_id=UUID(str(item["product_id"])),
            points=[
                ForecastPoint(
                    period_date=date.fromisoformat(str(p["date"])),
                    predicted_demand=Decimal(str(p["predicted_demand"])),
                    lower_bound=(
                        Decimal(str(p["lower_bound"]))
                        if p.get("lower_bound") is not None
                        else None
                    ),
                    upper_bound=(
                        Decimal(str(p["upper_bound"]))
                        if p.get("upper_bound") is not None
                        else None
                    ),
                )
                for p in item.get("points", [])
            ],
            mape=Decimal(str(metrics.get("mape", "0"))),
            mae=Decimal(str(metrics.get("mae", "0"))),
            rmse=Decimal(str(metrics.get("rmse", "0"))),
        )

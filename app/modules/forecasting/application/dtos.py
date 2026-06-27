"""Forecasting module — application output DTOs."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.modules.forecasting.domain.entities import (
    ForecastMetrics,
    ForecastResult,
    ForecastRun,
)


class ForecastRunDTO(BaseModel):
    id: UUID
    company_id: UUID
    dataset_id: UUID | None
    model_name: str
    horizon_days: int
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_entity(cls, run: ForecastRun) -> ForecastRunDTO:
        assert run.id is not None
        return cls(
            id=run.id,
            company_id=run.company_id,
            dataset_id=run.dataset_id,
            model_name=run.model_name,
            horizon_days=run.horizon_days,
            status=run.status.value,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class ForecastPointDTO(BaseModel):
    period_date: date
    predicted_demand: Decimal
    lower_bound: Decimal | None
    upper_bound: Decimal | None


class ForecastResultDTO(BaseModel):
    id: UUID
    run_id: UUID
    company_id: UUID
    product_id: UUID
    points: list[ForecastPointDTO]

    @classmethod
    def from_entity(cls, result: ForecastResult) -> ForecastResultDTO:
        assert result.id is not None
        return cls(
            id=result.id,
            run_id=result.run_id,
            company_id=result.company_id,
            product_id=result.product_id,
            points=[
                ForecastPointDTO(
                    period_date=p.period_date,
                    predicted_demand=p.predicted_demand,
                    lower_bound=p.lower_bound,
                    upper_bound=p.upper_bound,
                )
                for p in result.points
            ],
        )


class ForecastMetricsDTO(BaseModel):
    run_id: UUID
    product_id: UUID
    mape: Decimal
    mae: Decimal
    rmse: Decimal

    @classmethod
    def from_entity(cls, metrics: ForecastMetrics) -> ForecastMetricsDTO:
        return cls(
            run_id=metrics.run_id,
            product_id=metrics.product_id,
            mape=metrics.mape,
            mae=metrics.mae,
            rmse=metrics.rmse,
        )

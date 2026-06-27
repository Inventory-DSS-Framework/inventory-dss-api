"""Forecasting module — mappers."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from app.modules.forecasting.domain.entities import (
    ForecastMetrics,
    ForecastResult,
    ForecastRun,
)
from app.modules.forecasting.domain.enums import RunStatus
from app.modules.forecasting.domain.value_objects import ForecastPoint
from app.modules.forecasting.infrastructure.persistence.models import (
    ForecastMetricsModel,
    ForecastResultModel,
    ForecastRunModel,
)


def run_to_entity(model: ForecastRunModel) -> ForecastRun:
    return ForecastRun(
        id=model.id,
        company_id=model.company_id,
        dataset_id=model.dataset_id,
        model_name=model.model_name,
        horizon_days=model.horizon_days,
        status=RunStatus(model.status),
        started_at=model.started_at,
        completed_at=model.completed_at,
        error_message=model.error_message,
    )


def run_to_model(entity: ForecastRun) -> ForecastRunModel:
    return ForecastRunModel(
        id=entity.id,
        company_id=entity.company_id,
        dataset_id=entity.dataset_id,
        model_name=entity.model_name,
        horizon_days=entity.horizon_days,
        status=entity.status.value,
        started_at=entity.started_at,
        completed_at=entity.completed_at,
        error_message=entity.error_message,
    )


def _point_to_dict(p: ForecastPoint) -> dict[str, Any]:
    return {
        "period_date": p.period_date.isoformat(),
        "predicted_demand": str(p.predicted_demand),
        "lower_bound": str(p.lower_bound) if p.lower_bound is not None else None,
        "upper_bound": str(p.upper_bound) if p.upper_bound is not None else None,
    }


def _point_from_dict(data: dict[str, Any]) -> ForecastPoint:
    return ForecastPoint(
        period_date=date.fromisoformat(str(data["period_date"])),
        predicted_demand=Decimal(str(data["predicted_demand"])),
        lower_bound=(
            Decimal(str(data["lower_bound"]))
            if data.get("lower_bound") is not None
            else None
        ),
        upper_bound=(
            Decimal(str(data["upper_bound"]))
            if data.get("upper_bound") is not None
            else None
        ),
    )


def result_to_entity(model: ForecastResultModel) -> ForecastResult:
    return ForecastResult(
        id=model.id,
        run_id=model.run_id,
        company_id=model.company_id,
        product_id=model.product_id,
        points=[_point_from_dict(p) for p in model.points],
    )


def result_to_model(entity: ForecastResult) -> ForecastResultModel:
    return ForecastResultModel(
        id=entity.id,
        run_id=entity.run_id,
        company_id=entity.company_id,
        product_id=entity.product_id,
        points=[_point_to_dict(p) for p in entity.points],
    )


def metrics_to_entity(model: ForecastMetricsModel) -> ForecastMetrics:
    return ForecastMetrics(
        run_id=model.run_id,
        product_id=model.product_id,
        mape=model.mape,
        mae=model.mae,
        rmse=model.rmse,
    )


def metrics_to_model(entity: ForecastMetrics) -> ForecastMetricsModel:
    return ForecastMetricsModel(
        run_id=entity.run_id,
        product_id=entity.product_id,
        mape=entity.mape,
        mae=entity.mae,
        rmse=entity.rmse,
    )

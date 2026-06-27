"""Forecasting module — presentation DI providers."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.forecasting.infrastructure.persistence.repositories import (
    SqlForecastMetricsRepository,
    SqlForecastResultRepository,
    SqlForecastRunRepository,
)
from app.shared.infrastructure.database import get_db


def get_run_repository(db: Session = Depends(get_db)) -> SqlForecastRunRepository:
    return SqlForecastRunRepository(db)


def get_result_repository(db: Session = Depends(get_db)) -> SqlForecastResultRepository:
    return SqlForecastResultRepository(db)


def get_metrics_repository(
    db: Session = Depends(get_db),
) -> SqlForecastMetricsRepository:
    return SqlForecastMetricsRepository(db)

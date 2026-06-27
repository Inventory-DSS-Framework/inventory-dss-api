"""Forecasting module — background job runner.

Runs a forecast execution with its own DB session (the request session is already
closed by the time the background task runs). Decision ADR-002: forecasting executes
as a background job, not via async global. Later this can move behind QueuePort.
"""
from __future__ import annotations

from uuid import UUID

from app.modules.data_preparation.infrastructure.persistence.repositories import (
    SqlPreparedDatasetRepository,
)
from app.modules.forecasting.application.use_cases.execution import ExecuteForecastRun
from app.modules.forecasting.infrastructure.adapters.ftgm_adapter import FtgmHttpAdapter
from app.modules.forecasting.infrastructure.persistence.repositories import (
    SqlForecastMetricsRepository,
    SqlForecastResultRepository,
    SqlForecastRunRepository,
)
from app.shared.infrastructure.database import SessionLocal


def run_forecast_job(run_id: UUID) -> None:
    db = SessionLocal()
    try:
        ExecuteForecastRun(
            runs=SqlForecastRunRepository(db),
            results=SqlForecastResultRepository(db),
            metrics=SqlForecastMetricsRepository(db),
            datasets=SqlPreparedDatasetRepository(db),
            engine=FtgmHttpAdapter(),
        ).execute(run_id)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

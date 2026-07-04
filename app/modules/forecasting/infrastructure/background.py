"""Forecasting module — background job runner.

Runs a forecast execution with its own DB session (the request session is already
closed by the time the background task runs). Decision ADR-002: forecasting executes
as a background job, not via async global. Later this can move behind QueuePort.

After a successful run we also populate the downstream decision layer (KPIs and
replenishment recommendations) so the user doesn't have to trigger each one by hand.
That step is best-effort: a failure there is logged and swallowed so it can never
turn a successful forecast into a failed one.
"""
from __future__ import annotations

import logging
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
from app.modules.inventory.infrastructure.persistence.repositories import (
    SqlInventoryMovementRepository,
)
from app.modules.kpis.application.use_cases.compute import ComputeCompanyKpis
from app.modules.kpis.infrastructure.persistence.repositories import SqlKpiRepository
from app.modules.products.infrastructure.persistence.repositories import (
    SqlProductRepository,
)
from app.modules.recommendations.application.use_cases.generate import (
    GenerateRecommendations,
)
from app.modules.recommendations.infrastructure.persistence.repositories import (
    SqlRecommendationRepository,
)
from app.shared.infrastructure.database import SessionLocal

logger = logging.getLogger(__name__)


def run_forecast_job(run_id: UUID) -> None:
    db = SessionLocal()
    try:
        dto = ExecuteForecastRun(
            runs=SqlForecastRunRepository(db),
            results=SqlForecastResultRepository(db),
            metrics=SqlForecastMetricsRepository(db),
            datasets=SqlPreparedDatasetRepository(db),
            engine=FtgmHttpAdapter(),
        ).execute(run_id)

        # On success, populate KPIs + recommendations (best-effort, never fails the run).
        if dto.status == "success":
            _populate_decision_layer(db, dto.company_id)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _populate_decision_layer(db: object, company_id: UUID) -> None:
    """Compute KPIs and generate recommendations from the just-finished forecast.

    Each step is isolated: if one raises (e.g. no stock movements yet), it is logged
    and skipped so the other still runs and the forecast stays successful.
    """
    try:
        ComputeCompanyKpis(
            products=SqlProductRepository(db),
            runs=SqlForecastRunRepository(db),
            results=SqlForecastResultRepository(db),
            movements=SqlInventoryMovementRepository(db),
            kpis=SqlKpiRepository(db),
        ).execute(company_id)
    except Exception:  # noqa: BLE001 - best effort
        logger.exception("Auto KPI computation failed for company %s", company_id)

    try:
        GenerateRecommendations(
            products=SqlProductRepository(db),
            runs=SqlForecastRunRepository(db),
            results=SqlForecastResultRepository(db),
            movements=SqlInventoryMovementRepository(db),
            recommendations=SqlRecommendationRepository(db),
        ).execute(company_id)
    except Exception:  # noqa: BLE001 - best effort
        logger.exception("Auto recommendation generation failed for company %s", company_id)

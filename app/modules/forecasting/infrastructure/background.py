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
from datetime import datetime, timezone
from uuid import UUID

from app.modules.data_preparation.infrastructure.persistence.repositories import (
    SqlPreparedDatasetRepository,
)
from app.modules.forecasting.application.use_cases.execution import ExecuteForecastRun
from app.config import settings
from app.modules.forecasting.infrastructure.adapters.ftgm_adapter import FtgmHttpAdapter
from app.modules.forecasting.infrastructure.adapters.mock_ftgm import MockFtgmAdapter
from app.modules.forecasting.infrastructure.persistence.repositories import (
    SqlForecastMetricsRepository,
    SqlForecastResultRepository,
    SqlForecastRunRepository,
)
from app.modules.inventory.application.use_cases.movement import GetCompanyStockLevels
from app.modules.inventory.infrastructure.persistence.repositories import (
    SqlInventoryMovementRepository,
)
from app.modules.kpis.application.use_cases.compute import ComputeCompanyKpis
from app.modules.kpis.infrastructure.persistence.repositories import SqlKpiRepository
from app.modules.notifications.domain.entities import Notification
from app.modules.notifications.domain.enums import NotificationSeverity
from app.modules.notifications.infrastructure.persistence.repositories import (
    SqlNotificationRepository,
)
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
            engine=MockFtgmAdapter(db) if settings.ftgm_engine_mode == "mock" else FtgmHttpAdapter(),
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
    """Compute KPIs, generate recommendations, and emit notifications from the run.

    Each step is isolated: if one raises (e.g. no stock movements yet), it is logged
    and skipped so the others still run and the forecast stays successful.
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

    rec_count = 0
    try:
        created = GenerateRecommendations(
            products=SqlProductRepository(db),
            runs=SqlForecastRunRepository(db),
            results=SqlForecastResultRepository(db),
            movements=SqlInventoryMovementRepository(db),
            recommendations=SqlRecommendationRepository(db),
        ).execute(company_id)
        rec_count = len(created)
    except Exception:  # noqa: BLE001 - best effort
        logger.exception("Auto recommendation generation failed for company %s", company_id)

    try:
        _emit_notifications(db, company_id, rec_count)
    except Exception:  # noqa: BLE001 - best effort
        logger.exception("Auto notifications failed for company %s", company_id)


def _emit_notifications(db: object, company_id: UUID, rec_count: int) -> None:
    """Post user-facing notifications about the forecast and its downstream signals."""
    products_repo = SqlProductRepository(db)
    movements_repo = SqlInventoryMovementRepository(db)

    # Count products at or below their safety stock (critical).
    safety_by_id = {
        p.id: p.safety_stock for p in products_repo.list_active(company_id) if p.id is not None
    }
    levels = GetCompanyStockLevels(products=products_repo, movements=movements_repo).execute(
        company_id
    )
    critical = sum(
        1 for lvl in levels if lvl.quantity_on_hand <= safety_by_id.get(lvl.product_id, 0)
    )

    notifications = SqlNotificationRepository(db)

    def post(severity: NotificationSeverity, title: str, message: str) -> None:
        notifications.add(
            Notification(
                company_id=company_id,
                title=title,
                message=message,
                severity=severity,
                created_at=datetime.now(timezone.utc),
            )
        )

    post(
        NotificationSeverity.INFO,
        "Pronóstico FTGM completado",
        "El motor generó las predicciones y actualizó tus KPIs.",
    )
    if rec_count:
        post(
            NotificationSeverity.WARNING,
            f"{rec_count} recomendaciones de reabastecimiento",
            "Revisa las sugerencias de compra en la sección Recomendaciones.",
        )
    if critical:
        post(
            NotificationSeverity.CRITICAL,
            f"{critical} producto(s) en stock crítico",
            "Hay productos por debajo del stock de seguridad. Revísalos en Inventario.",
        )

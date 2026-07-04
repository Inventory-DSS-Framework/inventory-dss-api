"""KPIs module — cross-module orchestration to compute KPIs for a company.

Combines the three inputs of the DSS:
1. the forecast (latest successful ForecastRun + its per-product results),
2. the current stock (derived from the inventory movement ledger),
3. the product parameters (lead time, safety stock).
Applies the pure KPI formulas and persists one Kpi per (product, KpiType).
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.config import settings
from app.modules.forecasting.domain.enums import RunStatus
from app.modules.forecasting.domain.repositories import (
    ForecastResultRepository,
    ForecastRunRepository,
)
from app.modules.inventory.domain.repositories import InventoryMovementRepository
from app.modules.inventory.domain.services import compute_stock_on_hand
from app.modules.kpis.application.dtos import KpiDTO
from app.modules.kpis.domain.entities import Kpi
from app.modules.kpis.domain.repositories import KpiRepository
from app.modules.kpis.domain.services import ProductKpiInputs, compute_all
from app.modules.products.domain.repositories import ProductRepository
from app.shared.domain.errors import ValidationError

_MOVE_PAGE = 200
# Approximate calendar days per seasonal period, to turn per-period (monthly) forecast
# points into the daily-demand series the day-based reorder/KPI policies expect.
_DAYS_PER_PERIOD = {12: 30.44, 4: 91.31, 52: 7.0, 1: 1.0}


def _to_daily_demand(points: list) -> list[Decimal]:
    """Expand per-period forecast points into a flat daily-demand series.

    The FTGM engine forecasts one value per seasonal period (monthly by default), but
    the reorder/KPI formulas reason in days. Spread each period's demand evenly across
    its days so ``daily_demand[:lead_time_days]`` is the demand over the lead time.
    """
    period_days = _DAYS_PER_PERIOD.get(settings.ftgm_seasonal_period, 30.44)
    span = max(1, round(period_days))
    divisor = Decimal(str(period_days))
    daily: list[Decimal] = []
    for p in points:
        rate = p.predicted_demand / divisor
        daily.extend([rate] * span)
    return daily


class ComputeCompanyKpis:
    def __init__(
        self,
        *,
        products: ProductRepository,
        runs: ForecastRunRepository,
        results: ForecastResultRepository,
        movements: InventoryMovementRepository,
        kpis: KpiRepository,
    ) -> None:
        self._products = products
        self._runs = runs
        self._results = results
        self._movements = movements
        self._kpis = kpis

    def _current_stock(self, product_id: UUID) -> int:
        collected = []
        offset = 0
        while True:
            page = self._movements.list_by_product(product_id, offset, _MOVE_PAGE)
            collected.extend(page)
            if len(page) < _MOVE_PAGE:
                break
            offset += _MOVE_PAGE
        return compute_stock_on_hand(collected)

    def _latest_successful_run(self, company_id: UUID) -> UUID:
        for run in self._runs.list_by_company(company_id, 0, 50):
            if run.status == RunStatus.SUCCESS and run.id is not None:
                return run.id
        raise ValidationError(
            message="No completed forecast run available; run a forecast first."
        )

    def execute(self, company_id: UUID) -> list[KpiDTO]:
        run_id = self._latest_successful_run(company_id)
        computed_at = datetime.now(timezone.utc)

        to_add: list[Kpi] = []
        for product in self._products.list_active(company_id):
            if product.id is None:
                continue
            result = self._results.get_by_run_and_product(run_id, product.id)
            if result is None or not result.points:
                continue
            inputs = ProductKpiInputs(
                current_stock=self._current_stock(product.id),
                daily_demand=_to_daily_demand(result.points),
                lead_time_days=product.lead_time_days,
                safety_stock=product.safety_stock,
            )
            for kpi_type, value in compute_all(inputs).items():
                to_add.append(
                    Kpi(
                        company_id=company_id,
                        product_id=product.id,
                        kpi_type=kpi_type,
                        value=value,
                        computed_at=computed_at,
                        run_id=run_id,
                    )
                )

        return [KpiDTO.from_entity(k) for k in self._kpis.add_bulk(to_add)]

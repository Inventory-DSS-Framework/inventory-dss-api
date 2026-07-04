"""Recommendations module — generate replenishment recommendations for a company.

Cross-module orchestration: latest forecast + derived stock + product parameters ->
reorder policy -> persisted Recommendation. Skips products that already have a pending
recommendation to avoid duplicates.
"""
from __future__ import annotations

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
from app.modules.recommendations.application.dtos import RecommendationDTO
from app.modules.recommendations.domain.entities import Recommendation
from app.modules.recommendations.domain.repositories import RecommendationRepository
from app.modules.recommendations.domain.services import (
    ReorderInputs,
    suggest_reorder,
)
from app.modules.products.domain.repositories import ProductRepository
from app.shared.domain.errors import ValidationError
from app.shared.domain.value_objects import Quantity

_MOVE_PAGE = 200
# Approximate calendar days per seasonal period, to turn per-period (monthly) forecast
# points into the daily-demand series the day-based reorder policy expects.
_DAYS_PER_PERIOD = {12: 30.44, 4: 91.31, 52: 7.0, 1: 1.0}


def _to_daily_demand(points: list) -> list[Decimal]:
    """Expand per-period (monthly) forecast points into a flat daily-demand series."""
    period_days = _DAYS_PER_PERIOD.get(settings.ftgm_seasonal_period, 30.44)
    span = max(1, round(period_days))
    divisor = Decimal(str(period_days))
    daily: list[Decimal] = []
    for p in points:
        rate = p.predicted_demand / divisor
        daily.extend([rate] * span)
    return daily


class GenerateRecommendations:
    def __init__(
        self,
        *,
        products: ProductRepository,
        runs: ForecastRunRepository,
        results: ForecastResultRepository,
        movements: InventoryMovementRepository,
        recommendations: RecommendationRepository,
    ) -> None:
        self._products = products
        self._runs = runs
        self._results = results
        self._movements = movements
        self._recommendations = recommendations

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

    def execute(self, company_id: UUID) -> list[RecommendationDTO]:
        run_id = self._latest_successful_run(company_id)
        pending_products = {
            r.product_id for r in self._recommendations.list_pending(company_id)
        }

        created: list[RecommendationDTO] = []
        for product in self._products.list_active(company_id):
            if product.id is None or product.id in pending_products:
                continue
            result = self._results.get_by_run_and_product(run_id, product.id)
            if result is None or not result.points:
                continue
            suggestion = suggest_reorder(
                ReorderInputs(
                    current_stock=self._current_stock(product.id),
                    daily_demand=_to_daily_demand(result.points),
                    lead_time_days=product.lead_time_days,
                    safety_stock=product.safety_stock,
                    reorder_point=product.reorder_point,
                )
            )
            if suggestion is None:
                continue
            recommendation = Recommendation(
                company_id=company_id,
                product_id=product.id,
                recommended_quantity=Quantity(suggestion.quantity),
                priority=suggestion.priority,
                reason=suggestion.reason,
            )
            created.append(
                RecommendationDTO.from_entity(
                    self._recommendations.add(recommendation)
                )
            )
        return created

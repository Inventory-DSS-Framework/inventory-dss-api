"""Recommendations module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.modules.recommendations.domain.enums import (
    RecommendationPriority,
    RecommendationStatus,
)
from app.modules.recommendations.domain.exceptions import (
    InvalidRecommendationError,
)
from app.shared.domain.value_objects import Quantity


@dataclass
class Recommendation:
    """An actionable replenishment recommendation for a product."""

    company_id: UUID
    product_id: UUID
    recommended_quantity: Quantity
    priority: RecommendationPriority
    reason: str
    status: RecommendationStatus = RecommendationStatus.PENDING
    id: UUID | None = None

    def accept(self) -> None:
        """Accept this recommendation."""
        if self.status != RecommendationStatus.PENDING:
            raise InvalidRecommendationError(
                message=f"Cannot accept recommendation in status '{self.status}'"
            )
        self.status = RecommendationStatus.ACCEPTED

    def dismiss(self) -> None:
        """Dismiss this recommendation."""
        if self.status != RecommendationStatus.PENDING:
            raise InvalidRecommendationError(
                message=f"Cannot dismiss recommendation in status '{self.status}'"
            )
        self.status = RecommendationStatus.DISMISSED

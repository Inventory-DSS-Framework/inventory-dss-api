"""Billing module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import NotFoundError


class SubscriptionNotFoundError(NotFoundError):
    def __init__(self, company_id: UUID) -> None:
        super().__init__(
            message=f"Subscription for company '{company_id}' not found",
            details={"company_id": str(company_id)},
        )

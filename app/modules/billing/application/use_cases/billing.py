"""Billing module — application use cases."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.modules.billing.application.dtos import SubscriptionDTO
from app.modules.billing.domain.entities import Subscription
from app.modules.billing.domain.enums import SubscriptionStatus
from app.modules.billing.domain.exceptions import SubscriptionNotFoundError
from app.modules.billing.domain.repositories import SubscriptionRepository


class GetSubscription:
    def __init__(self, subscription_repo: SubscriptionRepository) -> None:
        self._subscription_repo = subscription_repo

    def execute(self, company_id: UUID) -> SubscriptionDTO:
        entity = self._subscription_repo.get_by_company(company_id)
        if not entity:
            raise SubscriptionNotFoundError(company_id)
        return SubscriptionDTO.from_entity(entity)


class UpdateSubscriptionStatus:
    """Updates a subscription status (e.g. via webhook)."""

    def __init__(self, subscription_repo: SubscriptionRepository) -> None:
        self._subscription_repo = subscription_repo

    def execute(
        self,
        company_id: UUID,
        status: SubscriptionStatus,
        plan_id: str | None = None,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> SubscriptionDTO:
        entity = self._subscription_repo.get_by_company(company_id)
        
        if entity:
            # Update existing
            entity.status = status
            if plan_id:
                entity.plan_id = plan_id
            if period_start:
                entity.current_period_start = period_start
            if period_end:
                entity.current_period_end = period_end
            saved = self._subscription_repo.update(entity)
        else:
            # Create new (simulate first webhook)
            now = datetime.now(timezone.utc)
            entity = Subscription(
                company_id=company_id,
                plan_id=plan_id or "default_plan",
                status=status,
                current_period_start=period_start or now,
                current_period_end=period_end or now,
            )
            saved = self._subscription_repo.add(entity)

        return SubscriptionDTO.from_entity(saved)

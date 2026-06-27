"""Billing module — SQLAlchemy repository implementation."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.billing.domain.entities import Subscription
from app.modules.billing.domain.exceptions import SubscriptionNotFoundError
from app.modules.billing.infrastructure.persistence.mappers import (
    subscription_to_entity,
    subscription_to_model,
)
from app.modules.billing.infrastructure.persistence.models import SubscriptionModel


class SqlSubscriptionRepository:
    """SQLAlchemy implementation of SubscriptionRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_company(self, company_id: UUID) -> Subscription | None:
        model = self._session.execute(
            select(SubscriptionModel).where(SubscriptionModel.company_id == company_id)
        ).scalar_one_or_none()
        return subscription_to_entity(model) if model else None

    def add(self, subscription: Subscription) -> Subscription:
        model = subscription_to_model(subscription)
        self._session.add(model)
        self._session.flush()
        return subscription_to_entity(model)

    def update(self, subscription: Subscription) -> Subscription:
        model = self._session.get(SubscriptionModel, subscription.id)
        if model is None:
            raise SubscriptionNotFoundError(subscription.company_id)
        
        model.plan_id = subscription.plan_id
        model.status = subscription.status.value
        model.current_period_start = subscription.current_period_start
        model.current_period_end = subscription.current_period_end
        
        self._session.flush()
        return subscription_to_entity(model)

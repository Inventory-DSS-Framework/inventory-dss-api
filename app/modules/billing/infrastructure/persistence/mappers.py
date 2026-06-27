"""Billing module — mappers."""
from __future__ import annotations

from app.modules.billing.domain.entities import Subscription
from app.modules.billing.domain.enums import SubscriptionStatus
from app.modules.billing.infrastructure.persistence.models import SubscriptionModel


def subscription_to_entity(model: SubscriptionModel) -> Subscription:
    return Subscription(
        id=model.id,
        company_id=model.company_id,
        plan_id=model.plan_id,
        status=SubscriptionStatus(model.status),
        current_period_start=model.current_period_start,
        current_period_end=model.current_period_end,
    )


def subscription_to_model(entity: Subscription) -> SubscriptionModel:
    return SubscriptionModel(
        id=entity.id,
        company_id=entity.company_id,
        plan_id=entity.plan_id,
        status=entity.status.value,
        current_period_start=entity.current_period_start,
        current_period_end=entity.current_period_end,
    )

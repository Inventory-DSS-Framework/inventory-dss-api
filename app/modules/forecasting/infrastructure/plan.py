"""Forecasting — plan lookup used for free-plan gating of the FTGM engine."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.billing.infrastructure.persistence.models import SubscriptionModel

PREMIUM_PLAN = "premium"
PREMIUM_STATUSES = frozenset({"active", "trialing"})


def company_is_premium(session: Session, company_id: UUID) -> bool:
    sub = session.execute(
        select(SubscriptionModel).where(SubscriptionModel.company_id == company_id)
    ).scalar_one_or_none()
    return bool(sub and sub.plan_id == PREMIUM_PLAN and sub.status in PREMIUM_STATUSES)

"""Billing module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.billing.domain.enums import SubscriptionStatus


@dataclass
class Subscription:
    """A company's billing subscription."""

    company_id: UUID
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    id: UUID | None = None

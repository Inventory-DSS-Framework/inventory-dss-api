"""Billing module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.modules.billing.domain.enums import (
    BillingCycle,
    PaymentMethod,
    PaymentStatus,
    SubscriptionStatus,
)


@dataclass
class Subscription:
    """A company's billing subscription."""

    company_id: UUID
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    id: UUID | None = None


@dataclass
class BillingPayment:
    """A (simulated) payment for a plan. Never holds card numbers or CVV — only last4."""

    company_id: UUID
    plan_id: str
    billing_cycle: BillingCycle
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    reference: str
    paid_at: datetime
    currency: str = "PEN"
    card_last4: str | None = None
    id: UUID | None = None
    created_at: datetime | None = None

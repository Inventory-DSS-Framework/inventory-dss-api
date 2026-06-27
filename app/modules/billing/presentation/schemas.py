"""Billing module — HTTP schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.billing.application.dtos import SubscriptionDTO
from app.modules.billing.domain.enums import SubscriptionStatus


class SubscriptionResponse(SubscriptionDTO):
    """Response schema for a company's subscription."""
    pass


class SubscriptionRequest(BaseModel):
    """Request schema for creating/updating a subscription."""
    plan_id: str = Field(..., min_length=1, max_length=50)


class WebhookUpdateSubscriptionRequest(BaseModel):
    """Payload for updating subscription via webhook."""
    status: SubscriptionStatus
    plan_id: str | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None


# Placeholders for endpoints not fully implemented
class PlanResponse(BaseModel):
    message: str
    module: str
    action: str

class PaymentWebhookResponse(BaseModel):
    message: str
    module: str
    action: str

class InvoiceResponse(BaseModel):
    message: str
    module: str
    action: str

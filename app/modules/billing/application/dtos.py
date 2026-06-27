"""Billing module — application DTOs."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.billing.domain.entities import Subscription
from app.modules.billing.domain.enums import SubscriptionStatus


class SubscriptionDTO(BaseModel):
    id: UUID
    company_id: UUID
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, entity: Subscription) -> SubscriptionDTO:
        if entity.id is None:
            raise ValueError("Entity must have an id to create DTO")
        return cls(
            id=entity.id,
            company_id=entity.company_id,
            plan_id=entity.plan_id,
            status=entity.status,
            current_period_start=entity.current_period_start,
            current_period_end=entity.current_period_end,
        )

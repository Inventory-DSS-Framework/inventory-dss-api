"""Billing module — ORM models."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base, TimestampMixin, UUIDMixin


class SubscriptionModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id"), unique=True, index=True, nullable=False
    )
    plan_id: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

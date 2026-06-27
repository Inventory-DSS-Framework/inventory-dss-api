"""Forecasting module — ORM models."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base, TimestampMixin, UUIDMixin


class ForecastRunModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "forecast_runs"

    company_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    dataset_id: Mapped[UUID | None] = mapped_column(index=True, nullable=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class ForecastResultModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "forecast_results"

    run_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    company_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    product_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    points: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)


class ForecastMetricsModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "forecast_metrics"

    run_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    product_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    mape: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    mae: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    rmse: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)

"""Forecasting module — presentation request schemas."""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class CreateForecastRunRequest(BaseModel):
    model_name: str = "FTGM"
    horizon_days: int = 30
    dataset_id: UUID | None = None

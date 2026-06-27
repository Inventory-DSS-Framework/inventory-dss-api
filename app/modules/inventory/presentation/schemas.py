"""Inventory module — presentation request schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateMovementRequest(BaseModel):
    product_id: UUID
    movement_type: str
    quantity: int
    reason: str = ""
    occurred_at: datetime | None = None


class CreateSnapshotRequest(BaseModel):
    product_id: UUID
    quantity_on_hand: int
    snapshot_at: datetime | None = None


class CreateReplenishmentRequest(BaseModel):
    product_id: UUID
    quantity: int


class UpdateReplenishmentRequest(BaseModel):
    status: str


class CreateStockoutRequest(BaseModel):
    product_id: UUID
    started_at: datetime | None = None


class CloseStockoutRequest(BaseModel):
    ended_at: datetime | None = None

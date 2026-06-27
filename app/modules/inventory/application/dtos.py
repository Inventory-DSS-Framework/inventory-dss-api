"""Inventory module — application output DTOs."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.inventory.domain.entities import (
    InventoryMovement,
    Replenishment,
    StockoutEvent,
    StockSnapshot,
)


class MovementDTO(BaseModel):
    id: UUID
    company_id: UUID
    product_id: UUID
    movement_type: str
    quantity: int
    reason: str
    occurred_at: datetime

    @classmethod
    def from_entity(cls, m: InventoryMovement) -> MovementDTO:
        assert m.id is not None
        return cls(
            id=m.id,
            company_id=m.company_id,
            product_id=m.product_id,
            movement_type=m.movement_type.value,
            quantity=m.quantity.value,
            reason=m.reason,
            occurred_at=m.occurred_at,
        )


class StockLevelDTO(BaseModel):
    product_id: UUID
    quantity_on_hand: int


class SnapshotDTO(BaseModel):
    id: UUID
    company_id: UUID
    product_id: UUID
    quantity_on_hand: int
    snapshot_at: datetime

    @classmethod
    def from_entity(cls, s: StockSnapshot) -> SnapshotDTO:
        assert s.id is not None
        return cls(
            id=s.id,
            company_id=s.company_id,
            product_id=s.product_id,
            quantity_on_hand=s.quantity_on_hand.value,
            snapshot_at=s.snapshot_at,
        )


class ReplenishmentDTO(BaseModel):
    id: UUID
    company_id: UUID
    product_id: UUID
    quantity: int
    status: str

    @classmethod
    def from_entity(cls, r: Replenishment) -> ReplenishmentDTO:
        assert r.id is not None
        return cls(
            id=r.id,
            company_id=r.company_id,
            product_id=r.product_id,
            quantity=r.quantity.value,
            status=r.status.value,
        )


class StockoutDTO(BaseModel):
    id: UUID
    company_id: UUID
    product_id: UUID
    started_at: datetime
    ended_at: datetime | None
    duration_days: int | None

    @classmethod
    def from_entity(cls, e: StockoutEvent) -> StockoutDTO:
        assert e.id is not None
        return cls(
            id=e.id,
            company_id=e.company_id,
            product_id=e.product_id,
            started_at=e.started_at,
            ended_at=e.ended_at,
            duration_days=e.duration_days(),
        )

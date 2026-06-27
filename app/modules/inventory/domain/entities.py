"""Inventory module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.inventory.domain.enums import MovementType, ReplenishmentStatus
from app.modules.inventory.domain.exceptions import InvalidInventoryError
from app.shared.domain.value_objects import Quantity


@dataclass
class InventoryMovement:
    """Records an inventory movement (in/out/adjustment)."""

    company_id: UUID
    product_id: UUID
    movement_type: MovementType
    quantity: Quantity
    reason: str
    occurred_at: datetime
    id: UUID | None = None


@dataclass
class StockSnapshot:
    """A point-in-time snapshot of stock for a product."""

    company_id: UUID
    product_id: UUID
    quantity_on_hand: Quantity
    snapshot_at: datetime
    id: UUID | None = None


@dataclass
class Replenishment:
    """A suggested or tracked replenishment order."""

    company_id: UUID
    product_id: UUID
    quantity: Quantity
    status: ReplenishmentStatus = ReplenishmentStatus.SUGGESTED
    id: UUID | None = None


@dataclass
class StockoutEvent:
    """Tracks a period when a product was out of stock."""

    company_id: UUID
    product_id: UUID
    started_at: datetime
    ended_at: datetime | None = None
    id: UUID | None = None

    def duration_days(self) -> int | None:
        """Return duration in days, or None if still open."""
        if self.ended_at is None:
            return None
        delta = self.ended_at - self.started_at
        return delta.days

    def close(self, at: datetime) -> None:
        """Close this stockout event at the given timestamp."""
        if self.ended_at is not None:
            raise InvalidInventoryError(
                message="Stockout event is already closed"
            )
        if at < self.started_at:
            raise InvalidInventoryError(
                message="End time cannot be before start time"
            )
        self.ended_at = at

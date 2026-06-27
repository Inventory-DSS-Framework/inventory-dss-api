"""Products module domain — entities.

Design note: unit_price < unit_cost is allowed (loss-leader pricing is a valid
business strategy). The invariant only enforces non-negative numeric fields.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.modules.products.domain.exceptions import InvalidProductError
from app.shared.domain.value_objects import Money, Sku


@dataclass
class Category:
    """Product category with optional parent for tree structures."""

    company_id: UUID
    name: str
    description: str = ""
    parent_id: UUID | None = None
    id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidProductError(message="Category name cannot be empty")


@dataclass
class Product:
    """A product (SKU) within a company's catalog."""

    company_id: UUID
    sku: Sku
    name: str
    unit_cost: Money
    unit_price: Money
    description: str = ""
    category_id: UUID | None = None
    unit_of_measure: str = "unit"
    lead_time_days: int = 0
    safety_stock: int = 0
    reorder_point: int = 0
    is_active: bool = True
    id: UUID | None = None

    def __post_init__(self) -> None:
        if self.lead_time_days < 0:
            raise InvalidProductError(
                message=f"lead_time_days cannot be negative, got {self.lead_time_days}"
            )
        if self.safety_stock < 0:
            raise InvalidProductError(
                message=f"safety_stock cannot be negative, got {self.safety_stock}"
            )
        if self.reorder_point < 0:
            raise InvalidProductError(
                message=f"reorder_point cannot be negative, got {self.reorder_point}"
            )

    def deactivate(self) -> None:
        """Mark product as inactive."""
        self.is_active = False

    def needs_reorder(self, on_hand: int) -> bool:
        """Return True when current stock is at or below the reorder point."""
        return self.is_active and on_hand <= self.reorder_point

"""Products module — presentation request schemas."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CreateProductRequest(BaseModel):
    sku: str
    name: str
    unit_cost: Decimal
    unit_price: Decimal
    currency: str = "PEN"
    description: str = ""
    category_id: UUID | None = None
    unit_of_measure: str = "unit"
    lead_time_days: int = 0
    safety_stock: int = 0
    reorder_point: int = 0


class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    unit_cost: Decimal | None = None
    unit_price: Decimal | None = None
    unit_of_measure: str | None = None
    lead_time_days: int | None = None
    safety_stock: int | None = None
    reorder_point: int | None = None


class CreateCategoryRequest(BaseModel):
    name: str
    description: str = ""
    parent_id: UUID | None = None


class UpdateCategoryRequest(BaseModel):
    name: str | None = None
    description: str | None = None

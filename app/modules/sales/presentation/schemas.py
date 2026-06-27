"""Sales module — presentation request schemas."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CreateSaleRequest(BaseModel):
    product_id: UUID
    sale_date: date
    quantity: int
    unit_price: Decimal
    currency: str = "PEN"
    batch_id: UUID | None = None


class BulkSalesItem(BaseModel):
    product_id: UUID
    sale_date: date
    quantity: int
    unit_price: Decimal
    currency: str = "PEN"
    batch_id: UUID | None = None


class BulkSalesRequest(BaseModel):
    items: list[BulkSalesItem]


class CreateSalesBatchRequest(BaseModel):
    source_file: str
    period_start: date | None = None
    period_end: date | None = None

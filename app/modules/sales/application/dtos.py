"""Sales module — application output DTOs."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.modules.sales.domain.entities import Sale, SalesBatch


class SaleDTO(BaseModel):
    id: UUID
    company_id: UUID
    product_id: UUID
    batch_id: UUID | None
    sale_date: date
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    currency: str

    @classmethod
    def from_entity(cls, sale: Sale) -> SaleDTO:
        assert sale.id is not None
        return cls(
            id=sale.id,
            company_id=sale.company_id,
            product_id=sale.product_id,
            batch_id=sale.batch_id,
            sale_date=sale.sale_date,
            quantity=sale.quantity.value,
            unit_price=sale.unit_price.amount,
            total_amount=sale.total_amount.amount,
            currency=sale.unit_price.currency,
        )


class SalesBatchDTO(BaseModel):
    id: UUID
    company_id: UUID
    source_file: str
    status: str
    row_count: int
    period_start: date | None
    period_end: date | None

    @classmethod
    def from_entity(cls, batch: SalesBatch) -> SalesBatchDTO:
        assert batch.id is not None
        return cls(
            id=batch.id,
            company_id=batch.company_id,
            source_file=batch.source_file,
            status=batch.status.value,
            row_count=batch.row_count,
            period_start=batch.period.start if batch.period else None,
            period_end=batch.period.end if batch.period else None,
        )

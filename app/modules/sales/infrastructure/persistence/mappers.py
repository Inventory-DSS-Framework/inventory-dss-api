"""Sales module — mappers between ORM models and domain entities."""
from __future__ import annotations

from app.modules.sales.domain.entities import Sale, SalesBatch
from app.modules.sales.domain.enums import BatchStatus
from app.modules.sales.infrastructure.persistence.models import (
    SaleModel,
    SalesBatchModel,
)
from app.shared.domain.value_objects import DateRange, Money, Quantity


def batch_to_entity(model: SalesBatchModel) -> SalesBatch:
    period = None
    if model.period_start is not None and model.period_end is not None:
        period = DateRange(model.period_start, model.period_end)
    return SalesBatch(
        id=model.id,
        company_id=model.company_id,
        source_file=model.source_file,
        status=BatchStatus(model.status),
        row_count=model.row_count,
        period=period,
    )


def batch_to_model(entity: SalesBatch) -> SalesBatchModel:
    return SalesBatchModel(
        id=entity.id,
        company_id=entity.company_id,
        source_file=entity.source_file,
        status=entity.status.value,
        row_count=entity.row_count,
        period_start=entity.period.start if entity.period else None,
        period_end=entity.period.end if entity.period else None,
    )


def sale_to_entity(model: SaleModel) -> Sale:
    return Sale(
        id=model.id,
        company_id=model.company_id,
        product_id=model.product_id,
        sale_date=model.sale_date,
        quantity=Quantity(model.quantity),
        unit_price=Money(model.unit_price, model.currency),
        total_amount=Money(model.total_amount, model.currency),
        batch_id=model.batch_id,
    )


def sale_to_model(entity: Sale) -> SaleModel:
    return SaleModel(
        id=entity.id,
        company_id=entity.company_id,
        product_id=entity.product_id,
        batch_id=entity.batch_id,
        sale_date=entity.sale_date,
        quantity=entity.quantity.value,
        unit_price=entity.unit_price.amount,
        total_amount=entity.total_amount.amount,
        currency=entity.unit_price.currency,
    )

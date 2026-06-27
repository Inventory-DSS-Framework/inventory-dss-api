"""Sales module — SQLAlchemy repository implementations."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.sales.domain.entities import Sale, SalesBatch
from app.modules.sales.domain.exceptions import SalesBatchNotFoundError
from app.modules.sales.infrastructure.persistence.mappers import (
    batch_to_entity,
    batch_to_model,
    sale_to_entity,
    sale_to_model,
)
from app.modules.sales.infrastructure.persistence.models import (
    SaleModel,
    SalesBatchModel,
)


class SqlSaleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, sale_id: UUID) -> Sale | None:
        model = self._session.get(SaleModel, sale_id)
        return sale_to_entity(model) if model else None

    def list_by_product_and_range(
        self, product_id: UUID, start: date, end: date
    ) -> list[Sale]:
        rows = self._session.execute(
            select(SaleModel)
            .where(
                SaleModel.product_id == product_id,
                SaleModel.sale_date >= start,
                SaleModel.sale_date <= end,
            )
            .order_by(SaleModel.sale_date)
        ).scalars().all()
        return [sale_to_entity(m) for m in rows]

    def list_by_company(
        self, company_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[Sale]:
        rows = self._session.execute(
            select(SaleModel)
            .where(SaleModel.company_id == company_id)
            .order_by(SaleModel.sale_date.desc())
            .offset(offset)
            .limit(limit)
        ).scalars().all()
        return [sale_to_entity(m) for m in rows]

    def add(self, sale: Sale) -> Sale:
        model = sale_to_model(sale)
        self._session.add(model)
        self._session.flush()
        return sale_to_entity(model)

    def add_bulk(self, sales: list[Sale]) -> list[Sale]:
        models = [sale_to_model(s) for s in sales]
        self._session.add_all(models)
        self._session.flush()
        return [sale_to_entity(m) for m in models]

    def delete(self, sale_id: UUID) -> bool:
        model = self._session.get(SaleModel, sale_id)
        if model is None:
            return False
        self._session.delete(model)
        self._session.flush()
        return True


class SqlSalesBatchRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, batch_id: UUID) -> SalesBatch | None:
        model = self._session.get(SalesBatchModel, batch_id)
        return batch_to_entity(model) if model else None

    def list_by_company(self, company_id: UUID) -> list[SalesBatch]:
        rows = self._session.execute(
            select(SalesBatchModel)
            .where(SalesBatchModel.company_id == company_id)
            .order_by(SalesBatchModel.created_at.desc())
        ).scalars().all()
        return [batch_to_entity(m) for m in rows]

    def add(self, batch: SalesBatch) -> SalesBatch:
        model = batch_to_model(batch)
        self._session.add(model)
        self._session.flush()
        return batch_to_entity(model)

    def update(self, batch: SalesBatch) -> SalesBatch:
        model = self._session.get(SalesBatchModel, batch.id)
        if model is None:
            raise SalesBatchNotFoundError(message=f"Sales batch '{batch.id}' not found")
        model.source_file = batch.source_file
        model.status = batch.status.value
        model.row_count = batch.row_count
        model.period_start = batch.period.start if batch.period else None
        model.period_end = batch.period.end if batch.period else None
        self._session.flush()
        return batch_to_entity(model)

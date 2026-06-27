"""Sales module — presentation DI providers."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.sales.infrastructure.persistence.repositories import (
    SqlSaleRepository,
    SqlSalesBatchRepository,
)
from app.shared.infrastructure.database import get_db


def get_sale_repository(db: Session = Depends(get_db)) -> SqlSaleRepository:
    return SqlSaleRepository(db)


def get_sales_batch_repository(db: Session = Depends(get_db)) -> SqlSalesBatchRepository:
    return SqlSalesBatchRepository(db)

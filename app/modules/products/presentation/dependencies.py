"""Products module — presentation DI providers."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.products.infrastructure.persistence.repositories import (
    SqlCategoryRepository,
    SqlProductRepository,
)
from app.shared.infrastructure.database import get_db


def get_product_repository(db: Session = Depends(get_db)) -> SqlProductRepository:
    return SqlProductRepository(db)


def get_category_repository(db: Session = Depends(get_db)) -> SqlCategoryRepository:
    return SqlCategoryRepository(db)

"""Data preparation module — presentation DI providers."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.data_preparation.infrastructure.persistence.repositories import (
    SqlPreparedDatasetRepository,
)
from app.modules.ingestion.infrastructure.persistence.repositories import (
    SqlIngestionBatchRepository,
)
from app.modules.products.infrastructure.persistence.repositories import (
    SqlProductRepository,
)
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.storage.local import LocalFileStorage


def get_dataset_repository(
    db: Session = Depends(get_db),
) -> SqlPreparedDatasetRepository:
    return SqlPreparedDatasetRepository(db)


def get_ingestion_repository(
    db: Session = Depends(get_db),
) -> SqlIngestionBatchRepository:
    return SqlIngestionBatchRepository(db)


def get_product_repository(db: Session = Depends(get_db)) -> SqlProductRepository:
    return SqlProductRepository(db)


def get_storage() -> LocalFileStorage:
    return LocalFileStorage()

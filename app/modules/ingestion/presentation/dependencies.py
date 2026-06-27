"""Ingestion module — presentation DI providers."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.ingestion.infrastructure.persistence.repositories import (
    SqlIngestionBatchRepository,
)
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.storage.local import LocalFileStorage


def get_ingestion_repository(
    db: Session = Depends(get_db),
) -> SqlIngestionBatchRepository:
    return SqlIngestionBatchRepository(db)


def get_storage() -> LocalFileStorage:
    return LocalFileStorage()

"""Files module — dependencies."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.modules.files.domain.repositories import StoredFileRepository
from app.modules.files.infrastructure.persistence.repositories import (
    SqlStoredFileRepository,
)
from app.shared.infrastructure.ports import StoragePort
from app.shared.infrastructure.storage.local import LocalFileStorage
from app.shared.presentation.deps import get_db


def get_stored_file_repository(
    db: Annotated[Session, Depends(get_db)],
) -> StoredFileRepository:
    """Dependency provider for StoredFileRepository."""
    return SqlStoredFileRepository(db)


def get_storage_port() -> StoragePort:
    """Dependency provider for StoragePort."""
    return LocalFileStorage(settings.storage_root)

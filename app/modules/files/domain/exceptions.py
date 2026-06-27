"""Files module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import NotFoundError


class StoredFileNotFoundError(NotFoundError):
    def __init__(self, file_id: UUID) -> None:
        super().__init__(
            message=f"File with id '{file_id}' not found",
            details={"file_id": str(file_id)},
        )

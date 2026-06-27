"""Ingestion module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from app.modules.ingestion.domain.enums import FileType, IngestionStatus
from app.modules.ingestion.domain.exceptions import InvalidIngestionError


@dataclass
class IngestionBatch:
    """Tracks an uploaded file through the ingestion pipeline."""

    company_id: UUID
    file_name: str
    file_path: str
    file_type: FileType
    column_mapping: dict[str, str] = field(default_factory=dict)
    status: IngestionStatus = IngestionStatus.UPLOADED
    row_count: int = 0
    error_count: int = 0
    id: UUID | None = None

    def __post_init__(self) -> None:
        if self.row_count < 0:
            raise InvalidIngestionError(
                message=f"row_count cannot be negative, got {self.row_count}"
            )
        if self.error_count < 0:
            raise InvalidIngestionError(
                message=f"error_count cannot be negative, got {self.error_count}"
            )

    def mark_validated(self) -> None:
        """Transition to validated status."""
        if self.status not in (IngestionStatus.VALIDATING, IngestionStatus.MAPPING):
            raise InvalidIngestionError(
                message=f"Cannot validate batch in status '{self.status}'"
            )
        self.status = IngestionStatus.VALIDATED

    def mark_failed(self) -> None:
        """Transition to failed status."""
        self.status = IngestionStatus.FAILED

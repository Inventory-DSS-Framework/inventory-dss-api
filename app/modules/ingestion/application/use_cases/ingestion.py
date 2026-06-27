"""Ingestion module — use cases.

Covers uploading a file (stored via StoragePort), registering its IngestionBatch,
setting the column mapping, and marking it validated. The analytical parsing/cleaning
of the file belongs to the data_preparation module.
"""
from __future__ import annotations

from uuid import UUID

from app.modules.ingestion.application.dtos import IngestionBatchDTO
from app.modules.ingestion.domain.entities import IngestionBatch
from app.modules.ingestion.domain.enums import FileType, IngestionStatus
from app.modules.ingestion.domain.exceptions import (
    IngestionBatchNotFoundError,
    InvalidIngestionError,
)
from app.modules.ingestion.domain.repositories import IngestionBatchRepository
from app.shared.infrastructure.ports import StoragePort


def _infer_file_type(file_name: str) -> FileType:
    ext = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
    if ext == "csv":
        return FileType.CSV
    if ext in ("xls", "xlsx"):
        return FileType.EXCEL
    raise InvalidIngestionError(
        message=f"Unsupported file extension '{ext}'. Allowed: csv, xls, xlsx"
    )


class UploadDataset:
    def __init__(
        self, batches: IngestionBatchRepository, storage: StoragePort
    ) -> None:
        self._batches = batches
        self._storage = storage

    def execute(
        self,
        company_id: UUID,
        *,
        file_name: str,
        content: bytes,
        content_type: str,
    ) -> IngestionBatchDTO:
        file_type = _infer_file_type(file_name)
        stored_path = self._storage.save(file_name, content, content_type)
        batch = IngestionBatch(
            company_id=company_id,
            file_name=file_name,
            file_path=stored_path,
            file_type=file_type,
        )
        return IngestionBatchDTO.from_entity(self._batches.add(batch))


class ListUploads:
    def __init__(self, batches: IngestionBatchRepository) -> None:
        self._batches = batches

    def execute(self, company_id: UUID) -> list[IngestionBatchDTO]:
        return [
            IngestionBatchDTO.from_entity(b)
            for b in self._batches.list_by_company(company_id)
        ]


class GetUpload:
    def __init__(self, batches: IngestionBatchRepository) -> None:
        self._batches = batches

    def execute(self, batch_id: UUID) -> IngestionBatchDTO:
        batch = self._batches.get_by_id(batch_id)
        if batch is None:
            raise IngestionBatchNotFoundError(
                message=f"Ingestion batch '{batch_id}' not found"
            )
        return IngestionBatchDTO.from_entity(batch)


class SetColumnMapping:
    def __init__(self, batches: IngestionBatchRepository) -> None:
        self._batches = batches

    def execute(
        self, batch_id: UUID, *, mapping: dict[str, str]
    ) -> IngestionBatchDTO:
        batch = self._batches.get_by_id(batch_id)
        if batch is None:
            raise IngestionBatchNotFoundError(
                message=f"Ingestion batch '{batch_id}' not found"
            )
        batch.column_mapping = mapping
        batch.status = IngestionStatus.MAPPING
        return IngestionBatchDTO.from_entity(self._batches.update(batch))


class ValidateUpload:
    def __init__(self, batches: IngestionBatchRepository) -> None:
        self._batches = batches

    def execute(self, batch_id: UUID) -> IngestionBatchDTO:
        batch = self._batches.get_by_id(batch_id)
        if batch is None:
            raise IngestionBatchNotFoundError(
                message=f"Ingestion batch '{batch_id}' not found"
            )
        batch.mark_validated()
        return IngestionBatchDTO.from_entity(self._batches.update(batch))

"""Reports module — application use cases."""
from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from app.modules.reports.application.dtos import ReportDTO
from app.modules.reports.domain.entities import Report
from app.modules.reports.domain.enums import ReportType
from app.modules.reports.domain.exceptions import ReportNotFoundError
from app.modules.reports.domain.repositories import ReportRepository
from app.shared.infrastructure.ports import StoragePort


class CreateReport:
    def __init__(self, report_repo: ReportRepository) -> None:
        self._report_repo = report_repo

    def execute(
        self,
        company_id: UUID,
        title: str,
        report_type: ReportType,
        params: dict[str, Any],
    ) -> ReportDTO:
        entity = Report(
            company_id=company_id,
            title=title,
            report_type=report_type,
            params=params,
        )
        saved = self._report_repo.add(entity)
        return ReportDTO.from_entity(saved)


class GenerateReport:
    """Generates stub content, saves via StoragePort, and marks report ready."""

    def __init__(self, report_repo: ReportRepository, storage: StoragePort) -> None:
        self._report_repo = report_repo
        self._storage = storage

    def execute(self, company_id: UUID, report_id: UUID) -> ReportDTO:
        entity = self._report_repo.get_by_id(report_id)
        if not entity or entity.company_id != company_id:
            raise ReportNotFoundError(report_id)

        try:
            # Generate stub content
            content_dict = {
                "report_id": str(entity.id),
                "title": entity.title,
                "type": entity.report_type.value,
                "params": entity.params,
                "data": "This is a STUB report generated automatically.",
            }
            content_bytes = json.dumps(content_dict, indent=2).encode("utf-8")
            file_name = f"report_{entity.id}.json"
            content_type = "application/json"

            # Save to storage
            file_path = self._storage.save(file_name, content_bytes, content_type)

            # Update entity
            entity.mark_ready(file_path)
            self._report_repo.update(entity)

        except Exception:
            entity.mark_failed()
            self._report_repo.update(entity)
            raise

        return ReportDTO.from_entity(entity)


class ListReports:
    def __init__(self, report_repo: ReportRepository) -> None:
        self._report_repo = report_repo

    def execute(
        self,
        company_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[ReportDTO]:
        entities = self._report_repo.list_by_company(
            company_id=company_id, offset=offset, limit=limit
        )
        return [ReportDTO.from_entity(e) for e in entities]


class GetReport:
    def __init__(self, report_repo: ReportRepository) -> None:
        self._report_repo = report_repo

    def execute(self, company_id: UUID, report_id: UUID) -> ReportDTO:
        entity = self._report_repo.get_by_id(report_id)
        if not entity or entity.company_id != company_id:
            raise ReportNotFoundError(report_id)
        return ReportDTO.from_entity(entity)


class DownloadReport:
    """Returns the bytes, filename, and content_type of a generated report."""

    def __init__(self, report_repo: ReportRepository, storage: StoragePort) -> None:
        self._report_repo = report_repo
        self._storage = storage

    def execute(self, company_id: UUID, report_id: UUID) -> tuple[bytes, str, str]:
        entity = self._report_repo.get_by_id(report_id)
        if not entity or entity.company_id != company_id:
            raise ReportNotFoundError(report_id)

        if not entity.file_path:
            raise ValueError("Report is not ready or has no file_path")

        content = self._storage.get(entity.file_path)
        file_name = f"report_{entity.id}.json"
        content_type = "application/json"

        return content, file_name, content_type

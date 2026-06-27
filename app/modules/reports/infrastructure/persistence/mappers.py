"""Reports module — mappers."""
from __future__ import annotations

from app.modules.reports.domain.entities import Report
from app.modules.reports.domain.enums import ReportStatus, ReportType
from app.modules.reports.infrastructure.persistence.models import ReportModel


def report_to_entity(model: ReportModel) -> Report:
    return Report(
        id=model.id,
        company_id=model.company_id,
        title=model.title,
        report_type=ReportType(model.report_type),
        status=ReportStatus(model.status),
        file_path=model.file_path,
        params=model.params or {},
    )


def report_to_model(entity: Report) -> ReportModel:
    return ReportModel(
        id=entity.id,
        company_id=entity.company_id,
        title=entity.title,
        report_type=entity.report_type.value,
        status=entity.status.value,
        file_path=entity.file_path,
        params=entity.params,
    )

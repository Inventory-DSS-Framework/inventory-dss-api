"""Audit module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import NotFoundError


class AuditEventNotFoundError(NotFoundError):
    def __init__(self, event_id: UUID) -> None:
        super().__init__(
            message=f"Audit event with id '{event_id}' not found",
            details={"event_id": str(event_id)},
        )

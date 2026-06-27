"""Notifications module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import NotFoundError, ValidationError


class NotificationNotFoundError(NotFoundError):
    def __init__(self, notification_id: UUID) -> None:
        super().__init__(
            message=f"Notification with id '{notification_id}' not found",
            details={"notification_id": str(notification_id)},
        )


class InvalidNotificationStateError(ValidationError):
    pass

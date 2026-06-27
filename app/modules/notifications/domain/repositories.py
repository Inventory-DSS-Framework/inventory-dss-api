"""Notifications module domain — repository ports."""
from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.modules.notifications.domain.entities import Notification


class NotificationRepository(Protocol):
    """Port for Notification persistence."""

    def get_by_id(self, notification_id: UUID) -> Notification | None: ...
    def list_by_company(
        self,
        company_id: UUID,
        unread_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Notification]: ...
    def add(self, notification: Notification) -> Notification: ...
    def update(self, notification: Notification) -> Notification: ...
    def delete(self, notification_id: UUID) -> bool: ...

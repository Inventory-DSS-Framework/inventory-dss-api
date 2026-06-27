"""Validation module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import NotFoundError


class ValidationRuleNotFoundError(NotFoundError):
    def __init__(self, rule_id: UUID) -> None:
        super().__init__(
            message=f"Validation rule with id '{rule_id}' not found",
            details={"rule_id": str(rule_id)},
        )

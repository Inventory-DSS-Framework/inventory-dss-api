"""Recommendations module domain — exceptions."""
from __future__ import annotations

from app.shared.domain.errors import NotFoundError, ValidationError


class RecommendationNotFoundError(NotFoundError):
    pass


class InvalidRecommendationError(ValidationError):
    pass

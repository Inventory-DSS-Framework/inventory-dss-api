"""Sales module domain — exceptions."""
from __future__ import annotations

from app.shared.domain.errors import NotFoundError, ValidationError


class SaleNotFoundError(NotFoundError):
    pass


class SalesBatchNotFoundError(NotFoundError):
    pass


class InvalidSaleError(ValidationError):
    pass

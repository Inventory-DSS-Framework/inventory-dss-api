"""Products module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import ConflictError, NotFoundError, ValidationError


class CategoryNotFoundError(NotFoundError):
    def __init__(self, category_id: UUID) -> None:
        super().__init__(
            message=f"Category with id '{category_id}' not found",
            details={"category_id": str(category_id)},
        )


class ProductNotFoundError(NotFoundError):
    def __init__(self, product_id: UUID) -> None:
        super().__init__(
            message=f"Product with id '{product_id}' not found",
            details={"product_id": str(product_id)},
        )


class ProductAlreadyExistsError(ConflictError):
    def __init__(self, sku: str) -> None:
        super().__init__(
            message=f"Product with SKU '{sku}' already exists",
            details={"sku": sku},
        )


class InvalidProductError(ValidationError):
    pass

"""Purchases module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import ConflictError, NotFoundError, ValidationError


class PurchaseNotFoundError(NotFoundError):
    def __init__(self, purchase_id: UUID) -> None:
        super().__init__(
            message="Compra no encontrada",
            details={"purchase_id": str(purchase_id)},
        )


class PurchaseDocumentNotFoundError(NotFoundError):
    def __init__(self, document_id: str) -> None:
        super().__init__(message="Documento de compra no encontrado", details={"document_id": document_id})


class PurchaseSupplierNotFoundError(NotFoundError):
    def __init__(self, supplier_id: UUID) -> None:
        super().__init__(message="El proveedor no existe", details={"supplier_id": str(supplier_id)})


class PurchaseProductNotFoundError(NotFoundError):
    def __init__(self, product_id: UUID) -> None:
        super().__init__(message="El producto no existe", details={"product_id": str(product_id)})


class InvalidPurchaseError(ValidationError):
    pass


class DuplicateProductCodeError(ConflictError):
    def __init__(self, sku: str) -> None:
        super().__init__(message=f"Ya existe un producto con el código {sku}", details={"sku": sku})

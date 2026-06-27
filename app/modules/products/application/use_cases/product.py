"""Products module — use cases for the Product aggregate."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.modules.products.application.dtos import ProductDTO
from app.modules.products.domain.entities import Product
from app.modules.products.domain.exceptions import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
)
from app.modules.products.domain.repositories import ProductRepository
from app.shared.domain.value_objects import Money, Sku


class CreateProduct:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    def execute(
        self,
        company_id: UUID,
        *,
        sku: str,
        name: str,
        unit_cost: Decimal,
        unit_price: Decimal,
        currency: str = "PEN",
        description: str = "",
        category_id: UUID | None = None,
        unit_of_measure: str = "unit",
        lead_time_days: int = 0,
        safety_stock: int = 0,
        reorder_point: int = 0,
    ) -> ProductDTO:
        sku_vo = Sku(sku)
        if self._products.get_by_sku(company_id, sku_vo.value) is not None:
            raise ProductAlreadyExistsError(sku_vo.value)
        product = Product(
            company_id=company_id,
            sku=sku_vo,
            name=name,
            unit_cost=Money(unit_cost, currency),
            unit_price=Money(unit_price, currency),
            description=description,
            category_id=category_id,
            unit_of_measure=unit_of_measure,
            lead_time_days=lead_time_days,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
        )
        return ProductDTO.from_entity(self._products.add(product))


class GetProduct:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    def execute(self, product_id: UUID) -> ProductDTO:
        product = self._products.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return ProductDTO.from_entity(product)


class ListProducts:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    def execute(
        self, company_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[ProductDTO]:
        return [
            ProductDTO.from_entity(p)
            for p in self._products.list_by_company(company_id, offset, limit)
        ]


class UpdateProduct:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    def execute(
        self,
        product_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        category_id: UUID | None = None,
        unit_cost: Decimal | None = None,
        unit_price: Decimal | None = None,
        unit_of_measure: str | None = None,
        lead_time_days: int | None = None,
        safety_stock: int | None = None,
        reorder_point: int | None = None,
    ) -> ProductDTO:
        product = self._products.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        currency = product.unit_cost.currency
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if category_id is not None:
            product.category_id = category_id
        if unit_cost is not None:
            product.unit_cost = Money(unit_cost, currency)
        if unit_price is not None:
            product.unit_price = Money(unit_price, currency)
        if unit_of_measure is not None:
            product.unit_of_measure = unit_of_measure
        if lead_time_days is not None:
            product.lead_time_days = lead_time_days
        if safety_stock is not None:
            product.safety_stock = safety_stock
        if reorder_point is not None:
            product.reorder_point = reorder_point
        return ProductDTO.from_entity(self._products.update(product))


class DeleteProduct:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    def execute(self, product_id: UUID) -> bool:
        if not self._products.delete(product_id):
            raise ProductNotFoundError(product_id)
        return True

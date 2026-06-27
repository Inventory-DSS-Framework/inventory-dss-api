"""Products module — application output DTOs."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.modules.products.domain.entities import Category, Product


class CategoryDTO(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: str
    parent_id: UUID | None

    @classmethod
    def from_entity(cls, category: Category) -> CategoryDTO:
        assert category.id is not None
        return cls(
            id=category.id,
            company_id=category.company_id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
        )


class ProductDTO(BaseModel):
    id: UUID
    company_id: UUID
    sku: str
    name: str
    description: str
    category_id: UUID | None
    unit_cost: Decimal
    unit_price: Decimal
    currency: str
    unit_of_measure: str
    lead_time_days: int
    safety_stock: int
    reorder_point: int
    is_active: bool

    @classmethod
    def from_entity(cls, product: Product) -> ProductDTO:
        assert product.id is not None
        return cls(
            id=product.id,
            company_id=product.company_id,
            sku=product.sku.value,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            unit_cost=product.unit_cost.amount,
            unit_price=product.unit_price.amount,
            currency=product.unit_cost.currency,
            unit_of_measure=product.unit_of_measure,
            lead_time_days=product.lead_time_days,
            safety_stock=product.safety_stock,
            reorder_point=product.reorder_point,
            is_active=product.is_active,
        )

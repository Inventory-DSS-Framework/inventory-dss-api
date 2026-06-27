"""Products module — use cases for the Category aggregate."""
from __future__ import annotations

from uuid import UUID

from app.modules.products.application.dtos import CategoryDTO
from app.modules.products.domain.entities import Category
from app.modules.products.domain.exceptions import CategoryNotFoundError
from app.modules.products.domain.repositories import CategoryRepository


class CreateCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    def execute(
        self,
        company_id: UUID,
        *,
        name: str,
        description: str = "",
        parent_id: UUID | None = None,
    ) -> CategoryDTO:
        category = Category(
            company_id=company_id,
            name=name,
            description=description,
            parent_id=parent_id,
        )
        return CategoryDTO.from_entity(self._categories.add(category))


class GetCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    def execute(self, category_id: UUID) -> CategoryDTO:
        category = self._categories.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
        return CategoryDTO.from_entity(category)


class ListCategories:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    def execute(self, company_id: UUID) -> list[CategoryDTO]:
        return [
            CategoryDTO.from_entity(c)
            for c in self._categories.list_by_company(company_id)
        ]


class UpdateCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    def execute(
        self,
        category_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> CategoryDTO:
        category = self._categories.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        return CategoryDTO.from_entity(self._categories.update(category))


class DeleteCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    def execute(self, category_id: UUID) -> bool:
        if not self._categories.delete(category_id):
            raise CategoryNotFoundError(category_id)
        return True

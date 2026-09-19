"""Custom fields module — use cases."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from uuid import UUID

from app.modules.custom_fields.domain.entities import (
    CustomFieldDefinition,
    normalize_category_ids,
    slugify,
)
from app.modules.custom_fields.infrastructure.persistence.repositories import (
    SqlCustomFieldRepository,
)
from app.shared.domain.errors import ConflictError, NotFoundError


@dataclass(frozen=True)
class CustomFieldDTO:
    id: UUID
    company_id: UUID
    entity: str
    key: str
    label: str
    field_type: str
    options: list[str]
    position: int
    is_visible: bool
    is_required: bool
    category_ids: list[str]

    @classmethod
    def from_entity(cls, f: CustomFieldDefinition) -> "CustomFieldDTO":
        return cls(**asdict(f))  # type: ignore[arg-type]


class ListCustomFields:
    def __init__(self, repo: SqlCustomFieldRepository) -> None:
        self._repo = repo

    def execute(self, company_id: UUID, entity: str | None) -> list[CustomFieldDTO]:
        return [CustomFieldDTO.from_entity(f) for f in self._repo.list(company_id, entity)]


class CreateCustomField:
    def __init__(self, repo: SqlCustomFieldRepository) -> None:
        self._repo = repo

    def execute(
        self,
        company_id: UUID,
        *,
        entity: str,
        label: str,
        field_type: str = "text",
        options: list[str] | None = None,
        is_required: bool = False,
        category_ids: list[str] | None = None,
    ) -> CustomFieldDTO:
        field = CustomFieldDefinition(
            company_id=company_id,
            entity=entity,
            label=label,
            field_type=field_type,
            options=options or [],
            is_required=is_required,
            category_ids=category_ids or [],
        )
        if self._repo.get_by_key(company_id, entity, field.key) is not None:
            raise ConflictError(message=f"Ya existe una columna llamada '{field.label}'")
        field.position = self._repo.next_position(company_id, entity)
        return CustomFieldDTO.from_entity(self._repo.add(field))


class EnsureCustomFields:
    """Idempotent create-if-missing, used by smart imports that add columns on the fly."""

    def __init__(self, repo: SqlCustomFieldRepository) -> None:
        self._repo = repo

    def execute(
        self, company_id: UUID, *, entity: str, fields: list[dict[str, Any]]
    ) -> list[CustomFieldDTO]:
        for spec in fields:
            label = (spec.get("label") or "").strip()
            if not label:
                continue
            if self._repo.get_by_key(company_id, entity, slugify(label)) is None:
                self._repo.add(
                    CustomFieldDefinition(
                        company_id=company_id,
                        entity=entity,
                        label=label,
                        field_type=spec.get("field_type") or "text",
                        options=spec.get("options") or [],
                        category_ids=spec.get("category_ids") or [],
                        position=self._repo.next_position(company_id, entity),
                    )
                )
        return [CustomFieldDTO.from_entity(f) for f in self._repo.list(company_id, entity)]


class UpdateCustomField:
    def __init__(self, repo: SqlCustomFieldRepository) -> None:
        self._repo = repo

    def execute(
        self,
        field_id: UUID,
        *,
        label: str | None = None,
        options: list[str] | None = None,
        is_visible: bool | None = None,
        is_required: bool | None = None,
        position: int | None = None,
        category_ids: list[str] | None = None,
    ) -> CustomFieldDTO:
        field = self._repo.get(field_id)
        if field is None:
            raise NotFoundError(message="Columna no encontrada")
        if category_ids is not None and field.entity == "product":
            field.category_ids = normalize_category_ids(category_ids)
        if label is not None and label.strip():
            field.label = label.strip()  # key stays stable so stored values keep working
        if options is not None:
            field.options = [o.strip() for o in options if o.strip()]
        if is_visible is not None:
            field.is_visible = is_visible
        if is_required is not None:
            field.is_required = is_required
        if position is not None:
            field.position = position
        return CustomFieldDTO.from_entity(self._repo.update(field))


class ReorderCustomFields:
    def __init__(self, repo: SqlCustomFieldRepository) -> None:
        self._repo = repo

    def execute(self, company_id: UUID, *, entity: str, ids: list[UUID]) -> list[CustomFieldDTO]:
        order = {fid: i for i, fid in enumerate(ids)}
        for field in self._repo.list(company_id, entity):
            if field.id in order:
                field.position = order[field.id]
                self._repo.update(field)
        return [CustomFieldDTO.from_entity(f) for f in self._repo.list(company_id, entity)]


class DeleteCustomField:
    def __init__(self, repo: SqlCustomFieldRepository) -> None:
        self._repo = repo

    def execute(self, field_id: UUID) -> None:
        if self._repo.get(field_id) is None:
            raise NotFoundError(message="Columna no encontrada")
        self._repo.delete(field_id)

"""Inventory module — movement and derived-stock use cases."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.modules.inventory.application.dtos import MovementDTO, StockLevelDTO
from app.modules.inventory.domain.entities import InventoryMovement
from app.modules.inventory.domain.enums import MovementType
from app.modules.inventory.domain.exceptions import InventoryMovementNotFoundError
from app.modules.inventory.domain.repositories import InventoryMovementRepository
from app.modules.inventory.domain.services import compute_stock_on_hand
from app.shared.domain.value_objects import Quantity

_PAGE = 200


class CreateMovement:
    def __init__(self, movements: InventoryMovementRepository) -> None:
        self._movements = movements

    def execute(
        self,
        company_id: UUID,
        *,
        product_id: UUID,
        movement_type: MovementType,
        quantity: int,
        reason: str = "",
        occurred_at: datetime | None = None,
    ) -> MovementDTO:
        movement = InventoryMovement(
            company_id=company_id,
            product_id=product_id,
            movement_type=movement_type,
            quantity=Quantity(quantity),
            reason=reason,
            occurred_at=occurred_at or datetime.now(timezone.utc),
        )
        return MovementDTO.from_entity(self._movements.add(movement))


class GetMovement:
    def __init__(self, movements: InventoryMovementRepository) -> None:
        self._movements = movements

    def execute(self, movement_id: UUID) -> MovementDTO:
        movement = self._movements.get_by_id(movement_id)
        if movement is None:
            raise InventoryMovementNotFoundError(
                message=f"Movement '{movement_id}' not found"
            )
        return MovementDTO.from_entity(movement)


class ListMovements:
    def __init__(self, movements: InventoryMovementRepository) -> None:
        self._movements = movements

    def execute(
        self, company_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[MovementDTO]:
        return [
            MovementDTO.from_entity(m)
            for m in self._movements.list_by_company(company_id, offset, limit)
        ]


class GetCurrentStock:
    """Derive current stock for a product from its full movement ledger."""

    def __init__(self, movements: InventoryMovementRepository) -> None:
        self._movements = movements

    def execute(self, product_id: UUID) -> StockLevelDTO:
        all_movements: list[InventoryMovement] = []
        offset = 0
        while True:
            page = self._movements.list_by_product(product_id, offset, _PAGE)
            all_movements.extend(page)
            if len(page) < _PAGE:
                break
            offset += _PAGE
        return StockLevelDTO(
            product_id=product_id,
            quantity_on_hand=compute_stock_on_hand(all_movements),
        )

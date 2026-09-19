"""Products module — application ports implemented by infrastructure adapters.

Creating or importing a product touches other concerns: the company's code correlativo
(P-000001...) and the inventory ledger (initial stock valued at cost). The use cases
depend on these small ports instead of on SQLAlchemy or on the inventory module.
"""
from __future__ import annotations

from contextlib import AbstractContextManager
from decimal import Decimal
from typing import Protocol
from uuid import UUID


class ProductCodeGenerator(Protocol):
    def next_code(self, company_id: UUID) -> str: ...


class ProductStockGateway(Protocol):
    def on_hand(self, company_id: UUID, product_id: UUID) -> int: ...

    def receive(
        self,
        company_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_cost: Decimal | None,
        *,
        reason: str,
        reference_type: str,
    ) -> None:
        """Inbound movement; updates weighted-average cost when unit_cost is given."""
        ...

    def remove(
        self,
        company_id: UUID,
        product_id: UUID,
        quantity: int,
        *,
        reason: str,
        reference_type: str,
    ) -> None:
        """Outbound correction (negative adjustment)."""
        ...


class UnitOfWork(Protocol):
    def savepoint(self) -> AbstractContextManager[object]:
        """A nested transaction: rolled back on exception, kept otherwise."""
        ...

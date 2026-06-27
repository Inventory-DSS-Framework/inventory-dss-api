"""Sales module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.modules.sales.domain.enums import BatchStatus
from app.modules.sales.domain.exceptions import InvalidSaleError
from app.shared.domain.value_objects import DateRange, Money, Quantity


@dataclass
class SalesBatch:
    """A batch of imported sales data."""

    company_id: UUID
    source_file: str
    status: BatchStatus = BatchStatus.PENDING
    row_count: int = 0
    period: DateRange | None = None
    id: UUID | None = None

    def __post_init__(self) -> None:
        if self.row_count < 0:
            raise InvalidSaleError(
                message=f"row_count cannot be negative, got {self.row_count}"
            )


@dataclass
class Sale:
    """An individual sale transaction.

    Invariant: total_amount == unit_price * quantity.
    """

    company_id: UUID
    product_id: UUID
    sale_date: date
    quantity: Quantity
    unit_price: Money
    total_amount: Money
    batch_id: UUID | None = None
    id: UUID | None = None

    def __post_init__(self) -> None:
        expected = self.unit_price.amount * Decimal(self.quantity.value)
        if self.total_amount.amount != expected:
            raise InvalidSaleError(
                message=(
                    f"total_amount ({self.total_amount.amount}) does not match "
                    f"unit_price * quantity ({expected})"
                )
            )
        if self.unit_price.currency != self.total_amount.currency:
            raise InvalidSaleError(
                message=(
                    f"Currency mismatch: unit_price is {self.unit_price.currency} "
                    f"but total_amount is {self.total_amount.currency}"
                )
            )

"""Forecasting module domain — entities.

ForecastRun implements a state machine with the following valid transitions:
    PENDING  → RUNNING   (start)
    PENDING  → CANCELLED (cancel)
    RUNNING  → SUCCESS   (complete)
    RUNNING  → FAILED    (fail)
    RUNNING  → CANCELLED (cancel)

Any other transition raises InvalidRunTransitionError.

Design note: ForecastMetrics is modeled as a standalone entity (not a frozen VO)
because it has an identity (run_id + product_id), is persisted independently, and
may be queried/listed on its own.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.modules.forecasting.domain.enums import RunStatus
from app.modules.forecasting.domain.exceptions import InvalidRunTransitionError
from app.modules.forecasting.domain.value_objects import ForecastPoint


# Valid state transitions for ForecastRun
_VALID_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.PENDING: frozenset({RunStatus.RUNNING, RunStatus.CANCELLED}),
    RunStatus.RUNNING: frozenset({RunStatus.SUCCESS, RunStatus.FAILED, RunStatus.CANCELLED}),
    RunStatus.SUCCESS: frozenset(),
    RunStatus.FAILED: frozenset(),
    RunStatus.CANCELLED: frozenset(),
}


@dataclass
class ForecastRun:
    """A forecast execution run tracking its lifecycle."""

    company_id: UUID
    model_name: str
    horizon_days: int
    dataset_id: UUID | None = None
    status: RunStatus = RunStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    id: UUID | None = None

    def _transition(self, target: RunStatus) -> None:
        """Validate and perform a state transition."""
        allowed = _VALID_TRANSITIONS.get(self.status, frozenset())
        if target not in allowed:
            raise InvalidRunTransitionError(
                message=(
                    f"Cannot transition from '{self.status}' to '{target}'"
                )
            )
        self.status = target

    def start(self) -> None:
        """Mark the run as started."""
        self._transition(RunStatus.RUNNING)
        self.started_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        """Mark the run as successfully completed."""
        self._transition(RunStatus.SUCCESS)
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, message: str) -> None:
        """Mark the run as failed with an error message."""
        self._transition(RunStatus.FAILED)
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = message

    def cancel(self) -> None:
        """Cancel the run."""
        self._transition(RunStatus.CANCELLED)
        self.completed_at = datetime.now(timezone.utc)


@dataclass
class ForecastResult:
    """Forecast output for a single product within a run."""

    run_id: UUID
    company_id: UUID
    product_id: UUID
    points: list[ForecastPoint] = field(default_factory=list)
    id: UUID | None = None


@dataclass
class ForecastMetrics:
    """Accuracy metrics for a forecast run on a specific product."""

    run_id: UUID
    product_id: UUID
    mape: Decimal
    mae: Decimal
    rmse: Decimal

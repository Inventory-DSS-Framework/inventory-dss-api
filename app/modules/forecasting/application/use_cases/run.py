"""Forecasting module — run lifecycle use cases."""
from __future__ import annotations

from uuid import UUID

from app.modules.forecasting.application.dtos import (
    ForecastMetricsDTO,
    ForecastResultDTO,
    ForecastRunDTO,
)
from app.modules.forecasting.domain.entities import ForecastRun
from app.modules.forecasting.domain.exceptions import ForecastRunNotFoundError
from app.modules.forecasting.domain.repositories import (
    ForecastMetricsRepository,
    ForecastResultRepository,
    ForecastRunRepository,
)


class CreateForecastRun:
    def __init__(self, runs: ForecastRunRepository) -> None:
        self._runs = runs

    def execute(
        self,
        company_id: UUID,
        *,
        model_name: str,
        horizon_days: int,
        dataset_id: UUID | None = None,
    ) -> ForecastRunDTO:
        run = ForecastRun(
            company_id=company_id,
            model_name=model_name,
            horizon_days=horizon_days,
            dataset_id=dataset_id,
        )
        return ForecastRunDTO.from_entity(self._runs.add(run))


class GetForecastRun:
    def __init__(self, runs: ForecastRunRepository) -> None:
        self._runs = runs

    def execute(self, run_id: UUID) -> ForecastRunDTO:
        run = self._runs.get_by_id(run_id)
        if run is None:
            raise ForecastRunNotFoundError(message=f"Forecast run '{run_id}' not found")
        return ForecastRunDTO.from_entity(run)


class ListForecastRuns:
    def __init__(self, runs: ForecastRunRepository) -> None:
        self._runs = runs

    def execute(
        self, company_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[ForecastRunDTO]:
        return [
            ForecastRunDTO.from_entity(r)
            for r in self._runs.list_by_company(company_id, offset, limit)
        ]


class CancelForecastRun:
    def __init__(self, runs: ForecastRunRepository) -> None:
        self._runs = runs

    def execute(self, run_id: UUID) -> ForecastRunDTO:
        run = self._runs.get_by_id(run_id)
        if run is None:
            raise ForecastRunNotFoundError(message=f"Forecast run '{run_id}' not found")
        run.cancel()
        return ForecastRunDTO.from_entity(self._runs.update(run))


class ListRunResults:
    def __init__(self, results: ForecastResultRepository) -> None:
        self._results = results

    def execute(self, run_id: UUID) -> list[ForecastResultDTO]:
        return [
            ForecastResultDTO.from_entity(r) for r in self._results.list_by_run(run_id)
        ]


class ListRunMetrics:
    def __init__(self, metrics: ForecastMetricsRepository) -> None:
        self._metrics = metrics

    def execute(self, run_id: UUID) -> list[ForecastMetricsDTO]:
        return [
            ForecastMetricsDTO.from_entity(m) for m in self._metrics.list_by_run(run_id)
        ]

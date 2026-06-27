"""Forecasting module — run execution (consumes the FTGM engine).

Orchestrates: start the run, fetch the prepared dataset series, call the engine,
persist results + metrics, and complete the run. Any failure marks the run as failed
with the error message (the run state machine guarantees valid transitions).
"""
from __future__ import annotations

from uuid import UUID

from app.modules.data_preparation.domain.repositories import (
    PreparedDatasetRepository,
)
from app.modules.forecasting.application.dtos import ForecastRunDTO
from app.modules.forecasting.application.ports import ForecastEnginePort
from app.modules.forecasting.domain.entities import ForecastMetrics, ForecastResult
from app.modules.forecasting.domain.exceptions import ForecastRunNotFoundError
from app.modules.forecasting.domain.repositories import (
    ForecastMetricsRepository,
    ForecastResultRepository,
    ForecastRunRepository,
)


class ExecuteForecastRun:
    def __init__(
        self,
        *,
        runs: ForecastRunRepository,
        results: ForecastResultRepository,
        metrics: ForecastMetricsRepository,
        datasets: PreparedDatasetRepository,
        engine: ForecastEnginePort,
    ) -> None:
        self._runs = runs
        self._results = results
        self._metrics = metrics
        self._datasets = datasets
        self._engine = engine

    def execute(self, run_id: UUID) -> ForecastRunDTO:
        run = self._runs.get_by_id(run_id)
        if run is None:
            raise ForecastRunNotFoundError(message=f"Forecast run '{run_id}' not found")

        run.start()
        self._runs.update(run)

        try:
            if run.dataset_id is None:
                raise ValueError("Run has no prepared dataset to forecast")
            dataset = self._datasets.get_by_id(run.dataset_id)
            if dataset is None:
                raise ValueError(f"Prepared dataset '{run.dataset_id}' not found")

            forecasts = self._engine.forecast(
                series=dataset.series,
                horizon_days=run.horizon_days,
                model_name=run.model_name,
            )

            self._results.add_bulk(
                [
                    ForecastResult(
                        run_id=run_id,
                        company_id=run.company_id,
                        product_id=f.product_id,
                        points=f.points,
                    )
                    for f in forecasts
                ]
            )
            self._metrics.add_bulk(
                [
                    ForecastMetrics(
                        run_id=run_id,
                        product_id=f.product_id,
                        mape=f.mape,
                        mae=f.mae,
                        rmse=f.rmse,
                    )
                    for f in forecasts
                ]
            )

            run.complete()
            return ForecastRunDTO.from_entity(self._runs.update(run))
        except Exception as exc:  # noqa: BLE001 - any failure must fail the run
            run.fail(str(exc))
            return ForecastRunDTO.from_entity(self._runs.update(run))

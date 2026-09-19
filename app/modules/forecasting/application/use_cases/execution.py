"""Forecasting module — run execution (consumes the FTGM engine).

Orchestrates: start the run, fetch the prepared dataset series, call the engine,
persist results + metrics, record the engine diagnostics and a run summary, and complete
the run. Any failure marks the run as failed with the error message (the run state
machine guarantees valid transitions).
"""
from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from app.modules.data_preparation.domain.repositories import (
    PreparedDatasetRepository,
)
from app.modules.forecasting.application.dtos import ForecastRunDTO
from app.modules.forecasting.application.ports import ForecastEnginePort, ProductForecast
from app.modules.forecasting.domain.entities import ForecastMetrics, ForecastResult
from app.modules.forecasting.domain.exceptions import ForecastRunNotFoundError
from app.modules.forecasting.domain.repositories import (
    ForecastMetricsRepository,
    ForecastResultRepository,
    ForecastRunRepository,
)


def summarize(forecasts: list[ProductForecast]) -> dict[str, Any]:
    """Run-level summary shown in the runs list."""
    total = sum(float(p.predicted_demand) for f in forecasts for p in f.points)
    next_period = sum(float(f.points[0].predicted_demand) for f in forecasts if f.points)
    models: dict[str, int] = {}
    freqs: dict[str, int] = {}
    for f in forecasts:
        if f.status != "skipped":
            models[f.model_used] = models.get(f.model_used, 0) + 1
        if f.frequency:
            freqs[f.frequency] = freqs.get(f.frequency, 0) + 1
    mapes = [
        float(f.diagnostics["holdout"]["mape"])
        for f in forecasts
        if isinstance(f.diagnostics.get("holdout"), dict) and f.diagnostics["holdout"].get("mape") is not None
    ]
    accuracies = sorted(
        float(f.diagnostics["accuracy_pct"])
        for f in forecasts
        if f.diagnostics.get("accuracy_pct") is not None
    )
    return {
        "total_forecast_units": round(total, 1),
        "next_period_units": round(next_period, 1),
        "products_ok": sum(1 for f in forecasts if f.status == "ok"),
        "products_fallback": sum(1 for f in forecasts if f.status == "fallback"),
        "products_skipped": sum(1 for f in forecasts if f.status == "skipped"),
        "models": models,
        "frequencies": freqs,
        "median_holdout_mape": round(sorted(mapes)[len(mapes) // 2], 2) if mapes else None,
        "median_accuracy_pct": round(accuracies[len(accuracies) // 2], 1) if accuracies else None,
    }


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

            as_of_raw = run.meta.get("as_of")
            forecasts = self._engine.forecast(
                series=dataset.series,
                horizon_days=run.horizon_days,
                model_name=run.model_name,
                frequency=run.frequency,
                as_of=date.fromisoformat(as_of_raw) if as_of_raw else None,
            )

            self._results.add_bulk(
                [
                    ForecastResult(
                        run_id=run_id,
                        company_id=run.company_id,
                        product_id=f.product_id,
                        points=f.points,
                        history=f.history,
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
                        mase=f.mase,
                        rmsse=f.rmsse,
                        order_selected=f.order_selected,
                        model_used=f.model_used,
                        status=f.status,
                        fallback_reason=f.fallback_reason,
                        validation_rmse=f.validation_rmse,
                    )
                    for f in forecasts
                ]
            )

            # The metrics table has no room for the engine's rich diagnostics, so they are
            # kept with the run (scope["_meta"]) — the result view explains every decision.
            run.set_meta(
                summary=summarize(forecasts),
                diagnostics={
                    str(f.product_id): {
                        **f.diagnostics,
                        "frequency": f.frequency or f.diagnostics.get("frequency"),
                        "period": f.period or f.diagnostics.get("period"),
                        "warnings": f.warnings,
                    }
                    for f in forecasts
                },
            )
            if run.product_ids is None:
                run.product_ids = [str(f.product_id) for f in forecasts]
            run.complete()
            return ForecastRunDTO.from_entity(self._runs.update(run))
        except Exception as exc:  # noqa: BLE001 - any failure must fail the run
            run.fail(str(exc)[:1000])
            return ForecastRunDTO.from_entity(self._runs.update(run))

"""Forecasting module — HTTP routers wired to use cases.

Implements the run lifecycle: create a run, execute it as a background job
(ADR-002), poll status, cancel, and read results/metrics. The FTGM engine is called
through FtgmHttpAdapter. Model comparison and CSV-driven execution stay as placeholders.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from app.modules.forecasting.application.dtos import (
    ForecastMetricsDTO,
    ForecastResultDTO,
    ForecastRunDTO,
)
from app.modules.forecasting.application.use_cases.run import (
    CancelForecastRun,
    CreateForecastRun,
    GetForecastRun,
    ListForecastRuns,
    ListRunMetrics,
    ListRunResults,
)
from app.modules.forecasting.domain.repositories import (
    ForecastMetricsRepository,
    ForecastResultRepository,
    ForecastRunRepository,
)
from app.modules.forecasting.infrastructure.background import run_forecast_job
from app.modules.forecasting.presentation.dependencies import (
    get_metrics_repository,
    get_result_repository,
    get_run_repository,
)
from app.modules.forecasting.presentation.schemas import CreateForecastRunRequest
from app.shared.presentation.deps import (
    AuthenticatedUser,
    get_pagination,
    require_company_access,
)
from app.shared.presentation.schemas import PaginationParams, PlaceholderResponse

runs_router = APIRouter()
forecasts_router = APIRouter()


@runs_router.post("", response_model=ForecastRunDTO, status_code=201)
def create_run(
    company_id: UUID,
    request: CreateForecastRunRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> ForecastRunDTO:
    return CreateForecastRun(repo).execute(
        company_id,
        model_name=request.model_name,
        horizon_days=request.horizon_days,
        dataset_id=request.dataset_id,
    )


@runs_router.get("", response_model=list[ForecastRunDTO])
def list_runs(
    company_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> list[ForecastRunDTO]:
    return ListForecastRuns(repo).execute(
        company_id,
        offset=(pagination.page - 1) * pagination.size,
        limit=pagination.size,
    )


@runs_router.post("/{run_id}/execute", response_model=ForecastRunDTO, status_code=202)
def execute_run(
    company_id: UUID,
    run_id: UUID,
    background_tasks: BackgroundTasks,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> ForecastRunDTO:
    run = GetForecastRun(repo).execute(run_id)  # 404 if missing
    background_tasks.add_task(run_forecast_job, run_id)
    return run


@runs_router.post("/{run_id}/cancel", response_model=ForecastRunDTO)
def cancel_run(
    company_id: UUID,
    run_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> ForecastRunDTO:
    return CancelForecastRun(repo).execute(run_id)


@runs_router.get("/{run_id}/status", response_model=ForecastRunDTO)
def get_run_status(
    company_id: UUID,
    run_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> ForecastRunDTO:
    return GetForecastRun(repo).execute(run_id)


@runs_router.get("/{run_id}/results", response_model=list[ForecastResultDTO])
def get_run_results(
    company_id: UUID,
    run_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastResultRepository = Depends(get_result_repository),
) -> list[ForecastResultDTO]:
    return ListRunResults(repo).execute(run_id)


@runs_router.get("/{run_id}/metrics", response_model=list[ForecastMetricsDTO])
def get_run_metrics(
    company_id: UUID,
    run_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastMetricsRepository = Depends(get_metrics_repository),
) -> list[ForecastMetricsDTO]:
    return ListRunMetrics(repo).execute(run_id)


@runs_router.get("/{run_id}", response_model=ForecastRunDTO)
def get_run(
    company_id: UUID,
    run_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> ForecastRunDTO:
    return GetForecastRun(repo).execute(run_id)


@runs_router.post("/compare-models", response_model=PlaceholderResponse)
def compare_models(company_id: UUID) -> PlaceholderResponse:
    # TODO: run FTGM vs baseline and compare metrics.
    return PlaceholderResponse(
        message="Endpoint scaffold ready", module="forecasting", action="compare_models"
    )


# --- Forecast results convenience endpoints ----------------------------------
@forecasts_router.get("/latest", response_model=ForecastRunDTO)
def get_latest_run(
    company_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ForecastRunRepository = Depends(get_run_repository),
) -> ForecastRunDTO:
    latest = repo.get_latest_by_company(company_id)
    if latest is None:
        from app.modules.forecasting.domain.exceptions import ForecastRunNotFoundError

        raise ForecastRunNotFoundError(message="No forecast runs for this company")
    return ForecastRunDTO.from_entity(latest)

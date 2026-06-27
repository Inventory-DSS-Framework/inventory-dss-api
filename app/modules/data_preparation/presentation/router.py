"""Data preparation module — HTTP router wired to use cases.

Implemented: create a prepared dataset (with series), list/get/delete. The automatic
preparation pipeline from an ingestion batch (cleaning, outliers, stockout flags) is a
placeholder for a later block.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.data_preparation.application.dtos import PreparedDatasetDTO
from app.modules.data_preparation.application.use_cases.dataset import (
    CreatePreparedDataset,
    DeletePreparedDataset,
    GetPreparedDataset,
    ListPreparedDatasets,
)
from app.modules.data_preparation.application.use_cases.prepare import (
    PrepareDatasetFromBatch,
)
from app.modules.data_preparation.domain.repositories import (
    PreparedDatasetRepository,
)
from app.modules.data_preparation.presentation.dependencies import (
    get_dataset_repository,
    get_ingestion_repository,
    get_product_repository,
    get_storage,
)
from app.modules.data_preparation.presentation.schemas import (
    CreatePreparedDatasetRequest,
    PrepareFromBatchRequest,
)
from app.modules.ingestion.infrastructure.persistence.repositories import (
    SqlIngestionBatchRepository,
)
from app.modules.products.infrastructure.persistence.repositories import (
    SqlProductRepository,
)
from app.shared.infrastructure.storage.local import LocalFileStorage
from app.shared.presentation.deps import AuthenticatedUser, require_company_access
from app.shared.presentation.schemas import MessageResponse

router = APIRouter()


@router.get("/datasets", response_model=list[PreparedDatasetDTO])
def list_datasets(
    company_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: PreparedDatasetRepository = Depends(get_dataset_repository),
) -> list[PreparedDatasetDTO]:
    return ListPreparedDatasets(repo).execute(company_id)


@router.post("/datasets", response_model=PreparedDatasetDTO, status_code=201)
def create_dataset(
    company_id: UUID,
    request: CreatePreparedDatasetRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: PreparedDatasetRepository = Depends(get_dataset_repository),
) -> PreparedDatasetDTO:
    series = [s.model_dump(mode="json") for s in request.series]
    return CreatePreparedDataset(repo).execute(
        company_id,
        series=series,
        source_batch_id=request.source_batch_id,
        period_start=request.period_start,
        period_end=request.period_end,
    )


@router.post("/prepare", response_model=PreparedDatasetDTO, status_code=201)
def prepare_from_batch(
    company_id: UUID,
    request: PrepareFromBatchRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    datasets: PreparedDatasetRepository = Depends(get_dataset_repository),
    batches: SqlIngestionBatchRepository = Depends(get_ingestion_repository),
    products: SqlProductRepository = Depends(get_product_repository),
    storage: LocalFileStorage = Depends(get_storage),
) -> PreparedDatasetDTO:
    return PrepareDatasetFromBatch(
        batches=batches,
        products=products,
        datasets=datasets,
        storage=storage,
    ).execute(
        company_id,
        batch_id=request.batch_id,
        treat_zero_as_stockout=request.treat_zero_as_stockout,
    )


@router.get("/datasets/{dataset_id}", response_model=PreparedDatasetDTO)
def get_dataset(
    company_id: UUID,
    dataset_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: PreparedDatasetRepository = Depends(get_dataset_repository),
) -> PreparedDatasetDTO:
    return GetPreparedDataset(repo).execute(dataset_id)


@router.delete("/datasets/{dataset_id}", response_model=MessageResponse)
def delete_dataset(
    company_id: UUID,
    dataset_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: PreparedDatasetRepository = Depends(get_dataset_repository),
) -> MessageResponse:
    DeletePreparedDataset(repo).execute(dataset_id)
    return MessageResponse(message="Dataset deleted")

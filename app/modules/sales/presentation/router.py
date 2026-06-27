"""Sales module — HTTP routers wired to use cases.

Sales CRUD (create/bulk/list/get/delete) and batch create/list/get are implemented.
update_sale and batch deletion are not implemented because the domain ports do not
expose those operations; analytics endpoints (history, summary, timeseries) belong to
later blocks and stay as placeholders.
"""
from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.sales.application.dtos import SaleDTO, SalesBatchDTO
from app.modules.sales.application.use_cases.batch import (
    CreateSalesBatch,
    GetSalesBatch,
    ListSalesBatches,
)
from app.modules.sales.application.use_cases.sale import (
    CreateSale,
    CreateSalesBulk,
    DeleteSale,
    GetSale,
    ListSales,
    ListSalesByProduct,
)
from app.modules.sales.domain.repositories import (
    SaleRepository,
    SalesBatchRepository,
)
from app.modules.sales.presentation.dependencies import (
    get_sale_repository,
    get_sales_batch_repository,
)
from app.modules.sales.presentation.schemas import (
    BulkSalesRequest,
    CreateSaleRequest,
    CreateSalesBatchRequest,
)
from app.shared.presentation.deps import (
    AuthenticatedUser,
    get_pagination,
    require_company_access,
)
from app.shared.presentation.schemas import (
    MessageResponse,
    PaginationParams,
    PlaceholderResponse,
)

router = APIRouter()
batches_router = APIRouter()


# --- Sales -------------------------------------------------------------------
@router.get("", response_model=list[SaleDTO])
def list_sales(
    company_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SaleRepository = Depends(get_sale_repository),
) -> list[SaleDTO]:
    return ListSales(repo).execute(
        company_id,
        offset=(pagination.page - 1) * pagination.size,
        limit=pagination.size,
    )


@router.post("", response_model=SaleDTO, status_code=201)
def create_sale(
    company_id: UUID,
    request: CreateSaleRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SaleRepository = Depends(get_sale_repository),
) -> SaleDTO:
    return CreateSale(repo).execute(
        company_id,
        product_id=request.product_id,
        sale_date=request.sale_date,
        quantity=request.quantity,
        unit_price=request.unit_price,
        currency=request.currency,
        batch_id=request.batch_id,
    )


@router.post("/bulk", response_model=list[SaleDTO], status_code=201)
def create_sales_bulk(
    company_id: UUID,
    request: BulkSalesRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SaleRepository = Depends(get_sale_repository),
) -> list[SaleDTO]:
    items = [item.model_dump(mode="json") for item in request.items]
    return CreateSalesBulk(repo).execute(company_id, items=items)


@router.get("/by-product/{product_id}", response_model=list[SaleDTO])
def get_sales_by_product(
    company_id: UUID,
    product_id: UUID,
    start: date,
    end: date,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SaleRepository = Depends(get_sale_repository),
) -> list[SaleDTO]:
    return ListSalesByProduct(repo).execute(product_id, start=start, end=end)


@router.get("/summary", response_model=PlaceholderResponse)
def get_sales_summary(company_id: UUID) -> PlaceholderResponse:
    # TODO(kpis/dashboard): sales aggregation.
    return PlaceholderResponse(
        message="Endpoint scaffold ready", module="sales", action="get_sales_summary"
    )


@router.get("/{sale_id}", response_model=SaleDTO)
def get_sale(
    company_id: UUID,
    sale_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SaleRepository = Depends(get_sale_repository),
) -> SaleDTO:
    return GetSale(repo).execute(sale_id)


@router.delete("/{sale_id}", response_model=MessageResponse)
def delete_sale(
    company_id: UUID,
    sale_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SaleRepository = Depends(get_sale_repository),
) -> MessageResponse:
    DeleteSale(repo).execute(sale_id)
    return MessageResponse(message="Sale deleted")


@router.patch("/{sale_id}", response_model=PlaceholderResponse)
def update_sale(company_id: UUID, sale_id: UUID) -> PlaceholderResponse:
    # TODO: SaleRepository has no update operation; revise the port if needed.
    return PlaceholderResponse(
        message="Endpoint scaffold ready", module="sales", action="update_sale"
    )


# --- Sales batches -----------------------------------------------------------
@batches_router.get("", response_model=list[SalesBatchDTO])
def list_sales_batches(
    company_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SalesBatchRepository = Depends(get_sales_batch_repository),
) -> list[SalesBatchDTO]:
    return ListSalesBatches(repo).execute(company_id)


@batches_router.post("", response_model=SalesBatchDTO, status_code=201)
def create_sales_batch(
    company_id: UUID,
    request: CreateSalesBatchRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SalesBatchRepository = Depends(get_sales_batch_repository),
) -> SalesBatchDTO:
    return CreateSalesBatch(repo).execute(
        company_id,
        source_file=request.source_file,
        period_start=request.period_start,
        period_end=request.period_end,
    )


@batches_router.get("/{batch_id}", response_model=SalesBatchDTO)
def get_sales_batch(
    company_id: UUID,
    batch_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: SalesBatchRepository = Depends(get_sales_batch_repository),
) -> SalesBatchDTO:
    return GetSalesBatch(repo).execute(batch_id)

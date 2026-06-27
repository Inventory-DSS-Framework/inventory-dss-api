"""Inventory module — HTTP router wired to use cases.

Implemented: derived current stock, movement create/list/get, snapshot create/list,
replenishment create/list/update-status, stockout create/list-open/close. Endpoints
whose domain ports do not exist yet (bulk, movement update/delete, get-by-id for
snapshots, automatic stockout detection, company-wide current stock) remain placeholders.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.inventory.application.dtos import (
    MovementDTO,
    ReplenishmentDTO,
    SnapshotDTO,
    StockLevelDTO,
    StockoutDTO,
)
from app.modules.inventory.application.use_cases.movement import (
    CreateMovement,
    GetCurrentStock,
    GetMovement,
    ListMovements,
)
from app.modules.inventory.application.use_cases.detection import DetectStockouts
from app.modules.inventory.application.use_cases.stock_records import (
    CloseStockout,
    CreateReplenishment,
    CreateSnapshot,
    CreateStockout,
    ListOpenStockouts,
    ListProductSnapshots,
    ListReplenishments,
    UpdateReplenishmentStatus,
)
from app.modules.inventory.domain.repositories import (
    InventoryMovementRepository,
    ReplenishmentRepository,
    StockoutEventRepository,
    StockSnapshotRepository,
)
from app.modules.inventory.presentation.dependencies import (
    get_movement_repository,
    get_product_repository,
    get_replenishment_repository,
    get_snapshot_repository,
    get_stockout_repository,
    parse_movement_type,
    parse_replenishment_status,
)
from app.modules.products.domain.repositories import ProductRepository
from app.modules.inventory.presentation.schemas import (
    CloseStockoutRequest,
    CreateMovementRequest,
    CreateReplenishmentRequest,
    CreateSnapshotRequest,
    CreateStockoutRequest,
    UpdateReplenishmentRequest,
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


# --- Current stock (derived) -------------------------------------------------
@router.get("/current-stock/{product_id}", response_model=StockLevelDTO)
def get_current_stock_by_product(
    company_id: UUID,
    product_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: InventoryMovementRepository = Depends(get_movement_repository),
) -> StockLevelDTO:
    return GetCurrentStock(repo).execute(product_id)


@router.get("/current-stock", response_model=PlaceholderResponse)
def get_current_stock(company_id: UUID) -> PlaceholderResponse:
    # TODO: company-wide stock needs the product catalogue (cross-module).
    return PlaceholderResponse(
        message="Endpoint scaffold ready", module="inventory", action="get_current_stock"
    )


# --- Movements ---------------------------------------------------------------
@router.get("/movements", response_model=list[MovementDTO])
def list_movements(
    company_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    _: AuthenticatedUser = Depends(require_company_access),
    repo: InventoryMovementRepository = Depends(get_movement_repository),
) -> list[MovementDTO]:
    return ListMovements(repo).execute(
        company_id,
        offset=(pagination.page - 1) * pagination.size,
        limit=pagination.size,
    )


@router.post("/movements", response_model=MovementDTO, status_code=201)
def create_movement(
    company_id: UUID,
    request: CreateMovementRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: InventoryMovementRepository = Depends(get_movement_repository),
) -> MovementDTO:
    return CreateMovement(repo).execute(
        company_id,
        product_id=request.product_id,
        movement_type=parse_movement_type(request.movement_type),
        quantity=request.quantity,
        reason=request.reason,
        occurred_at=request.occurred_at,
    )


@router.get("/movements/{movement_id}", response_model=MovementDTO)
def get_movement(
    company_id: UUID,
    movement_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: InventoryMovementRepository = Depends(get_movement_repository),
) -> MovementDTO:
    return GetMovement(repo).execute(movement_id)


# --- Snapshots ---------------------------------------------------------------
@router.post("/snapshots", response_model=SnapshotDTO, status_code=201)
def create_snapshot(
    company_id: UUID,
    request: CreateSnapshotRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: StockSnapshotRepository = Depends(get_snapshot_repository),
) -> SnapshotDTO:
    return CreateSnapshot(repo).execute(
        company_id,
        product_id=request.product_id,
        quantity_on_hand=request.quantity_on_hand,
        snapshot_at=request.snapshot_at,
    )


@router.get("/snapshots/by-product/{product_id}", response_model=list[SnapshotDTO])
def list_product_snapshots(
    company_id: UUID,
    product_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: StockSnapshotRepository = Depends(get_snapshot_repository),
) -> list[SnapshotDTO]:
    return ListProductSnapshots(repo).execute(product_id)


# --- Replenishments ----------------------------------------------------------
@router.get("/replenishments", response_model=list[ReplenishmentDTO])
def list_replenishments(
    company_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ReplenishmentRepository = Depends(get_replenishment_repository),
) -> list[ReplenishmentDTO]:
    return ListReplenishments(repo).execute(
        company_id,
        offset=(pagination.page - 1) * pagination.size,
        limit=pagination.size,
    )


@router.post("/replenishments", response_model=ReplenishmentDTO, status_code=201)
def create_replenishment(
    company_id: UUID,
    request: CreateReplenishmentRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ReplenishmentRepository = Depends(get_replenishment_repository),
) -> ReplenishmentDTO:
    return CreateReplenishment(repo).execute(
        company_id, product_id=request.product_id, quantity=request.quantity
    )


@router.patch("/replenishments/{replenishment_id}", response_model=ReplenishmentDTO)
def update_replenishment(
    company_id: UUID,
    replenishment_id: UUID,
    request: UpdateReplenishmentRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ReplenishmentRepository = Depends(get_replenishment_repository),
) -> ReplenishmentDTO:
    return UpdateReplenishmentStatus(repo).execute(
        replenishment_id, status=parse_replenishment_status(request.status)
    )


# --- Stockouts ---------------------------------------------------------------
@router.get("/stockouts", response_model=list[StockoutDTO])
def list_stockouts(
    company_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: StockoutEventRepository = Depends(get_stockout_repository),
) -> list[StockoutDTO]:
    return ListOpenStockouts(repo).execute(company_id)


@router.post("/stockouts", response_model=StockoutDTO, status_code=201)
def create_stockout(
    company_id: UUID,
    request: CreateStockoutRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: StockoutEventRepository = Depends(get_stockout_repository),
) -> StockoutDTO:
    return CreateStockout(repo).execute(
        company_id, product_id=request.product_id, started_at=request.started_at
    )


@router.post("/stockouts/detect", response_model=list[StockoutDTO], status_code=201)
def detect_stockouts(
    company_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    products: ProductRepository = Depends(get_product_repository),
    movements: InventoryMovementRepository = Depends(get_movement_repository),
    stockouts: StockoutEventRepository = Depends(get_stockout_repository),
) -> list[StockoutDTO]:
    return DetectStockouts(
        products=products,
        movements=movements,
        stockouts=stockouts,
    ).execute(company_id)


@router.patch("/stockouts/{stockout_id}", response_model=StockoutDTO)
def close_stockout(
    company_id: UUID,
    stockout_id: UUID,
    request: CloseStockoutRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: StockoutEventRepository = Depends(get_stockout_repository),
) -> StockoutDTO:
    return CloseStockout(repo).execute(stockout_id, ended_at=request.ended_at)


@router.delete("/stockouts/{stockout_id}", response_model=MessageResponse)
def delete_stockout(company_id: UUID, stockout_id: UUID) -> MessageResponse:
    # TODO: StockoutEventRepository has no delete operation.
    return MessageResponse(message="Not implemented yet")

"""Products module — HTTP routers wired to use cases.

CRUD for products and categories is implemented. Advanced endpoints (search, bulk
operations, summary, timeline, data-quality) remain placeholders for later blocks.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.products.application.dtos import CategoryDTO, ProductDTO
from app.modules.products.application.use_cases.category import (
    CreateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
)
from app.modules.products.application.use_cases.product import (
    CreateProduct,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
)
from app.modules.products.domain.repositories import (
    CategoryRepository,
    ProductRepository,
)
from app.modules.products.presentation.dependencies import (
    get_category_repository,
    get_product_repository,
)
from app.modules.products.presentation.schemas import (
    CreateCategoryRequest,
    CreateProductRequest,
    UpdateCategoryRequest,
    UpdateProductRequest,
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
categories_router = APIRouter()


# --- Products ----------------------------------------------------------------
@router.get("", response_model=list[ProductDTO])
def list_products(
    company_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> list[ProductDTO]:
    return ListProducts(repo).execute(
        company_id,
        offset=(pagination.page - 1) * pagination.size,
        limit=pagination.size,
    )


@router.post("", response_model=ProductDTO, status_code=201)
def create_product(
    company_id: UUID,
    request: CreateProductRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    return CreateProduct(repo).execute(
        company_id,
        sku=request.sku,
        name=request.name,
        unit_cost=request.unit_cost,
        unit_price=request.unit_price,
        currency=request.currency,
        description=request.description,
        category_id=request.category_id,
        unit_of_measure=request.unit_of_measure,
        lead_time_days=request.lead_time_days,
        safety_stock=request.safety_stock,
        reorder_point=request.reorder_point,
    )


@router.get("/{product_id}", response_model=ProductDTO)
def get_product(
    company_id: UUID,
    product_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    return GetProduct(repo).execute(product_id)


@router.patch("/{product_id}", response_model=ProductDTO)
def update_product(
    company_id: UUID,
    product_id: UUID,
    request: UpdateProductRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    return UpdateProduct(repo).execute(
        product_id,
        name=request.name,
        description=request.description,
        category_id=request.category_id,
        unit_cost=request.unit_cost,
        unit_price=request.unit_price,
        unit_of_measure=request.unit_of_measure,
        lead_time_days=request.lead_time_days,
        safety_stock=request.safety_stock,
        reorder_point=request.reorder_point,
    )


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
    company_id: UUID,
    product_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> MessageResponse:
    DeleteProduct(repo).execute(product_id)
    return MessageResponse(message="Product deleted")


@router.get("/{product_id}/summary", response_model=PlaceholderResponse)
def get_product_summary(company_id: UUID, product_id: UUID) -> PlaceholderResponse:
    # TODO(kpis/dashboard): product summary aggregation.
    return PlaceholderResponse(
        message="Endpoint scaffold ready", module="products", action="get_product_summary"
    )


# --- Categories --------------------------------------------------------------
@categories_router.get("", response_model=list[CategoryDTO])
def list_categories(
    company_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: CategoryRepository = Depends(get_category_repository),
) -> list[CategoryDTO]:
    return ListCategories(repo).execute(company_id)


@categories_router.post("", response_model=CategoryDTO, status_code=201)
def create_category(
    company_id: UUID,
    request: CreateCategoryRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryDTO:
    return CreateCategory(repo).execute(
        company_id,
        name=request.name,
        description=request.description,
        parent_id=request.parent_id,
    )


@categories_router.get("/{category_id}", response_model=CategoryDTO)
def get_category(
    company_id: UUID,
    category_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryDTO:
    return GetCategory(repo).execute(category_id)


@categories_router.patch("/{category_id}", response_model=CategoryDTO)
def update_category(
    company_id: UUID,
    category_id: UUID,
    request: UpdateCategoryRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryDTO:
    return UpdateCategory(repo).execute(
        category_id, name=request.name, description=request.description
    )


@categories_router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(
    company_id: UUID,
    category_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: CategoryRepository = Depends(get_category_repository),
) -> MessageResponse:
    DeleteCategory(repo).execute(category_id)
    return MessageResponse(message="Category deleted")

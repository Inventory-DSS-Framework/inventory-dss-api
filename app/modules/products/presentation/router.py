"""Products module — HTTP routers wired to use cases.

Products: CRUD (image, barcode, custom attributes, optional SKU → correlativo, initial
stock), smart import and the Product 360 timeline. Categories: CRUD.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.modules.products.application.dtos import (
    CategoryDTO,
    ImportProductsResultDTO,
    ProductDTO,
    ProductTimelineDTO,
)
from app.modules.products.application.use_cases.category import (
    CreateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
)
from app.modules.products.application.use_cases.importing import (
    ImportProducts,
    ProductImportRow,
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
from app.modules.products.infrastructure.adapters.stock import (
    SqlProductCodeGenerator,
    SqlProductStockGateway,
    SqlUnitOfWork,
)
from app.modules.products.infrastructure.persistence.timeline import SqlProductTimelineQuery
from app.modules.products.presentation.dependencies import (
    get_category_repository,
    get_code_generator,
    get_product_repository,
    get_stock_gateway,
    get_timeline_query,
    get_unit_of_work,
)
from app.modules.products.presentation.schemas import (
    CreateCategoryRequest,
    CreateProductRequest,
    ImportProductsRequest,
    UpdateCategoryRequest,
    UpdateProductRequest,
)
from app.shared.presentation.deps import (
    AuthenticatedUser,
    require_company_access,
)
from app.shared.presentation.schemas import MessageResponse

router = APIRouter()
categories_router = APIRouter()


# --- Products ----------------------------------------------------------------
@router.get("", response_model=list[ProductDTO])
def list_products(
    company_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(1000, ge=1, le=5000, description="Catalogs are small; default returns everything."),
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> list[ProductDTO]:
    return ListProducts(repo).execute(company_id, offset=(page - 1) * size, limit=size)


@router.post("", response_model=ProductDTO, status_code=201)
def create_product(
    company_id: UUID,
    request: CreateProductRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
    codes: SqlProductCodeGenerator = Depends(get_code_generator),
    stock: SqlProductStockGateway = Depends(get_stock_gateway),
) -> ProductDTO:
    return CreateProduct(repo, codes, stock).execute(
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
        barcode=request.barcode,
        image_url=request.image_url,
        custom_attributes=request.custom_attributes,
        initial_stock=request.initial_stock,
    )


@router.post("/import", response_model=ImportProductsResultDTO)
def import_products(
    company_id: UUID,
    request: ImportProductsRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    products: ProductRepository = Depends(get_product_repository),
    categories: CategoryRepository = Depends(get_category_repository),
    codes: SqlProductCodeGenerator = Depends(get_code_generator),
    stock: SqlProductStockGateway = Depends(get_stock_gateway),
    uow: SqlUnitOfWork = Depends(get_unit_of_work),
) -> ImportProductsResultDTO:
    rows = [ProductImportRow(**r.model_dump()) for r in request.rows]
    return ImportProducts(
        products=products, categories=categories, codes=codes, stock=stock, uow=uow
    ).execute(company_id, rows, update_existing=request.update_existing)


@router.get("/{product_id}", response_model=ProductDTO)
def get_product(
    company_id: UUID,
    product_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    return GetProduct(repo).execute(product_id, company_id)


@router.patch("/{product_id}", response_model=ProductDTO)
def update_product(
    company_id: UUID,
    product_id: UUID,
    request: UpdateProductRequest,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> ProductDTO:
    return UpdateProduct(repo).execute(company_id, product_id, request.model_dump(exclude_unset=True))


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
    company_id: UUID,
    product_id: UUID,
    _: AuthenticatedUser = Depends(require_company_access),
    repo: ProductRepository = Depends(get_product_repository),
) -> MessageResponse:
    DeleteProduct(repo).execute(product_id, company_id)
    return MessageResponse(message="Producto eliminado")


@router.get("/{product_id}/timeline", response_model=ProductTimelineDTO)
def get_product_timeline(
    company_id: UUID,
    product_id: UUID,
    limit: int = Query(150, ge=10, le=1000, description="Max events per kind"),
    _: AuthenticatedUser = Depends(require_company_access),
    query: SqlProductTimelineQuery = Depends(get_timeline_query),
) -> ProductTimelineDTO:
    return query.execute(company_id, product_id, limit=limit)


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
    return MessageResponse(message="Categoría eliminada")

import uuid
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, Awaitable, Any, cast
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.bootstrap.routers import api_router
from app.config import settings
from app.shared.domain.errors import (
    DomainError, NotFoundError, ConflictError, 
    ValidationError, UnauthorizedError, ForbiddenError
)
from app.shared.presentation.schemas import ErrorResponse
from app.shared.infrastructure.database.database import engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection successful.")
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed at startup: {e}")
        # Note: We don't raise here, we allow the app to start (it will report degraded health)
    
    # Optional: Ping FTGM here later
    yield
    
    # Shutdown
    engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Plataforma Web de Soporte de Decisiones para la Optimización de Inventarios mediante Predicción de Demanda y Análisis de KPIs basado en el Modelo FTGM en MYPEs retail de Lima Metropolitana.",
        version="0.1.0",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "System", "description": "System health and status endpoints."},
            {"name": "Auth", "description": "Authentication and authorization."},
            {"name": "Companies", "description": "Company management."},
            {"name": "Products", "description": "Product catalog and SKUs."},
            {"name": "Sales", "description": "Sales history and data."},
            {"name": "Inventory", "description": "Current stock and movements."},
            {"name": "Forecasting", "description": "FTGM forecasting runs and results."},
            {"name": "KPIs", "description": "Key performance indicators."},
            {"name": "Recommendations", "description": "Actionable replenishment recommendations."},
        ]
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID Logging Middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> JSONResponse:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        # In a real app, bind the request_id to contextvars for logging
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return cast(JSONResponse, response)

    # Global Exception Handlers
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump()
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump()
        )
        
    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump()
        )
        
    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump()
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred.").model_dump()
        )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app

app = create_app()


from fastapi import FastAPI

from app.bootstrap.routers import api_router
from app.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Plataforma Web de Soporte de Decisiones para la Optimización de Inventarios mediante Predicción de Demanda y Análisis de KPIs basado en el Modelo FTGM en MYPEs retail de Lima Metropolitana.",
        version="0.1.0",
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

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app

app = create_app()

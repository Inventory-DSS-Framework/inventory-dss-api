from fastapi import APIRouter

from app.shared.presentation.health_router import router as health_router

api_router = APIRouter()

api_router.include_router(health_router)

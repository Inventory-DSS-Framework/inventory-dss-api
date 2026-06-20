from fastapi import FastAPI

from app.bootstrap.routers import api_router
from app.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0"
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app

app = create_app()

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.shared.infrastructure.database.database import get_db
from app.shared.presentation.schemas import PlaceholderResponse
from pydantic import BaseModel
from typing import Dict

router = APIRouter(tags=["System"])

class HealthResponse(BaseModel):
    status: str
    database: str

class StatusResponse(BaseModel):
    status: str
    dependencies: Dict[str, str]

class VersionResponse(BaseModel):
    version: str

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Basic health check endpoint that verifies database connectivity."""
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        db_status = "unreachable"
        
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status
    )

@router.get("/status", response_model=StatusResponse)
def system_status(db: Session = Depends(get_db)) -> StatusResponse:
    """More detailed status endpoint checking various dependencies."""
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        db_status = "unreachable"
        
    # FTGM Ping (Simulated for this block, as it doesn't break startup)
    ftgm_status = "unknown (not implemented)"
    
    return StatusResponse(
        status="ok" if db_status == "ok" else "degraded",
        dependencies={
            "database": db_status,
            "ftgm_engine": ftgm_status
        }
    )

@router.get("/version", response_model=VersionResponse)
def system_version() -> VersionResponse:
    """Returns the current API version."""
    # Hardcoded for now, could be read from pyproject.toml
    return VersionResponse(version="0.1.0")

@router.get("/metadata", response_model=PlaceholderResponse)
def metadata() -> PlaceholderResponse:
    return PlaceholderResponse(
        message="Endpoint scaffold ready",
        module="system",
        action="get_metadata"
    )


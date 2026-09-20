from typing import Annotated, Any, List
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    app_name: str = "Inventory DSS API"
    app_env: str = "development"
    # When true SQLAlchemy echoes every SQL statement — very noisy, keep it opt-in.
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/inventory_dss"

    # CORS
    cors_origins: Annotated[List[str], NoDecode] = Field(default=["http://localhost:3000"])
    # Optional regex to allow dynamic origins (e.g. Vercel preview deploys):
    # CORS_ORIGIN_REGEX=https://.*\.vercel\.app
    cors_origin_regex: str = ""

    # Security / JWT
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7 # 7 days

    # FTGM Engine
    ftgm_engine_base_url: str = "http://localhost:8010/api/v1"
    # "real" calls the deployed FTGM engine; "mock" answers locally with demo-grade
    # predictions (no engine needed) — see adapters/mock_ftgm.py.
    ftgm_engine_mode: str = "real"
    ftgm_engine_timeout_seconds: int = 120
    # Seasonal period the engine forecasts on (12 = monthly). Drives day->period mapping.
    ftgm_seasonal_period: int = 12

    # Storage
    # Backend for uploaded files: "db" keeps bytes in Postgres (survives restarts /
    # ephemeral disks on Render/Railway free tiers); "local" writes to storage_root.
    storage_backend: str = "db"
    storage_root: str = "./storage"
    max_upload_size_mb: int = 10
    allowed_upload_mime_types: Annotated[List[str], NoDecode] = Field(default=["text/csv", "application/vnd.ms-excel"])

    # Email / SMTP
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    emails_from_email: str = "info@example.com"
    emails_from_name: str = "Inventory DSS"

    @field_validator("cors_origins", "allowed_upload_mime_types", mode="before")
    @classmethod
    def _split_csv(cls, value: Any) -> Any:
        """Parse comma-separated env vars (e.g. CORS_ORIGINS=http://a,http://b) into a list."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: Any) -> Any:
        """Coerce managed-Postgres URLs to the psycopg (v3) driver.

        Render/Neon/Railway hand out ``postgres://`` or ``postgresql://`` URLs, but
        SQLAlchemy needs an explicit ``postgresql+psycopg://`` driver. Leave URLs that
        already specify a driver (``postgresql+...``) untouched.
        """
        if isinstance(value, str):
            if value.startswith("postgresql+"):
                return value
            if value.startswith("postgresql://"):
                return "postgresql+psycopg://" + value[len("postgresql://"):]
            if value.startswith("postgres://"):
                return "postgresql+psycopg://" + value[len("postgres://"):]
        return value

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

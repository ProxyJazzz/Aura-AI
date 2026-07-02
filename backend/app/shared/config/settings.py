"""
Application settings loaded from environment variables.

Uses Pydantic BaseSettings for type-safe configuration with .env file support.
All settings are centralized here — no hardcoded values elsewhere in the codebase.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "AURA AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI Recruitment Intelligence Platform — Hiring Beyond Keywords."
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Server ───────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── API ──────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/aura.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"

    # ── Database (future) ────────────────────────────────────────
    DATABASE_URL: Optional[str] = None

    # ── Security (future) ────────────────────────────────────────
    ALLOWED_HOSTS: list[str] = ["*"]
    SECRET_KEY: str = "aura-dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once, reused everywhere."""
    return Settings()


settings = get_settings()

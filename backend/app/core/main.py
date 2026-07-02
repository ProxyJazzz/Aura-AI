"""
AURA AI — Application Entry Point

FastAPI application factory with lifespan management, middleware registration,
router inclusion, and CORS configuration.

Run with:
    uvicorn app.core.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.shared.config.settings import settings
from app.shared.logging import setup_logging
from app.shared.exceptions import register_exception_handlers
from app.shared.middleware import RequestLoggingMiddleware
from app.shared.database import get_db_connection
from app.modules.health.service import HealthService
from app.modules.health.api import router as health_router
from app.modules.candidates import candidates_router, dataset_router
from app.modules.jobs import jobs_router
from app.modules.semantic import semantic_router
from app.modules.features import features_router
from app.modules.ranking import ranking_router
from app.modules.decision import decision_router
from app.modules.intelligence import intelligence_router
from app.modules.export import export_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — runs on startup and shutdown."""
    # ── Startup ──────────────────────────────────────────────
    setup_logging()
    logger.info("Starting {name} v{version}", name=settings.APP_NAME, version=settings.APP_VERSION)
    logger.info("Environment: {env}", env=settings.APP_ENV)
    logger.info("API prefix: {prefix}", prefix=settings.API_V1_PREFIX)
    logger.info("CORS origins: {origins}", origins=settings.CORS_ORIGINS)

    yield

    # ── Shutdown ─────────────────────────────────────────────
    logger.info("Shutting down {name}", name=settings.APP_NAME)


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""

    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── Rate Limiting ────────────────────────────────────────
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(SlowAPIMiddleware)

    # ── CORS ─────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ── Trusted Hosts ────────────────────────────────────────
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    # ── GZip Compression ─────────────────────────────────────
    application.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
    )

    # ── Custom Middleware ────────────────────────────────────
    application.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ───────────────────────────────────
    register_exception_handlers(application)

    # ── Root Endpoints ───────────────────────────────────────
    @application.get("/health", tags=["System"])
    async def root_health():
        """Top-level health check endpoint for monitoring."""
        return HealthService.check()

    @application.get("/ready", tags=["System"])
    async def root_ready():
        """Readiness check verifying database connectivity."""
        try:
            with get_db_connection() as conn:
                conn.execute("SELECT 1;")
            return {"status": "ready"}
        except Exception as e:
            logger.error("Readiness check failed: {err}", err=str(e))
            raise HTTPException(
                status_code=503,
                detail=f"Database connection failed: {str(e)}"
            )

    @application.get("/version", tags=["System"])
    async def root_version():
        """Retrieve application version information."""
        return {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV
        }

    # ── Routers ──────────────────────────────────────────────
    application.include_router(health_router, prefix=settings.API_V1_PREFIX)
    application.include_router(candidates_router, prefix=settings.API_V1_PREFIX)
    application.include_router(dataset_router, prefix=settings.API_V1_PREFIX)
    application.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
    application.include_router(semantic_router, prefix=settings.API_V1_PREFIX)
    application.include_router(features_router, prefix=settings.API_V1_PREFIX)
    application.include_router(ranking_router, prefix=settings.API_V1_PREFIX)
    application.include_router(decision_router, prefix=settings.API_V1_PREFIX)
    application.include_router(intelligence_router, prefix=settings.API_V1_PREFIX)
    application.include_router(export_router, prefix=settings.API_V1_PREFIX)

    return application






app = create_app()

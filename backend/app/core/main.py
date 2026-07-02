"""
AURA AI — Application Entry Point

FastAPI application factory with lifespan management, middleware registration,
router inclusion, and CORS configuration.

Run with:
    uvicorn app.core.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.shared.config.settings import settings
from app.shared.logging import setup_logging
from app.shared.exceptions import register_exception_handlers
from app.shared.middleware import RequestLoggingMiddleware
from app.modules.health.api import router as health_router
from app.modules.candidates import candidates_router, dataset_router
from app.modules.jobs import jobs_router


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

    # ── CORS ─────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ── Custom Middleware ────────────────────────────────────
    application.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ───────────────────────────────────
    register_exception_handlers(application)

    # ── Routers ──────────────────────────────────────────────
    application.include_router(health_router, prefix=settings.API_V1_PREFIX)
    application.include_router(candidates_router, prefix=settings.API_V1_PREFIX)
    application.include_router(dataset_router, prefix=settings.API_V1_PREFIX)
    application.include_router(jobs_router, prefix=settings.API_V1_PREFIX)

    return application




app = create_app()

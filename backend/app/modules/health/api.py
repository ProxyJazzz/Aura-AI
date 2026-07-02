"""
Health check API router.

Provides a single endpoint for monitoring application health.
Used by load balancers, uptime monitors, and deployment health checks.
"""

from fastapi import APIRouter

from app.modules.health.schema import HealthResponse
from app.modules.health.service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns application health status, version, and environment.",
)
async def health_check() -> HealthResponse:
    """Check if the application is running and healthy."""
    return HealthService.check()

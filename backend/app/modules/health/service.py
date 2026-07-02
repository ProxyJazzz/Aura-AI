"""
Health check service.

Constructs the health check response with application metadata.
"""

from datetime import datetime, timezone

from app.shared.config.settings import settings
from app.modules.health.schema import HealthResponse


class HealthService:
    """Service responsible for health check logic."""

    @staticmethod
    def check() -> HealthResponse:
        """Return current application health status."""
        return HealthResponse(
            success=True,
            status="healthy",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.APP_ENV,
            timestamp=datetime.now(timezone.utc),
        )

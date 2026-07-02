"""
Health check response schemas.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    success: bool = Field(default=True, description="Request success status")
    status: str = Field(default="healthy", description="Application health status")
    app_name: str = Field(description="Application name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Current environment (development/production)")
    timestamp: datetime = Field(description="Server timestamp at time of response")

    model_config = {"json_schema_extra": {
        "example": {
            "success": True,
            "status": "healthy",
            "app_name": "AURA AI",
            "version": "1.0.0",
            "environment": "development",
            "timestamp": "2026-07-02T00:00:00Z",
        }
    }}

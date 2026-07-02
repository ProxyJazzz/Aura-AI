import pytest
from fastapi.testclient import TestClient

from app.core.main import app
from app.shared.config.settings import settings
from app.shared.database import get_db_connection

client = TestClient(app)


def test_app_startup():
    """Verify that the FastAPI application factory boots successfully."""
    assert app.title == settings.APP_NAME
    assert app.version == settings.APP_VERSION


def test_configuration_loading():
    """Verify that settings are loaded properly from env/defaults."""
    assert settings.APP_NAME == "AURA AI"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert "sqlite" in settings.DATABASE_URL


def test_database_connection():
    """Verify database connectivity helper executes successfully."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT 1;")
        res = cursor.fetchone()
        assert res[0] == 1


def test_root_health_endpoint():
    """Verify GET /health returns 200 and valid health payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert data["app_name"] == settings.APP_NAME


def test_root_ready_endpoint():
    """Verify GET /ready returns 200 when database is responsive."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_root_version_endpoint():
    """Verify GET /version returns app version details."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["app_name"] == settings.APP_NAME

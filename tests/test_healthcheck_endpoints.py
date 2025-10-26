import pytest
from fastapi import status
from datetime import datetime


class TestHealthCheckEndpoints:
    """Test suite for healthcheck-related endpoints."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, get_async_client):
        """Test successful health check when all dependencies are healthy."""
        client = get_async_client
        response = await client.get("/api/v1/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "dependencies" in data

        # Check status values
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert isinstance(data["version"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

        # Check timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO 8601 format")

        # Check dependencies structure
        dependencies = data["dependencies"]
        assert isinstance(dependencies, dict)

        # Check database dependency (should be present)
        if "database" in dependencies:
            db_dep = dependencies["database"]
            assert "name" in db_dep
            assert "status" in db_dep
            assert "timestamp" in db_dep
            assert db_dep["name"] == "database"
            assert db_dep["status"] in ["healthy", "unhealthy"]

            # If healthy, should have latency
            if db_dep["status"] == "healthy":
                assert "latency_ms" in db_dep
                assert isinstance(db_dep["latency_ms"], (int, float))
                assert db_dep["latency_ms"] >= 0
                assert db_dep["error"] is None
            else:
                # If unhealthy, should have error message
                assert "error" in db_dep
                assert db_dep["error"] is not None

    @pytest.mark.asyncio
    async def test_health_check_method_not_allowed(self, get_async_client):
        """Test that health check endpoint only accepts GET requests."""
        client = get_async_client
        # Test POST method
        response = await client.post("/api/v1/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Test PUT method
        response = await client.put("/api/v1/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Test DELETE method
        response = await client.delete("/api/v1/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.config.settings import settings
from app.healthcheck.v1.schemas import HealthCheckResponse, HealthStatus
from app.healthcheck.v1.service import HealthCheckService

router = APIRouter(prefix="/v1", tags=["Healthcheck"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="System Health Check",
    description="""
    Comprehensive health check endpoint that verifies the status of all critical dependencies.

    - **database**: PostgreSQL database connection

    Returns overall system status and detailed dependency information.
    """,
    responses={
        200: {
            "description": "System is healthy or degraded",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "timestamp": "2023-10-05T12:34:56.789Z",
                        "uptime_seconds": 12345.67,
                        "dependencies": {
                            "database": {
                                "name": "database",
                                "status": "healthy",
                                "latency_ms": 12.5,
                                "error": None,
                                "timestamp": "2023-10-05T12:34:56.789Z",
                            },
                        },
                    },
                },
            },
        },
        503: {
            "description": "System is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "version": "1.0.0",
                        "timestamp": "2023-10-05T12:34:56.789Z",
                        "uptime_seconds": 12345.67,
                        "dependencies": {
                            "database": {
                                "name": "database",
                                "status": "unhealthy",
                                "latency_ms": None,
                                "error": "Connection timeout",
                                "timestamp": "2023-10-05T12:34:56.789Z",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def health_check() -> HealthCheckResponse:
    health_service = HealthCheckService()

    dependencies = await health_service.perform_health_check()

    overall_status = health_service.determine_overall_status(dependencies)

    response = HealthCheckResponse(
        status=overall_status,
        version=settings.version,
        timestamp=datetime.now(tz=timezone.utc),
        uptime_seconds=health_service.get_uptime(),
        dependencies={dep.name: dep for dep in dependencies.values()},
    )

    if overall_status == HealthStatus.UNHEALTHY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump(),
        )
    elif overall_status == HealthStatus.DEGRADED:
        return response

    return response

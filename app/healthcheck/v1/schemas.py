from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class DependencyStatus(BaseModel):
    name: str = Field(..., description="Name of the dependency (e.g., database, redis)")
    status: HealthStatus = Field(..., description="Health status of dependency")
    latency_ms: Optional[float] = Field(
        None,
        description="Response latency in milliseconds",
    )
    error: Optional[str] = Field(
        None,
        description="Error message if dependency is unhealthy",
    )
    timestamp: datetime = Field(..., description="Time when check was performed")


class HealthCheckResponse(BaseModel):
    status: HealthStatus = Field(..., description="Overall system health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Time when check was performed")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    dependencies: dict[str, DependencyStatus] = Field(
        ...,
        description="Status of all dependencies",
    )

    model_config = {
        "json_schema_extra": {
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
                    "redis": {
                        "name": "redis",
                        "status": "unhealthy",
                        "latency_ms": None,
                        "error": "Connection timeout",
                        "timestamp": "2023-10-05T12:34:56.789Z",
                    },
                },
            },
        },
    }

import asyncio
import time
from datetime import datetime, timezone

from sqlalchemy import text

from app.config.database import database
from app.healthcheck.v1.schemas import DependencyStatus, HealthStatus


class HealthCheckService:
    def __init__(self):
        self.start_time = time.time()

    def get_uptime(self) -> float:
        return time.time() - self.start_time

    @staticmethod
    async def check_database() -> DependencyStatus:
        start_time = time.time()
        try:
            async with database.get_session() as session:
                await session.execute(text("SELECT 1"))
            latency_ms = (time.time() - start_time) * 1000
            return DependencyStatus(
                name="database",
                status=HealthStatus.HEALTHY,
                latency_ms=round(latency_ms, 2),
                error=None,
                timestamp=datetime.now(tz=timezone.utc),
            )
        except Exception as e:
            return DependencyStatus(
                name="database",
                status=HealthStatus.UNHEALTHY,
                latency_ms=None,
                error=str(e),
                timestamp=datetime.now(tz=timezone.utc),
            )

    async def perform_health_check(self) -> dict[str, DependencyStatus]:
        results = await asyncio.gather(
            self.check_database(),
            return_exceptions=True,
        )

        dependencies: dict[str, DependencyStatus] = {}
        checks = [
            "database",
        ]

        for i, result in enumerate(results):
            dep_name = checks[i]
            if isinstance(result, Exception):
                dependencies[dep_name] = DependencyStatus(
                    name=dep_name,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=None,
                    error=f"Health check failed: {str(result)}",
                    timestamp=datetime.now(tz=timezone.utc),
                )
            else:
                assert isinstance(result, DependencyStatus)
                dependencies[dep_name] = result

        return dependencies

    @staticmethod
    def determine_overall_status(
        dependencies: dict[str, DependencyStatus],
    ) -> HealthStatus:
        statuses = [dep.status for dep in dependencies.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

import uvicorn
from fastapi import FastAPI
from app.config.settings import settings

from dishka.integrations.fastapi import setup_dishka
from app.container import container
from app.config.logger import get_logger
from app.api.v1.routers import router
from app.healthcheck.v1.router import router as healthcheck_router
from app.exceptions import register_error_handlers


logger = get_logger(__name__)


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        debug=settings.debug,
        root_path="/api",
        description="Wallet API service",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    register_error_handlers(app=app)
    setup_dishka(container, app)
    app.include_router(router=router)
    app.include_router(router=healthcheck_router)
    return app


app = create_application()


def start_uvicorn() -> None:
    """Start the Uvicorn server with production configuration."""
    config = uvicorn.Config(
        "app.main:app",
        port=settings.app_port,
        loop="uvloop",  # Use uvloop for better performance
        http="httptools",  # Use httptools for better HTTP parsing
    )

    server = uvicorn.Server(config)
    server.run()

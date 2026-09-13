from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exceptions import register_exception_handlers
from app.api.routers import register_routers
from app.core.logging import configure_logging
from app.settings import APP_SETTINGS


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="Subsurface Data Platform API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=APP_SETTINGS.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    register_exception_handlers(app)
    register_routers(app)

    @app.get("/health", tags=["Health"], summary="Liveness probe")
    def health() -> dict[str, str]:
        """Unauthenticated liveness check for Compose."""
        return {"status": "ok"}

    return app


app = create_app()

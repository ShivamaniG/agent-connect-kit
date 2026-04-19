from fastapi import FastAPI

from agent_connect_kit import __version__
from agent_connect_kit.config import get_settings
from agent_connect_kit.logging_config import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Agent Connect Kit",
        version=__version__,
        description="Connector gateway for AI agents.",
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "env": settings.app_env}

    log.info("app.started", env=settings.app_env, version=__version__)
    return app


app = create_app()

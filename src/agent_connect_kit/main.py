from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from agent_connect_kit import __version__
from agent_connect_kit.config import get_settings
from agent_connect_kit.connections.routes import router as connections_router
from agent_connect_kit.connectors import get_connectors
from agent_connect_kit.db import get_session
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

    @app.get("/health/db")
    async def health_db(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar_one()
        return {"status": "ok" if value == 1 else "error", "database": "up"}

    @app.get("/connectors")
    async def list_connectors() -> list[dict]:
        return [
            {
                "name": connector.name,
                "actions": [
                    {
                        "name": action.name,
                        "description": action.description,
                        "parameters": action.parameters,
                    }
                    for action in connector.actions()
                ],
            }
            for connector in get_connectors().values()
        ]

    app.include_router(connections_router)

    log.info("app.started", env=settings.app_env, version=__version__)
    return app


app = create_app()

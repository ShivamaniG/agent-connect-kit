import httpx
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from agent_connect_kit.config import get_settings
from agent_connect_kit.connectors import get_actions
from agent_connect_kit.db import get_session
from agent_connect_kit.runtime.errors import (
    ActionNotFound,
    ProviderNotConfigured,
    UserNotConnected,
)
from agent_connect_kit.runtime.executor import execute


async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = get_settings().api_key
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


router = APIRouter(tags=["actions"])


@router.get("/actions", dependencies=[Depends(require_api_key)])
async def list_available_actions() -> list[dict]:
    return [
        {
            "name": action.name,
            "description": action.description,
            "parameters": action.parameters,
        }
        for action in get_actions().values()
    ]


@router.post("/actions/{action_name}", dependencies=[Depends(require_api_key)])
async def run_action(
    action_name: str,
    payload: dict = Body(...),
    session: AsyncSession = Depends(get_session),
) -> dict:
    user_id = payload.get("user_id")
    args = payload.get("args", {}) or {}

    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=400, detail="user_id (string) is required")
    if not isinstance(args, dict):
        raise HTTPException(status_code=400, detail="args must be an object")

    try:
        return await execute(action_name, user_id, args, session)
    except ActionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UserNotConnected as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"upstream {exc.response.status_code}: {exc.response.text[:500]}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"upstream error: {exc}") from exc

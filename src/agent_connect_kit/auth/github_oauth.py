from typing import Any
from urllib.parse import urlencode

import httpx

from agent_connect_kit.config import get_settings

AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"


def _scopes() -> str:
    raw = get_settings().github_oauth_scopes
    return " ".join(s.strip() for s in raw.split(",") if s.strip())


def build_authorize_url(state: str) -> str:
    settings = get_settings()
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_redirect_uri,
        "scope": _scopes(),
        "state": state,
        "allow_signup": "false",
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code(code: str) -> dict[str, Any]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_redirect_uri,
            },
        )
        response.raise_for_status()
        return response.json()


async def fetch_user(access_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            USER_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        response.raise_for_status()
        return response.json()

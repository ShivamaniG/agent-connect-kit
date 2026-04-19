import asyncio
from typing import Any

import httpx

from agent_connect_kit.logging_config import get_logger

log = get_logger(__name__)

DISCORD_API = "https://discord.com/api/v10"
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
RETRY_STATUS = {429, 500, 502, 503, 504}


def _headers(bot_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
        "User-Agent": "agent-connect-kit/0.1 (+https://github.com/ShivamaniG/agent-connect-kit)",
    }


def _backoff(attempt: int) -> float:
    return min(BACKOFF_BASE_SECONDS * (2**attempt), MAX_BACKOFF_SECONDS)


def _retry_after(response: httpx.Response) -> float | None:
    header = response.headers.get("Retry-After")
    if not header:
        return None
    try:
        return min(float(header), MAX_BACKOFF_SECONDS)
    except ValueError:
        return None


async def request(
    method: str,
    path: str,
    bot_token: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> Any:
    """Call the Discord REST API with bot auth and retry/backoff."""
    url = path if path.startswith("http") else f"{DISCORD_API}{path}"
    last_error: Exception | None = None

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=_headers(bot_token),
                )
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt == MAX_RETRIES:
                    raise
                delay = _backoff(attempt)
                log.warning(
                    "discord.retry.transport_error",
                    attempt=attempt + 1,
                    delay_s=delay,
                    error=str(exc),
                )
                await asyncio.sleep(delay)
                continue

            if response.status_code in RETRY_STATUS and attempt < MAX_RETRIES:
                delay = _retry_after(response) or _backoff(attempt)
                log.warning(
                    "discord.retry.status",
                    status=response.status_code,
                    attempt=attempt + 1,
                    delay_s=delay,
                )
                await asyncio.sleep(delay)
                continue

            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

    raise last_error or RuntimeError("discord request failed without response")

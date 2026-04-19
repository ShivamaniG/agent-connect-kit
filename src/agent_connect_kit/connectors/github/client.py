import asyncio
import time
from typing import Any

import httpx

from agent_connect_kit.logging_config import get_logger

log = get_logger(__name__)

GITHUB_API = "https://api.github.com"
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
RETRY_STATUS = {429, 500, 502, 503, 504}


def _headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "agent-connect-kit/0.1",
    }


def _delay_for_attempt(attempt: int) -> float:
    return min(BACKOFF_BASE_SECONDS * (2**attempt), MAX_BACKOFF_SECONDS)


def _rate_limit_delay(response: httpx.Response) -> float | None:
    """Derive a delay from GitHub's rate-limit headers, else None."""
    retry_after = response.headers.get("Retry-After")
    if retry_after and retry_after.isdigit():
        return min(float(retry_after), MAX_BACKOFF_SECONDS)

    remaining = response.headers.get("X-RateLimit-Remaining")
    reset = response.headers.get("X-RateLimit-Reset")
    if remaining == "0" and reset and reset.isdigit():
        wait = float(reset) - time.time()
        return min(max(wait, 1.0), MAX_BACKOFF_SECONDS)

    return None


async def request(
    method: str,
    path: str,
    access_token: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> Any:
    """Call the GitHub API with retries on transient errors and rate limits."""
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    last_error: Exception | None = None

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=_headers(access_token),
                )
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt == MAX_RETRIES:
                    raise
                delay = _delay_for_attempt(attempt)
                log.warning(
                    "github.retry.transport_error",
                    attempt=attempt + 1,
                    delay_s=delay,
                    error=str(exc),
                )
                await asyncio.sleep(delay)
                continue

            if response.status_code in RETRY_STATUS and attempt < MAX_RETRIES:
                delay = _rate_limit_delay(response) or _delay_for_attempt(attempt)
                log.warning(
                    "github.retry.status",
                    status=response.status_code,
                    attempt=attempt + 1,
                    delay_s=delay,
                )
                await asyncio.sleep(delay)
                continue

            # GitHub signals primary rate limit with 403 + X-RateLimit-Remaining=0.
            if (
                response.status_code == 403
                and response.headers.get("X-RateLimit-Remaining") == "0"
                and attempt < MAX_RETRIES
            ):
                delay = _rate_limit_delay(response) or _delay_for_attempt(attempt)
                log.warning(
                    "github.retry.rate_limited",
                    attempt=attempt + 1,
                    delay_s=delay,
                )
                await asyncio.sleep(delay)
                continue

            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

    raise last_error or RuntimeError("github request failed without response")

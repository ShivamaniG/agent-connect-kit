import base64
import hashlib
import hmac
import secrets
import time

from agent_connect_kit.config import get_settings

DEFAULT_TTL_SECONDS = 600


def _secret() -> bytes:
    return get_settings().app_secret.encode()


def create_state(user_external_id: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
    nonce = secrets.token_urlsafe(16)
    expires_at = int(time.time()) + ttl_seconds
    payload = f"{expires_at}|{nonce}|{user_external_id}".encode()
    sig = hmac.new(_secret(), payload, hashlib.sha256).digest()
    return (
        base64.urlsafe_b64encode(payload).decode().rstrip("=")
        + "."
        + base64.urlsafe_b64encode(sig).decode().rstrip("=")
    )


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def verify_state(state: str) -> str:
    try:
        payload_b64, sig_b64 = state.split(".")
    except ValueError as exc:
        raise ValueError("malformed state") from exc

    payload = _b64decode(payload_b64)
    sig = _b64decode(sig_b64)
    expected = hmac.new(_secret(), payload, hashlib.sha256).digest()

    if not hmac.compare_digest(sig, expected):
        raise ValueError("invalid signature")

    expires_at_str, _nonce, user_external_id = payload.decode().split("|", 2)
    if int(time.time()) > int(expires_at_str):
        raise ValueError("state expired")

    return user_external_id

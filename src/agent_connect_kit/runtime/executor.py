import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_connect_kit.auth.tokens import decrypt
from agent_connect_kit.connectors import get_action
from agent_connect_kit.db.models import ActionLog, Connection, User
from agent_connect_kit.logging_config import get_logger
from agent_connect_kit.runtime.context import ActionContext
from agent_connect_kit.runtime.errors import ActionNotFound, UserNotConnected

log = get_logger(__name__)


def _summarize(result: Any) -> str:
    if isinstance(result, list):
        return f"{len(result)} items"
    if isinstance(result, dict):
        return f"dict with {len(result)} keys"
    return str(result)[:200]


async def execute(
    action_name: str,
    user_external_id: str,
    args: dict,
    session: AsyncSession,
) -> dict:
    action = get_action(action_name)
    if action is None:
        raise ActionNotFound(action_name)

    provider = action_name.split(".", 1)[0]

    user = (
        await session.execute(select(User).where(User.external_id == user_external_id))
    ).scalar_one_or_none()
    if user is None:
        raise UserNotConnected(user_external_id, provider)

    conn = (
        await session.execute(
            select(Connection).where(
                Connection.user_id == user.id,
                Connection.provider == provider,
            )
        )
    ).scalar_one_or_none()
    if conn is None:
        raise UserNotConnected(user_external_id, provider)

    ctx = ActionContext(
        provider=provider,
        access_token=decrypt(conn.encrypted_access_token),
        user_id=user.id,
        user_external_id=user_external_id,
        connection_id=conn.id,
    )

    start = time.perf_counter()
    log_entry = ActionLog(
        user_id=user.id,
        connection_id=conn.id,
        action_name=action_name,
        args=args,
        status="pending",
    )

    try:
        result = await action.handler(ctx, args)
    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        log_entry.status = "error"
        log_entry.latency_ms = latency_ms
        log_entry.error = f"{type(exc).__name__}: {str(exc)[:2000]}"
        session.add(log_entry)
        await session.commit()
        log.warning(
            "action.failed",
            action=action_name,
            user=user_external_id,
            error=log_entry.error,
            latency_ms=latency_ms,
        )
        raise

    latency_ms = int((time.perf_counter() - start) * 1000)
    log_entry.status = "success"
    log_entry.latency_ms = latency_ms
    log_entry.result_summary = _summarize(result)
    session.add(log_entry)
    await session.commit()

    log.info(
        "action.succeeded",
        action=action_name,
        user=user_external_id,
        summary=log_entry.result_summary,
        latency_ms=latency_ms,
    )

    return {
        "status": "success",
        "action": action_name,
        "latency_ms": latency_ms,
        "result": result,
    }

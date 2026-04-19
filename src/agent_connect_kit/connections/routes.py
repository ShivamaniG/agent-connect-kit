from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_connect_kit.auth.github_oauth import build_authorize_url, exchange_code, fetch_user
from agent_connect_kit.auth.state import create_state, verify_state
from agent_connect_kit.auth.tokens import encrypt
from agent_connect_kit.db import get_session
from agent_connect_kit.db.models import Connection, User
from agent_connect_kit.logging_config import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get("/github/start")
async def github_start(
    user_id: str = Query(..., description="External user identifier"),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    result = await session.execute(select(User).where(User.external_id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(external_id=user_id)
        session.add(user)
        await session.commit()
        log.info("user.created", external_id=user_id)

    state = create_state(user_id)
    return RedirectResponse(url=build_authorize_url(state), status_code=302)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    try:
        user_external_id = verify_state(state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"invalid state: {exc}") from exc

    token_data = await exchange_code(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail=f"oauth error: {token_data.get('error_description') or token_data}",
        )
    scopes = token_data.get("scope", "")

    gh_user = await fetch_user(access_token)

    result = await session.execute(select(User).where(User.external_id == user_external_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail="user not found")

    result = await session.execute(
        select(Connection).where(
            Connection.user_id == user.id,
            Connection.provider == "github",
        )
    )
    conn = result.scalar_one_or_none()

    encrypted = encrypt(access_token)
    if conn is None:
        conn = Connection(
            user_id=user.id,
            provider="github",
            encrypted_access_token=encrypted,
            scopes=scopes,
            external_account_id=str(gh_user.get("id")) if gh_user.get("id") else None,
            external_account_login=gh_user.get("login"),
        )
        session.add(conn)
    else:
        conn.encrypted_access_token = encrypted
        conn.scopes = scopes
        conn.external_account_id = str(gh_user.get("id")) if gh_user.get("id") else None
        conn.external_account_login = gh_user.get("login")

    await session.commit()

    log.info(
        "connection.stored",
        user_external_id=user_external_id,
        provider="github",
        github_login=gh_user.get("login"),
        scopes=scopes,
    )

    github_login = gh_user.get("login", "unknown")
    return HTMLResponse(
        f"""
        <html>
          <head><title>GitHub connected</title></head>
          <body style="font-family: system-ui, sans-serif; padding: 40px; max-width: 520px;">
            <h2>GitHub connected</h2>
            <p>User <code>{user_external_id}</code> is now connected as
               <b>{github_login}</b>.</p>
            <p>Scopes: <code>{scopes}</code></p>
            <p>You can close this window.</p>
          </body>
        </html>
        """
    )


@router.get("")
async def list_connections(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    result = await session.execute(select(Connection))
    connections = result.scalars().all()
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "provider": c.provider,
            "external_account_login": c.external_account_login,
            "scopes": c.scopes,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in connections
    ]

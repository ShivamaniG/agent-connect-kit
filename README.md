# Agent Connect Kit

Open-source connector gateway for AI agents and copilots.

Build internal copilots and embed AI assistants once, then connect them to **GitHub**, **Discord**, and other tools through a REST API and MCP-compatible interfaces. Ships with **2 connectors and 37 actions** out of the box.

---

## Why this exists

AI engineers can build agents, but connecting them to real tools is still painful. Everyone rebuilds OAuth, token storage, permissions, tool schemas, retries, logging, and per-user connection management for the same apps.

Agent Connect Kit turns that integration layer into a reusable platform, so you can focus on workflows instead of plumbing.

---

## What ships out of the box

| | Connector | Actions | Auth model |
|---|---|---|---|
| 🟦 | **GitHub** | 22 — repos, issues, PRs, files, search, commits, stars, notifications, users, orgs | Per-user OAuth; encrypted tokens in Postgres |
| 🟪 | **Discord** | 10 — send message, list guilds, list channels, read messages, add reaction | Silent bot token; one bot per gateway |

Both connectors go through the same runtime — same retry logic, same audit log, same MCP exposure.

### Also included

- **MCP server (stdio)** — all 37 actions exposed as MCP tools for Claude Desktop, Cursor, VS Code Copilot, and Codex CLI.
- **REST API** with `X-API-Key` auth, exponential-backoff retries, rate-limit handling.
- **Local development** via `docker compose`: API, Postgres, Alembic migrations.
- **Audit log** (`action_logs` table) records every call with args, result summary, latency, and status.
- **Extensible** — adding a new connector is ~40 lines per action using the shared `Action` interface.

---

## Who this is for

- AI engineers building internal copilots.
- SaaS startups embedding AI assistants into their products.
- Independent devs who want self-hostable connector infrastructure instead of stitching together custom integrations for every agent project.

---

## Quickstart — 3 minutes to a working gateway

### 1. Register a GitHub OAuth App (optional but recommended)

Go to https://github.com/settings/applications/new and fill in:

- **Application name**: `Agent Connect Kit (local dev)`
- **Homepage URL**: `http://localhost:8000`
- **Authorization callback URL**: `http://localhost:8000/connections/github/callback`

Copy the **Client ID** and generate a **Client Secret**.

### 2. Register a Discord bot (optional but recommended)

Go to https://discord.com/developers/applications → **New Application** → **Bot** tab → **Reset Token** → copy it.

Then **OAuth2 → URL Generator**:
- Scope: `bot`
- Permissions: Send Messages, View Channels, Read Message History, Add Reactions

Open the generated URL, pick your server, **Authorize**.

### 3. Configure and start the stack

```bash
git clone https://github.com/ShivamaniG/agent-connect-kit
cd agent-connect-kit
cp .env.example .env
```

Edit `.env` and fill in:
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` (from step 1)
- `DISCORD_BOT_TOKEN` (from step 2)
- `APP_SECRET` — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `API_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`

```bash
docker compose up -d --build
docker compose exec api uv run alembic upgrade head
curl http://localhost:8000/health
```

Expect `{"status":"ok","version":"0.1.0","env":"development"}`.

### 4. Connect a GitHub user once

Open in your browser (pick any identifier for `user_id` and reuse it everywhere):

```
http://localhost:8000/connections/github/start?user_id=shiva
```

Click **Authorize**. The encrypted token is now stored.

### 5. Call an action

**GitHub — list your repos:**
```bash
curl -s -X POST http://localhost:8000/actions/github.list_repos \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"shiva","args":{"per_page":5}}'
```

**Discord — list servers your bot is in:**
```bash
curl -s -X POST http://localhost:8000/actions/discord.list_guilds \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"shiva","args":{}}'
```

**Discord — post a message:**
```bash
curl -s -X POST http://localhost:8000/actions/discord.send_message \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"shiva","args":{"channel_id":"YOUR_CHANNEL_ID","content":"hello from the gateway"}}'
```

Every call is audited in the `action_logs` table.

---

## Connect your agent

All 37 actions are callable via **REST** or **MCP**. Pick your integration.

### Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "agent-connect-kit": {
      "command": "docker",
      "args": [
        "exec", "-i",
        "-e", "ACK_USER_ID=shiva",
        "agentconnectkit-api-1",
        "uv", "run", "python", "-m", "agent_connect_kit.mcp"
      ]
    }
  }
}
```

Fully quit Claude Desktop (system tray → Quit) and reopen. The 🔌 icon should show `agent-connect-kit · 37 tools`.

### Cursor

Save to `.cursor/mcp.json` in your project (or global `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "agent-connect-kit": {
      "command": "docker",
      "args": [
        "exec", "-i",
        "-e", "ACK_USER_ID=shiva",
        "agentconnectkit-api-1",
        "uv", "run", "python", "-m", "agent_connect_kit.mcp"
      ]
    }
  }
}
```

Reload Cursor (`Ctrl+Shift+P` → Reload Window).

### GitHub Copilot in VS Code

Enable `chat.mcp.enabled` in VS Code settings, then create `.vscode/mcp.json`:

```json
{
  "servers": {
    "agent-connect-kit": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "exec", "-i",
        "-e", "ACK_USER_ID=shiva",
        "agentconnectkit-api-1",
        "uv", "run", "python", "-m", "agent_connect_kit.mcp"
      ]
    }
  }
}
```

Reload Window. In Copilot Chat, switch to **Agent** mode → 37 tools appear.

### OpenAI Codex CLI

Edit `~/.codex/config.toml` (Linux/macOS) or `C:\Users\<you>\.codex\config.toml` (Windows):

```toml
[mcp_servers.agent-connect-kit]
command = "docker"
args = ["exec", "-i", "-e", "ACK_USER_ID=shiva", "agentconnectkit-api-1", "uv", "run", "python", "-m", "agent_connect_kit.mcp"]
```

Restart Codex.

### Custom agent (REST, any language)

```python
import httpx

GATEWAY = "http://localhost:8000"
API_KEY = "..."
USER_ID = "shiva"

# Discover tools
tools = httpx.get(f"{GATEWAY}/actions", headers={"X-API-Key": API_KEY}).json()

# Execute one — GitHub
repos = httpx.post(
    f"{GATEWAY}/actions/github.list_repos",
    headers={"X-API-Key": API_KEY},
    json={"user_id": USER_ID, "args": {"per_page": 5}},
).json()

# Execute one — Discord
httpx.post(
    f"{GATEWAY}/actions/discord.send_message",
    headers={"X-API-Key": API_KEY},
    json={"user_id": USER_ID, "args": {"channel_id": "...", "content": "hi"}},
)
```

---

## How it works

```
Agent / SDK / MCP client
        │
        │  REST or MCP stdio
        ▼
┌─────────────────────────────────┐
│       Agent Connect Kit         │
│ ┌─────────────────────────────┐ │
│ │  Action runtime (executor)  │ │  validate → fetch creds → call → log
│ └─────────┬───────────────────┘ │
│ ┌─────────▼───────────────────┐ │
│ │     Connector registry      │ │  GitHub (per-user OAuth)
│ │                             │ │  Discord (service bot token)
│ └─────────┬───────────────────┘ │
│           │                     │
│  Postgres │  Connections (encrypted tokens)
│           │  ActionLog    (every call audited)
└───────────┼─────────────────────┘
            ▼
   GitHub API / Discord API / ...
```

Two credential patterns are supported:

- **Per-user OAuth** (GitHub) — each end user connects their own account via browser. Tokens are encrypted with Fernet and stored in Postgres.
- **Service credentials** (Discord bot) — one provider-wide token in `.env`. Useful when the agent acts as itself (e.g., a bot in a server) rather than on behalf of individual users.

Adding a new connector is ~40 lines per action via the `Action` dataclass + registry pattern.

---

## Architecture

- **Backend**: FastAPI + uvicorn, Python 3.12
- **Package manager**: `uv`
- **Database**: Postgres 16, SQLAlchemy 2.0 async, Alembic migrations
- **HTTP client**: `httpx` async, shared retry/backoff helpers per provider
- **Validation**: Pydantic v2
- **Crypto**: `cryptography.Fernet` for token encryption at rest
- **MCP**: official `mcp` Python SDK (stdio)
- **Logging**: `structlog` JSON on stderr
- **Packaging**: `docker-compose` (api + postgres)

---

## Roadmap

### Shipped
- GitHub connector (22 actions)
- Discord connector (10 actions)
- MCP stdio server
- REST API with audit logging
- Self-host via docker compose

### Next
- **More Discord actions** — threads, roles, voice state, message edits
- **Microsoft Teams connector** — Graph API + token refresh
- **Approval workflows** — human-in-the-loop for sensitive writes
- **HTTP MCP transport** — for multi-user hosted deployments
- **Python SDK** — typed wrapper over REST
- **Admin dashboard** — view connections, revoke tokens, browse audit log

---

## Contributing

Contributions, issues, and design feedback are welcome. The connector pattern is designed so you can add a new provider without touching the runtime — see `src/agent_connect_kit/connectors/discord/` for the smallest complete example.

---

## License

MIT.

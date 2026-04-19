# Agent Connect Kit

Open-source connector gateway that lets AI copilots and agentic apps securely connect to external tools like GitHub and Discord through a simple REST API and MCP-compatible interface. Ships with two connectors and 27 actions out of the box.

## Why this exists

AI engineers can build good agents, but connecting them to real tools is still painful. Every team ends up rebuilding OAuth, token handling, permission mapping, tool schemas, retries, logging, and per-user connection management for the same apps.

Agent Connect Kit aims to make that layer reusable.

## Vision

Build the developer-first connectivity layer for AI agents.

The first goal is simple:
- Connect a user account to GitHub.
- Expose GitHub actions as safe tools.
- Let any agent framework call those tools through MCP or a Python SDK.
- Extend the same pattern to Microsoft Teams and other workplace tools.

## Who this is for

- AI engineers building internal copilots.
- SaaS startups embedding AI assistants into their products.
- Developers who want self-hostable connector infrastructure instead of stitching together custom integrations for every agent project.

## Problem statement

Today, agent builders often have to solve the same integration problems repeatedly:
- OAuth setup and callback flows.
- Access token storage and refresh.
- Per-user account connections.
- Tool schema definition.
- API retries and rate-limit handling.
- Safe execution and permission boundaries.
- Tracing, logs, and auditability.

This project turns those repeated tasks into a reusable platform.

## Initial product direction

Agent Connect Kit starts as an open-source, self-hostable connector gateway focused on internal copilots.

### Phase 1 (shipped)
- **GitHub connector** — 22 actions across repos, issues, PRs, files, search, commits, stars, notifications, users, orgs. Per-user OAuth with encrypted token storage.
- **Discord connector** — 5 actions (send message, list guilds, list channels, get channel messages, add reaction). Silent-bot pattern via `DISCORD_BOT_TOKEN`.
- **MCP server** (stdio) — all actions exposed as MCP tools for Claude Desktop, Cursor, VS Code Copilot, Codex CLI.
- REST API with `X-API-Key` auth, retries, rate-limit handling.
- Local development via `docker compose`, Postgres + Alembic migrations.
- Per-call audit log (`action_logs` table) with args, status, latency.

### Phase 2 (roadmap)
- Microsoft Teams connector.
- Approval workflows for agent actions.
- Fine-grained connector permissions.
- Better dashboard and policy controls.

## Quickstart

Run the gateway locally in ~3 minutes.

### 1. Register a GitHub OAuth App

Go to https://github.com/settings/applications/new and fill in:

- **Application name**: `Agent Connect Kit (local dev)`
- **Homepage URL**: `http://localhost:8000`
- **Authorization callback URL**: `http://localhost:8000/connections/github/callback`

After registering, copy the **Client ID** and generate a **Client Secret**.

### 2. Configure and start the stack

```bash
git clone https://github.com/ShivamaniG/agent-connect-kit
cd agent-connect-kit
cp .env.example .env
# Edit .env and fill in:
#   GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
#   APP_SECRET   (generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
#   API_KEY      (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")

docker compose up -d --build
docker compose exec api uv run alembic upgrade head
curl http://localhost:8000/health
```

Expect `{"status":"ok","version":"0.1.0","env":"development"}`.

### 3a. Connect a GitHub account once

Open in your browser (replace `shiva` with any identifier you'll use consistently):

```
http://localhost:8000/connections/github/start?user_id=shiva
```

Click **Authorize**. Your encrypted GitHub token is now stored.

### 3b. Set up the Discord bot

Discord uses a **silent bot** pattern — one bot per gateway, shared across users. Skip this section if you only want GitHub.

1. Go to https://discord.com/developers/applications → **New Application**.
2. Bot tab → **Reset Token** → copy the token.
3. OAuth2 → URL Generator → tick `bot` scope and the permissions you need (Send Messages, View Channels, Read Message History, Add Reactions, etc.). Copy the generated URL, open it, pick your server, **Authorize**.
4. Add to `.env`:
   ```
   DISCORD_BOT_TOKEN=your-bot-token
   ```
5. Recreate the API container so it picks up the env var:
   ```bash
   docker compose up -d --force-recreate api
   ```

Verify: `curl -X POST http://localhost:8000/actions/discord.list_guilds -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" -d '{"user_id":"shiva","args":{}}'` should return your server.

### 4. Call an action

```bash
curl -s -X POST http://localhost:8000/actions/github.list_repos \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"shiva","args":{"per_page":5}}'
```

Real repos come back. Every call is audited in the `action_logs` table.

## Connect your agent

The gateway exposes all actions via **REST** and an **MCP server** (stdio). Pick your integration below.

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

Fully quit Claude Desktop (system tray → Quit) and reopen. The plug icon at the bottom of the chat will show `agent-connect-kit · 27 tools`.

### Cursor

Save to `.cursor/mcp.json` in your project, or global `~/.cursor/mcp.json`:

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

1. In VS Code settings, enable `chat.mcp.enabled`.
2. Create `.vscode/mcp.json`:

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

3. Reload Window. In Copilot Chat, switch to **Agent** mode — 27 tools appear under the tools icon.

### OpenAI Codex CLI

Edit `~/.codex/config.toml` (or `C:\Users\<you>\.codex\config.toml`):

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

# Execute one
result = httpx.post(
    f"{GATEWAY}/actions/github.list_repos",
    headers={"X-API-Key": API_KEY},
    json={"user_id": USER_ID, "args": {"per_page": 5}},
).json()
```

### Notes

- Every MCP integration uses the same `docker exec ... python -m agent_connect_kit.mcp` command. The MCP server reuses the REST action runtime, so all logs and audit rows are identical across surfaces.
- `ACK_USER_ID` in the MCP client's env pins the session to a single end user. One MCP client config = one user's actions.
- For multi-user or remote deployments, an HTTP transport variant is planned.

## Contributing

Contributions, ideas, and design feedback will be welcome once the first scaffold is stable.

## License

Planned: MIT
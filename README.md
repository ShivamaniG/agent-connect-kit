# Agent Connect Kit

Open-source connector gateway that lets AI copilots and agentic apps securely connect to external tools like GitHub and Microsoft Teams through a simple SDK and MCP-compatible interface.

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

### Phase 1
- GitHub connector.
- Python SDK.
- MCP server mode.
- Local development workflow.
- Connection management and execution logs.

### Phase 2
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

### 3. Connect a GitHub account once

Open in your browser (replace `shiva` with any identifier you'll use consistently):

```
http://localhost:8000/connections/github/start?user_id=shiva
```

Click **Authorize**. Your encrypted GitHub token is now stored.

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

Fully quit Claude Desktop (system tray → Quit) and reopen. The plug icon at the bottom of the chat will show `agent-connect-kit · 22 tools`.

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

3. Reload Window. In Copilot Chat, switch to **Agent** mode — 22 tools appear under the tools icon.

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

## Core ideas

### 1. Connector abstraction
Every external app is represented through a standard connector interface.

Example actions:
- `github_list_repos`
- `github_get_issues`
- `github_create_issue`
- `teams_send_message`
- `teams_create_approval_request`

### 2. User-scoped auth
Each end user connects their own account. The platform stores connection metadata and credentials securely, then executes tool calls on behalf of that user.

### 3. MCP + SDK access
Developers should be able to use this project in two ways:
- as an MCP server for agent frameworks and IDEs,
- as a direct SDK for Python applications.

### 4. Safety and observability
Every action should be validated, logged, and auditable.

## MVP scope

The first useful version should support:

- GitHub OAuth connection flow.
- Persisted connections in PostgreSQL.
- Two to four GitHub actions.
- MCP tool exposure for those actions.
- A simple Python SDK.
- Basic logs for action execution.

## Proposed architecture

```text
Frontend / Agent / App
        |
        |  SDK or MCP
        v
+---------------------------+
|   Agent Connect Kit API   |
|---------------------------|
| OAuth / Connections       |
| Connector Registry        |
| Action Runtime            |
| Logging / Audit Layer     |
| MCP Adapter               |
+---------------------------+
        |
        +--> GitHub API
        |
        +--> Microsoft Teams / Graph API
```

## Suggested tech stack

- Backend: FastAPI
- Database: PostgreSQL
- Validation: Pydantic
- HTTP client: httpx
- Optional cache/queue: Redis
- Auth: OAuth 2.0 provider integrations
- Packaging: Python-first
- Future UI: React or Next.js admin dashboard

## Proposed repo structure

```text
agent-connect-kit/
├── README.md
├── pyproject.toml
├── .env.example
├── docker-compose.yml
├── src/
│   └── agent_connect_kit/
│       ├── main.py
│       ├── config.py
│       ├── db/
│       ├── auth/
│       ├── connections/
│       ├── connectors/
│       │   ├── base.py
│       │   ├── github/
│       │   └── teams/
│       ├── runtime/
│       ├── mcp/
│       ├── sdk/
│       └── logging/
├── examples/
│   ├── python_agent_example.py
│   └── mcp_client_example.md
├── docs/
│   ├── architecture.md
│   ├── connector-spec.md
│   └── roadmap.md
└── tests/
```

## Milestones

### Milestone 1: Foundation
- Create project structure.
- Add FastAPI app.
- Add database models for users, providers, connections, and action logs.
- Define connector base classes.

### Milestone 2: GitHub vertical slice
- Add GitHub OAuth connect + callback flow.
- Store GitHub user connection.
- Implement `list_repos`.
- Implement `create_issue`.
- Add action execution logs.

### Milestone 3: MCP support
- Expose GitHub actions as MCP tools.
- Add tool discovery.
- Add tool execution handler.
- Add example agent integration.

### Milestone 4: Teams connector
- Add Teams auth flow.
- Implement `send_message`.
- Add approval-friendly workflow patterns.

### Milestone 5: Developer experience
- Improve docs.
- Add dashboard.
- Add policy controls and better permissions.
- Package for open-source adoption.

## Non-goals for v1

To keep scope realistic, v1 should not include:
- 10+ connectors.
- Marketplace or billing.
- Enterprise SSO.
- Complex workflow builder.
- Full multi-tenant SaaS control plane.

## Why this can stand out

The goal is not to compete immediately on connector count. The goal is to provide a clean, open-source, MCP-friendly developer experience for agent connectivity, starting with a narrow but highly useful workflow: GitHub + workplace communication tools.

## Naming notes

Current working name: **Agent Connect Kit**

Possible alternatives:
- ConnectorKit
- MCP Connect
- Agent Bridge
- ToolMesh
- ConnectLayer

## Roadmap summary

Short term:
- Build GitHub-first MVP.
- Support MCP and Python SDK.
- Open-source the repo with examples.

Medium term:
- Add Teams.
- Add permission controls.
- Add approval workflows.

Long term:
- Add more workplace connectors.
- Add hosted control plane if adoption appears.
- Become the default connector layer for internal copilots.

## Contributing

Contributions, ideas, and design feedback will be welcome once the first scaffold is stable.

## License

Planned: MIT
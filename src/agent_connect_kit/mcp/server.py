import json
import os
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from agent_connect_kit import __version__
from agent_connect_kit.connectors import get_actions
from agent_connect_kit.db.session import get_session_factory
from agent_connect_kit.logging_config import configure_logging, get_logger
from agent_connect_kit.runtime.errors import ActionNotFound, UserNotConnected
from agent_connect_kit.runtime.executor import execute

configure_logging()
log = get_logger(__name__)

SERVER_NAME = "agent-connect-kit"
USER_ID_ENV = "ACK_USER_ID"


def _mcp_tool_name(action_name: str) -> str:
    """Convert 'github.list_repos' -> 'github_list_repos' for MCP compatibility."""
    return action_name.replace(".", "_")


def _build_tool_map() -> dict[str, str]:
    """Map MCP-safe tool names back to internal action names."""
    return {_mcp_tool_name(name): name for name in get_actions().keys()}


server: Server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    tools: list[Tool] = []
    for action in get_actions().values():
        tools.append(
            Tool(
                name=_mcp_tool_name(action.name),
                description=action.description,
                inputSchema=action.parameters,
            )
        )
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    tool_map = _build_tool_map()
    if name not in tool_map:
        return [TextContent(type="text", text=json.dumps({"error": f"unknown tool: {name}"}))]

    action_name = tool_map[name]
    user_id = os.environ.get(USER_ID_ENV)
    if not user_id:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"{USER_ID_ENV} env var is required on the MCP server"}),
            )
        ]

    factory = get_session_factory()
    async with factory() as session:
        try:
            result = await execute(action_name, user_id, arguments or {}, session)
        except (ActionNotFound, UserNotConnected) as exc:
            return [TextContent(type="text", text=json.dumps({"error": str(exc)}))]
        except Exception as exc:
            log.error(
                "mcp.call_tool.error",
                tool=name,
                action=action_name,
                error=f"{type(exc).__name__}: {exc}",
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"{type(exc).__name__}: {exc}"}),
                )
            ]

    return [
        TextContent(
            type="text",
            text=json.dumps(result, default=str, indent=2),
        )
    ]


async def run_stdio() -> None:
    log.info(
        "mcp.starting",
        transport="stdio",
        user_env=USER_ID_ENV,
        tool_count=len(get_actions()),
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

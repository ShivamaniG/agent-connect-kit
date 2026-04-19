"""Smoke-test the stdio MCP server by connecting as a client and listing tools.

Usage (inside the api container):
    ACK_USER_ID=shiva uv run python scripts/check_mcp.py
"""
import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> int:
    user_id = os.environ.get("ACK_USER_ID", "smoke-test-user")
    params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "agent_connect_kit.mcp"],
        env={"ACK_USER_ID": user_id, "PATH": os.environ.get("PATH", "")},
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"connected to MCP server; {len(tools.tools)} tools exposed:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

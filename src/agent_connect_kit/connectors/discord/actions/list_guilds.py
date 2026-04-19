from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.discord.client import request
from agent_connect_kit.runtime.context import ActionContext


async def list_guilds(ctx: ActionContext, args: dict) -> list[dict]:
    data = await request("GET", "/users/@me/guilds", ctx.access_token)
    return [
        {
            "id": g["id"],
            "name": g["name"],
            "icon": g.get("icon"),
            "owner": g.get("owner", False),
            "permissions": g.get("permissions"),
        }
        for g in data
    ]


list_guilds_action = Action(
    name="discord.list_guilds",
    description="List Discord servers (guilds) the bot is a member of.",
    parameters={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    handler=list_guilds,
)

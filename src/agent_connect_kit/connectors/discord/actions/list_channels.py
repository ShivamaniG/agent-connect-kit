from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.discord.client import request
from agent_connect_kit.runtime.context import ActionContext

CHANNEL_TYPE_NAMES = {
    0: "text",
    2: "voice",
    4: "category",
    5: "announcement",
    10: "announcement_thread",
    11: "public_thread",
    12: "private_thread",
    13: "stage",
    15: "forum",
}


async def list_channels(ctx: ActionContext, args: dict) -> list[dict]:
    guild_id = str(args["guild_id"])
    data = await request("GET", f"/guilds/{guild_id}/channels", ctx.access_token)
    return [
        {
            "id": c["id"],
            "name": c.get("name"),
            "type": CHANNEL_TYPE_NAMES.get(c.get("type"), str(c.get("type"))),
            "type_id": c.get("type"),
            "parent_id": c.get("parent_id"),
            "position": c.get("position"),
            "topic": c.get("topic"),
            "nsfw": c.get("nsfw", False),
        }
        for c in data
    ]


list_channels_action = Action(
    name="discord.list_channels",
    description="List channels in a Discord server (guild).",
    parameters={
        "type": "object",
        "properties": {
            "guild_id": {
                "type": "string",
                "description": "Discord server (guild) ID.",
            },
        },
        "required": ["guild_id"],
        "additionalProperties": False,
    },
    handler=list_channels,
)

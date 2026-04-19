from urllib.parse import quote

from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.discord.client import request
from agent_connect_kit.runtime.context import ActionContext


async def add_reaction(ctx: ActionContext, args: dict) -> dict:
    channel_id = str(args["channel_id"])
    message_id = str(args["message_id"])
    emoji = args["emoji"]
    encoded = quote(emoji, safe="")
    await request(
        "PUT",
        f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me",
        ctx.access_token,
    )
    return {
        "channel_id": channel_id,
        "message_id": message_id,
        "emoji": emoji,
        "reacted": True,
    }


add_reaction_action = Action(
    name="discord.add_reaction",
    description="Add a reaction (emoji) to a Discord message as the bot.",
    parameters={
        "type": "object",
        "properties": {
            "channel_id": {"type": "string", "description": "Discord channel ID."},
            "message_id": {"type": "string", "description": "Target message ID."},
            "emoji": {
                "type": "string",
                "description": (
                    "Unicode emoji character (e.g. a thumbs-up) or custom emoji "
                    "in 'name:id' form."
                ),
                "minLength": 1,
            },
        },
        "required": ["channel_id", "message_id", "emoji"],
        "additionalProperties": False,
    },
    handler=add_reaction,
)

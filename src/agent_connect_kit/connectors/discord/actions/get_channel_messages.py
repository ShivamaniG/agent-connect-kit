from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.discord.client import request
from agent_connect_kit.runtime.context import ActionContext


async def get_channel_messages(ctx: ActionContext, args: dict) -> list[dict]:
    channel_id = str(args["channel_id"])
    params: dict = {"limit": min(max(int(args.get("limit", 50)), 1), 100)}
    for key in ("before", "after", "around"):
        if args.get(key):
            params[key] = str(args[key])

    data = await request(
        "GET",
        f"/channels/{channel_id}/messages",
        ctx.access_token,
        params=params,
    )
    return [
        {
            "id": m["id"],
            "channel_id": m["channel_id"],
            "content": m.get("content"),
            "author": (m.get("author") or {}).get("username"),
            "author_id": (m.get("author") or {}).get("id"),
            "timestamp": m.get("timestamp"),
            "edited_timestamp": m.get("edited_timestamp"),
            "attachment_count": len(m.get("attachments", [])),
            "embed_count": len(m.get("embeds", [])),
            "reactions": [
                {"emoji": (r.get("emoji") or {}).get("name"), "count": r.get("count", 0)}
                for r in m.get("reactions", [])
            ],
        }
        for m in data
    ]


get_channel_messages_action = Action(
    name="discord.get_channel_messages",
    description=(
        "Read recent messages from a Discord channel (REST, no privileged intent required)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "channel_id": {
                "type": "string",
                "description": "Discord channel ID.",
            },
            "limit": {
                "type": "integer",
                "description": "Max messages to return (1-100).",
                "default": 50,
                "minimum": 1,
                "maximum": 100,
            },
            "before": {
                "type": "string",
                "description": "Only messages before this message ID.",
            },
            "after": {
                "type": "string",
                "description": "Only messages after this message ID.",
            },
            "around": {
                "type": "string",
                "description": "Messages around this message ID.",
            },
        },
        "required": ["channel_id"],
        "additionalProperties": False,
    },
    handler=get_channel_messages,
)

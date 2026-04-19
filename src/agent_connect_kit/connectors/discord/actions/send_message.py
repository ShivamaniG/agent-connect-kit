from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.discord.client import request
from agent_connect_kit.runtime.context import ActionContext


async def send_message(ctx: ActionContext, args: dict) -> dict:
    channel_id = str(args["channel_id"])
    payload: dict = {"content": args["content"]}
    if args.get("tts"):
        payload["tts"] = bool(args["tts"])

    data = await request(
        "POST",
        f"/channels/{channel_id}/messages",
        ctx.access_token,
        json=payload,
    )
    return {
        "id": data["id"],
        "channel_id": data["channel_id"],
        "content": data.get("content"),
        "timestamp": data.get("timestamp"),
        "author": (data.get("author") or {}).get("username"),
    }


send_message_action = Action(
    name="discord.send_message",
    description="Post a message to a Discord text channel as the bot.",
    parameters={
        "type": "object",
        "properties": {
            "channel_id": {
                "type": "string",
                "description": "Discord channel ID (right-click channel > Copy Channel ID).",
            },
            "content": {
                "type": "string",
                "description": "Message content (plain text or Markdown).",
                "minLength": 1,
                "maxLength": 2000,
            },
            "tts": {
                "type": "boolean",
                "description": "Send as text-to-speech.",
                "default": False,
            },
        },
        "required": ["channel_id", "content"],
        "additionalProperties": False,
    },
    handler=send_message,
)

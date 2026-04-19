from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def list_notifications(ctx: ActionContext, args: dict) -> list[dict]:
    params: dict = {
        "all": "true" if args.get("all") else "false",
        "participating": "true" if args.get("participating") else "false",
        "per_page": min(int(args.get("per_page", 30)), 50),
        "page": max(int(args.get("page", 1)), 1),
    }
    if args.get("since"):
        params["since"] = args["since"]
    if args.get("before"):
        params["before"] = args["before"]

    data = await request("GET", "/notifications", ctx.access_token, params=params)
    return [
        {
            "id": n["id"],
            "unread": n.get("unread", True),
            "reason": n.get("reason"),
            "updated_at": n.get("updated_at"),
            "last_read_at": n.get("last_read_at"),
            "subject_type": n.get("subject", {}).get("type"),
            "subject_title": n.get("subject", {}).get("title"),
            "subject_url": n.get("subject", {}).get("url"),
            "repo": n.get("repository", {}).get("full_name"),
        }
        for n in data
    ]


list_notifications_action = Action(
    name="github.list_notifications",
    description=(
        "List GitHub notifications for the authenticated user. "
        "Requires the 'notifications' OAuth scope."
    ),
    parameters={
        "type": "object",
        "properties": {
            "all": {
                "type": "boolean",
                "description": "Include read notifications.",
                "default": False,
            },
            "participating": {
                "type": "boolean",
                "description": "Only notifications where the user is directly involved.",
                "default": False,
            },
            "since": {"type": "string", "description": "ISO 8601 timestamp lower bound."},
            "before": {"type": "string", "description": "ISO 8601 timestamp upper bound."},
            "per_page": {"type": "integer", "default": 30, "minimum": 1, "maximum": 50},
            "page": {"type": "integer", "default": 1, "minimum": 1},
        },
        "additionalProperties": False,
    },
    handler=list_notifications,
)

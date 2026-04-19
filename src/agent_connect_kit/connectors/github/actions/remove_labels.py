from urllib.parse import quote

from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def remove_labels(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    number = int(args["issue_number"])
    labels: list[str] = args["labels"]

    remaining: list[dict] | None = None
    for label in labels:
        path = f"/repos/{repo}/issues/{number}/labels/{quote(label, safe='')}"
        remaining = await request("DELETE", path, ctx.access_token)

    return {
        "removed": labels,
        "remaining": [label["name"] for label in (remaining or [])],
    }


remove_labels_action = Action(
    name="github.remove_labels",
    description="Remove one or more labels from an issue or pull request.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "issue_number": {"type": "integer", "minimum": 1},
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        },
        "required": ["repo", "issue_number", "labels"],
        "additionalProperties": False,
    },
    handler=remove_labels,
)

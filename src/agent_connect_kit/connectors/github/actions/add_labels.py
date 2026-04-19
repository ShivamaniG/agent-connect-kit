from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def add_labels(ctx: ActionContext, args: dict) -> list[dict]:
    repo = args["repo"]
    number = int(args["issue_number"])
    labels = args["labels"]

    data = await request(
        "POST",
        f"/repos/{repo}/issues/{number}/labels",
        ctx.access_token,
        json={"labels": labels},
    )
    return [{"name": label["name"], "color": label.get("color")} for label in data]


add_labels_action = Action(
    name="github.add_labels",
    description="Add one or more labels to an issue or pull request.",
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
    handler=add_labels,
)

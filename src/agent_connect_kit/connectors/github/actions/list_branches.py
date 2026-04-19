from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def list_branches(ctx: ActionContext, args: dict) -> list[dict]:
    repo = args["repo"]
    params: dict = {
        "per_page": min(int(args.get("per_page", 30)), 100),
        "page": max(int(args.get("page", 1)), 1),
    }
    if args.get("protected") is not None:
        params["protected"] = "true" if args["protected"] else "false"

    data = await request("GET", f"/repos/{repo}/branches", ctx.access_token, params=params)
    return [
        {
            "name": b["name"],
            "commit_sha": b.get("commit", {}).get("sha"),
            "protected": b.get("protected", False),
        }
        for b in data
    ]


list_branches_action = Action(
    name="github.list_branches",
    description="List branches on a GitHub repository.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "protected": {
                "type": "boolean",
                "description": "If set, filter by protected status.",
            },
            "per_page": {"type": "integer", "default": 30, "minimum": 1, "maximum": 100},
            "page": {"type": "integer", "default": 1, "minimum": 1},
        },
        "required": ["repo"],
        "additionalProperties": False,
    },
    handler=list_branches,
)

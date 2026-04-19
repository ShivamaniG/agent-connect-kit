from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def list_prs(ctx: ActionContext, args: dict) -> list[dict]:
    repo = args["repo"]
    params: dict = {
        "state": args.get("state", "open"),
        "sort": args.get("sort", "created"),
        "direction": args.get("direction", "desc"),
        "per_page": min(int(args.get("per_page", 30)), 100),
        "page": max(int(args.get("page", 1)), 1),
    }
    if args.get("head"):
        params["head"] = args["head"]
    if args.get("base"):
        params["base"] = args["base"]

    data = await request("GET", f"/repos/{repo}/pulls", ctx.access_token, params=params)
    return [
        {
            "number": p["number"],
            "title": p["title"],
            "state": p["state"],
            "draft": p.get("draft", False),
            "html_url": p["html_url"],
            "user": p.get("user", {}).get("login"),
            "head_ref": p.get("head", {}).get("ref"),
            "base_ref": p.get("base", {}).get("ref"),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
            "merged_at": p.get("merged_at"),
        }
        for p in data
    ]


list_prs_action = Action(
    name="github.list_prs",
    description="List pull requests on a GitHub repository.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
            "head": {"type": "string", "description": "user:branch filter."},
            "base": {"type": "string", "description": "Base branch filter."},
            "sort": {
                "type": "string",
                "enum": ["created", "updated", "popularity", "long-running"],
                "default": "created",
            },
            "direction": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
            "per_page": {"type": "integer", "default": 30, "minimum": 1, "maximum": 100},
            "page": {"type": "integer", "default": 1, "minimum": 1},
        },
        "required": ["repo"],
        "additionalProperties": False,
    },
    handler=list_prs,
)

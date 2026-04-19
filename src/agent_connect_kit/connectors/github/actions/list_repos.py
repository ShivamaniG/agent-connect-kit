from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def list_repos(ctx: ActionContext, args: dict) -> list[dict]:
    data = await request(
        "GET",
        "/user/repos",
        ctx.access_token,
        params={
            "per_page": min(int(args.get("per_page", 30)), 100),
            "page": max(int(args.get("page", 1)), 1),
            "sort": args.get("sort", "updated"),
            "visibility": args.get("visibility", "all"),
        },
    )
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "full_name": r["full_name"],
            "private": r.get("private", False),
            "html_url": r.get("html_url"),
            "description": r.get("description"),
            "language": r.get("language"),
            "stargazers_count": r.get("stargazers_count", 0),
            "fork": r.get("fork", False),
            "updated_at": r.get("updated_at"),
        }
        for r in data
    ]


list_repos_action = Action(
    name="github.list_repos",
    description="List repositories accessible to the authenticated GitHub user.",
    parameters={
        "type": "object",
        "properties": {
            "per_page": {
                "type": "integer",
                "description": "Repos per page (max 100).",
                "default": 30,
                "minimum": 1,
                "maximum": 100,
            },
            "page": {
                "type": "integer",
                "description": "Page number (1-indexed).",
                "default": 1,
                "minimum": 1,
            },
            "sort": {
                "type": "string",
                "description": "Sort field.",
                "enum": ["created", "updated", "pushed", "full_name"],
                "default": "updated",
            },
            "visibility": {
                "type": "string",
                "description": "Which repos to return.",
                "enum": ["all", "public", "private"],
                "default": "all",
            },
        },
        "additionalProperties": False,
    },
    handler=list_repos,
)

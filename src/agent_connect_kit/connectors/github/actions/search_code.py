from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def search_code(ctx: ActionContext, args: dict) -> dict:
    params = {
        "q": args["q"],
        "per_page": min(int(args.get("per_page", 30)), 100),
        "page": max(int(args.get("page", 1)), 1),
    }

    data = await request("GET", "/search/code", ctx.access_token, params=params)

    items = data.get("items", [])
    return {
        "total_count": data.get("total_count", 0),
        "incomplete_results": data.get("incomplete_results", False),
        "items": [
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "html_url": item.get("html_url"),
                "repo": item.get("repository", {}).get("full_name"),
                "sha": item.get("sha"),
            }
            for item in items
        ],
    }


search_code_action = Action(
    name="github.search_code",
    description=(
        "Search code across repositories accessible to the authenticated user. "
        "Query syntax: https://docs.github.com/en/search-github/searching-on-github/searching-code"
    ),
    parameters={
        "type": "object",
        "properties": {
            "q": {
                "type": "string",
                "description": (
                    "GitHub code search query, e.g. "
                    "'createUser language:python repo:owner/name'."
                ),
                "minLength": 1,
            },
            "per_page": {"type": "integer", "default": 30, "minimum": 1, "maximum": 100},
            "page": {"type": "integer", "default": 1, "minimum": 1},
        },
        "required": ["q"],
        "additionalProperties": False,
    },
    handler=search_code,
)

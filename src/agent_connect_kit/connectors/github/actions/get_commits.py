from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def get_commits(ctx: ActionContext, args: dict) -> list[dict]:
    repo = args["repo"]
    params: dict = {
        "per_page": min(int(args.get("per_page", 30)), 100),
        "page": max(int(args.get("page", 1)), 1),
    }
    for key in ("sha", "path", "author", "since", "until"):
        if args.get(key):
            params[key] = args[key]

    data = await request("GET", f"/repos/{repo}/commits", ctx.access_token, params=params)
    return [
        {
            "sha": c["sha"],
            "html_url": c.get("html_url"),
            "message": c.get("commit", {}).get("message"),
            "author_name": c.get("commit", {}).get("author", {}).get("name"),
            "author_email": c.get("commit", {}).get("author", {}).get("email"),
            "author_date": c.get("commit", {}).get("author", {}).get("date"),
            "committer_login": (c.get("committer") or {}).get("login"),
            "parents": [p["sha"] for p in c.get("parents", [])],
        }
        for c in data
    ]


get_commits_action = Action(
    name="github.get_commits",
    description="List commits on a GitHub repository (filter by sha, path, author, date range).",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "sha": {
                "type": "string",
                "description": "Branch, tag, or SHA to start from.",
            },
            "path": {
                "type": "string",
                "description": "Only commits touching this file path.",
            },
            "author": {
                "type": "string",
                "description": "Commit author login or email.",
            },
            "since": {"type": "string", "description": "ISO 8601 timestamp lower bound."},
            "until": {"type": "string", "description": "ISO 8601 timestamp upper bound."},
            "per_page": {"type": "integer", "default": 30, "minimum": 1, "maximum": 100},
            "page": {"type": "integer", "default": 1, "minimum": 1},
        },
        "required": ["repo"],
        "additionalProperties": False,
    },
    handler=get_commits,
)

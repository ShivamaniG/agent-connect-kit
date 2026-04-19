from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def get_issues(ctx: ActionContext, args: dict) -> list[dict]:
    repo = args["repo"]
    params: dict = {
        "state": args.get("state", "open"),
        "per_page": min(int(args.get("per_page", 30)), 100),
        "page": max(int(args.get("page", 1)), 1),
        "sort": args.get("sort", "created"),
        "direction": args.get("direction", "desc"),
    }
    if args.get("labels"):
        params["labels"] = args["labels"]
    if args.get("since"):
        params["since"] = args["since"]

    data = await request(
        "GET",
        f"/repos/{repo}/issues",
        ctx.access_token,
        params=params,
    )

    include_pulls = bool(args.get("include_pulls", False))
    issues = []
    for item in data:
        is_pr = "pull_request" in item
        if is_pr and not include_pulls:
            continue
        issues.append(
            {
                "number": item["number"],
                "title": item["title"],
                "state": item["state"],
                "html_url": item["html_url"],
                "user": item.get("user", {}).get("login"),
                "labels": [label["name"] for label in item.get("labels", [])],
                "comments": item.get("comments", 0),
                "is_pull_request": is_pr,
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            }
        )
    return issues


get_issues_action = Action(
    name="github.get_issues",
    description="List issues on a GitHub repository (excludes PRs by default).",
    parameters={
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": "Repository in 'owner/name' form.",
                "pattern": "^[^/]+/[^/]+$",
            },
            "state": {
                "type": "string",
                "enum": ["open", "closed", "all"],
                "default": "open",
            },
            "labels": {
                "type": "string",
                "description": "Comma-separated labels filter, e.g. 'bug,help wanted'.",
            },
            "since": {
                "type": "string",
                "description": "ISO 8601 timestamp; only issues updated after this.",
            },
            "sort": {
                "type": "string",
                "enum": ["created", "updated", "comments"],
                "default": "created",
            },
            "direction": {
                "type": "string",
                "enum": ["asc", "desc"],
                "default": "desc",
            },
            "per_page": {
                "type": "integer",
                "default": 30,
                "minimum": 1,
                "maximum": 100,
            },
            "page": {"type": "integer", "default": 1, "minimum": 1},
            "include_pulls": {
                "type": "boolean",
                "description": "Include pull requests in results (GitHub treats PRs as issues).",
                "default": False,
            },
        },
        "required": ["repo"],
        "additionalProperties": False,
    },
    handler=get_issues,
)

from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def create_issue(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    payload: dict = {"title": args["title"]}
    if args.get("body"):
        payload["body"] = args["body"]
    if args.get("labels"):
        payload["labels"] = args["labels"]
    if args.get("assignees"):
        payload["assignees"] = args["assignees"]

    data = await request(
        "POST",
        f"/repos/{repo}/issues",
        ctx.access_token,
        json=payload,
    )
    return {
        "number": data["number"],
        "title": data["title"],
        "state": data["state"],
        "html_url": data["html_url"],
        "user": data.get("user", {}).get("login"),
        "labels": [label["name"] for label in data.get("labels", [])],
        "created_at": data.get("created_at"),
    }


create_issue_action = Action(
    name="github.create_issue",
    description="Create an issue on a GitHub repository.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": "Repository in 'owner/name' form.",
                "pattern": "^[^/]+/[^/]+$",
            },
            "title": {
                "type": "string",
                "description": "Issue title.",
                "minLength": 1,
            },
            "body": {
                "type": "string",
                "description": "Issue body (Markdown).",
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional labels to apply.",
            },
            "assignees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional GitHub usernames to assign.",
            },
        },
        "required": ["repo", "title"],
        "additionalProperties": False,
    },
    handler=create_issue,
)

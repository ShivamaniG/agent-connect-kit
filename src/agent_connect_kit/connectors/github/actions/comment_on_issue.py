from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def comment_on_issue(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    number = int(args["issue_number"])
    data = await request(
        "POST",
        f"/repos/{repo}/issues/{number}/comments",
        ctx.access_token,
        json={"body": args["body"]},
    )
    return {
        "id": data["id"],
        "html_url": data["html_url"],
        "body": data["body"],
        "user": data.get("user", {}).get("login"),
        "created_at": data.get("created_at"),
    }


comment_on_issue_action = Action(
    name="github.comment_on_issue",
    description="Add a comment to a GitHub issue or pull request.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": "Repository in 'owner/name' form.",
                "pattern": "^[^/]+/[^/]+$",
            },
            "issue_number": {
                "type": "integer",
                "description": "Issue or PR number.",
                "minimum": 1,
            },
            "body": {
                "type": "string",
                "description": "Comment body (Markdown).",
                "minLength": 1,
            },
        },
        "required": ["repo", "issue_number", "body"],
        "additionalProperties": False,
    },
    handler=comment_on_issue,
)

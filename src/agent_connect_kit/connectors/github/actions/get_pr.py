from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def get_pr(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    number = int(args["number"])
    data = await request(
        "GET",
        f"/repos/{repo}/pulls/{number}",
        ctx.access_token,
    )
    return {
        "number": data["number"],
        "title": data["title"],
        "state": data["state"],
        "merged": data.get("merged", False),
        "draft": data.get("draft", False),
        "html_url": data["html_url"],
        "user": data.get("user", {}).get("login"),
        "head_ref": data.get("head", {}).get("ref"),
        "base_ref": data.get("base", {}).get("ref"),
        "body": data.get("body"),
        "commits": data.get("commits", 0),
        "additions": data.get("additions", 0),
        "deletions": data.get("deletions", 0),
        "changed_files": data.get("changed_files", 0),
        "mergeable": data.get("mergeable"),
        "mergeable_state": data.get("mergeable_state"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }


get_pr_action = Action(
    name="github.get_pr",
    description="Fetch details of a specific pull request by number.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": "Repository in 'owner/name' form.",
                "pattern": "^[^/]+/[^/]+$",
            },
            "number": {
                "type": "integer",
                "description": "Pull request number.",
                "minimum": 1,
            },
        },
        "required": ["repo", "number"],
        "additionalProperties": False,
    },
    handler=get_pr,
)

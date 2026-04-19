from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def assign_issue(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    number = int(args["issue_number"])
    assignees = args["assignees"]

    data = await request(
        "POST",
        f"/repos/{repo}/issues/{number}/assignees",
        ctx.access_token,
        json={"assignees": assignees},
    )
    return {
        "number": data["number"],
        "assignees": [u["login"] for u in data.get("assignees", [])],
        "html_url": data["html_url"],
    }


assign_issue_action = Action(
    name="github.assign_issue",
    description="Assign users to an issue or pull request.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "issue_number": {"type": "integer", "minimum": 1},
            "assignees": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "GitHub usernames to assign.",
            },
        },
        "required": ["repo", "issue_number", "assignees"],
        "additionalProperties": False,
    },
    handler=assign_issue,
)

from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def reopen_issue(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    number = int(args["number"])
    data = await request(
        "PATCH",
        f"/repos/{repo}/issues/{number}",
        ctx.access_token,
        json={"state": "open"},
    )
    return {
        "number": data["number"],
        "state": data["state"],
        "html_url": data["html_url"],
        "updated_at": data.get("updated_at"),
    }


reopen_issue_action = Action(
    name="github.reopen_issue",
    description="Reopen a closed issue.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "number": {"type": "integer", "minimum": 1},
        },
        "required": ["repo", "number"],
        "additionalProperties": False,
    },
    handler=reopen_issue,
)

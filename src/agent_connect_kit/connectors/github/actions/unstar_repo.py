from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def unstar_repo(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    await request("DELETE", f"/user/starred/{repo}", ctx.access_token)
    return {"repo": repo, "starred": False}


unstar_repo_action = Action(
    name="github.unstar_repo",
    description="Unstar a GitHub repository as the authenticated user.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "pattern": "^[^/]+/[^/]+$",
                "description": "Repository in 'owner/name' form.",
            },
        },
        "required": ["repo"],
        "additionalProperties": False,
    },
    handler=unstar_repo,
)

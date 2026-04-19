from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def create_pr(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    payload: dict = {
        "title": args["title"],
        "head": args["head"],
        "base": args["base"],
    }
    if args.get("body"):
        payload["body"] = args["body"]
    if args.get("draft") is not None:
        payload["draft"] = bool(args["draft"])
    if args.get("maintainer_can_modify") is not None:
        payload["maintainer_can_modify"] = bool(args["maintainer_can_modify"])

    data = await request("POST", f"/repos/{repo}/pulls", ctx.access_token, json=payload)
    return {
        "number": data["number"],
        "title": data["title"],
        "state": data["state"],
        "draft": data.get("draft", False),
        "html_url": data["html_url"],
        "head_ref": data.get("head", {}).get("ref"),
        "base_ref": data.get("base", {}).get("ref"),
        "created_at": data.get("created_at"),
    }


create_pr_action = Action(
    name="github.create_pr",
    description="Open a pull request on a GitHub repository.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "title": {"type": "string", "minLength": 1},
            "head": {
                "type": "string",
                "description": "Branch or 'user:branch' containing the changes.",
            },
            "base": {
                "type": "string",
                "description": "Branch to merge into (e.g. 'main').",
            },
            "body": {"type": "string", "description": "PR description (Markdown)."},
            "draft": {"type": "boolean", "default": False},
            "maintainer_can_modify": {"type": "boolean", "default": True},
        },
        "required": ["repo", "title", "head", "base"],
        "additionalProperties": False,
    },
    handler=create_pr,
)

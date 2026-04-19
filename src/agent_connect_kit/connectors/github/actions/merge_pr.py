from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def merge_pr(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    number = int(args["number"])
    payload: dict = {"merge_method": args.get("merge_method", "merge")}
    if args.get("commit_title"):
        payload["commit_title"] = args["commit_title"]
    if args.get("commit_message"):
        payload["commit_message"] = args["commit_message"]
    if args.get("sha"):
        payload["sha"] = args["sha"]

    data = await request(
        "PUT",
        f"/repos/{repo}/pulls/{number}/merge",
        ctx.access_token,
        json=payload,
    )
    return {
        "merged": data.get("merged", False),
        "message": data.get("message"),
        "sha": data.get("sha"),
    }


merge_pr_action = Action(
    name="github.merge_pr",
    description="Merge a pull request.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "number": {"type": "integer", "minimum": 1},
            "merge_method": {
                "type": "string",
                "enum": ["merge", "squash", "rebase"],
                "default": "merge",
            },
            "commit_title": {"type": "string"},
            "commit_message": {"type": "string"},
            "sha": {
                "type": "string",
                "description": "Require PR HEAD to match this SHA before merging.",
            },
        },
        "required": ["repo", "number"],
        "additionalProperties": False,
    },
    handler=merge_pr,
)

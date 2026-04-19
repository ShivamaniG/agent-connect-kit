from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def list_org_members(ctx: ActionContext, args: dict) -> list[dict]:
    org = args["org"]
    params: dict = {
        "per_page": min(int(args.get("per_page", 30)), 100),
        "page": max(int(args.get("page", 1)), 1),
    }
    if args.get("filter"):
        params["filter"] = args["filter"]
    if args.get("role"):
        params["role"] = args["role"]

    data = await request("GET", f"/orgs/{org}/members", ctx.access_token, params=params)
    return [
        {
            "id": u["id"],
            "login": u["login"],
            "html_url": u.get("html_url"),
            "avatar_url": u.get("avatar_url"),
            "site_admin": u.get("site_admin", False),
        }
        for u in data
    ]


list_org_members_action = Action(
    name="github.list_org_members",
    description=(
        "List members of a GitHub organization. Requires the 'read:org' OAuth scope."
    ),
    parameters={
        "type": "object",
        "properties": {
            "org": {"type": "string", "description": "Organization login (e.g. 'github')."},
            "filter": {
                "type": "string",
                "enum": ["all", "2fa_disabled"],
                "description": "Optional member filter.",
            },
            "role": {
                "type": "string",
                "enum": ["all", "admin", "member"],
                "description": "Optional role filter.",
            },
            "per_page": {"type": "integer", "default": 30, "minimum": 1, "maximum": 100},
            "page": {"type": "integer", "default": 1, "minimum": 1},
        },
        "required": ["org"],
        "additionalProperties": False,
    },
    handler=list_org_members,
)

from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def get_user(ctx: ActionContext, args: dict) -> dict:
    username = args.get("username")
    path = f"/users/{username}" if username else "/user"
    data = await request("GET", path, ctx.access_token)
    return {
        "id": data["id"],
        "login": data["login"],
        "name": data.get("name"),
        "bio": data.get("bio"),
        "company": data.get("company"),
        "blog": data.get("blog"),
        "location": data.get("location"),
        "email": data.get("email"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following"),
        "html_url": data.get("html_url"),
        "avatar_url": data.get("avatar_url"),
        "created_at": data.get("created_at"),
    }


get_user_action = Action(
    name="github.get_user",
    description=(
        "Fetch a GitHub user profile. If 'username' is omitted, returns the authenticated user."
    ),
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "GitHub username (login). Omit to fetch the authenticated user.",
            },
        },
        "additionalProperties": False,
    },
    handler=get_user,
)

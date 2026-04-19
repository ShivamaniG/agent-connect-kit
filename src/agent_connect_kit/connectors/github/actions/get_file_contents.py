import base64

from agent_connect_kit.connectors.base import Action
from agent_connect_kit.connectors.github.client import request
from agent_connect_kit.runtime.context import ActionContext


async def get_file_contents(ctx: ActionContext, args: dict) -> dict:
    repo = args["repo"]
    path = args["path"].lstrip("/")
    params = {}
    if args.get("ref"):
        params["ref"] = args["ref"]

    data = await request(
        "GET",
        f"/repos/{repo}/contents/{path}",
        ctx.access_token,
        params=params or None,
    )

    if isinstance(data, list):
        return {
            "type": "directory",
            "path": path,
            "entries": [
                {
                    "name": entry["name"],
                    "path": entry["path"],
                    "type": entry["type"],
                    "size": entry.get("size"),
                    "sha": entry.get("sha"),
                }
                for entry in data
            ],
        }

    result: dict = {
        "type": data.get("type", "file"),
        "name": data.get("name"),
        "path": data.get("path"),
        "size": data.get("size"),
        "sha": data.get("sha"),
        "html_url": data.get("html_url"),
        "encoding": data.get("encoding"),
    }

    if data.get("encoding") == "base64" and data.get("content"):
        try:
            decoded = base64.b64decode(data["content"]).decode("utf-8")
            result["content"] = decoded
            result["encoding"] = "utf-8"
        except UnicodeDecodeError:
            result["content"] = data["content"]
            result["encoding"] = "base64"
            result["note"] = "binary file; content is base64-encoded"
    else:
        result["content"] = data.get("content")

    return result


get_file_contents_action = Action(
    name="github.get_file_contents",
    description="Read the contents of a file or list a directory in a GitHub repository.",
    parameters={
        "type": "object",
        "properties": {
            "repo": {"type": "string", "pattern": "^[^/]+/[^/]+$"},
            "path": {
                "type": "string",
                "description": "File or directory path inside the repo (e.g. 'src/main.py').",
            },
            "ref": {
                "type": "string",
                "description": "Branch, tag, or commit SHA (default: repo's default branch).",
            },
        },
        "required": ["repo", "path"],
        "additionalProperties": False,
    },
    handler=get_file_contents,
)

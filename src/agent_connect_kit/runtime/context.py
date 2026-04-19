from dataclasses import dataclass


@dataclass(frozen=True)
class ActionContext:
    provider: str
    access_token: str
    user_id: int
    user_external_id: str
    connection_id: int

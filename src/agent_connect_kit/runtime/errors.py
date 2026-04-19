class ActionError(Exception):
    """Base class for action runtime errors."""


class ActionNotFound(ActionError):
    def __init__(self, name: str) -> None:
        super().__init__(f"action not registered: {name}")
        self.name = name


class UserNotConnected(ActionError):
    def __init__(self, user_external_id: str, provider: str) -> None:
        super().__init__(f"user {user_external_id!r} has no {provider} connection")
        self.user_external_id = user_external_id
        self.provider = provider

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


class ProviderNotConfigured(ActionError):
    def __init__(self, provider: str, detail: str = "") -> None:
        message = f"provider {provider!r} is not configured"
        if detail:
            message += f": {detail}"
        super().__init__(message)
        self.provider = provider

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

ActionHandler = Callable[..., Awaitable[Any]]


@dataclass(frozen=True)
class Action:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ActionHandler


class Connector(ABC):
    name: str
    # True  -> per-user OAuth; executor looks up Connection row and decrypts stored token
    # False -> service-credential model; executor calls get_service_credentials()
    requires_user_connection: bool = True

    @abstractmethod
    def actions(self) -> list[Action]:
        """Return the list of actions exposed by this connector."""

    def get_service_credentials(self) -> str | None:
        """Service-credential providers override this to supply a bot/service token.

        Raise RuntimeError if the provider is not configured (e.g. env var missing).
        """
        return None


_registry: dict[str, Connector] = {}


def register(connector: Connector) -> None:
    _registry[connector.name] = connector


def get_connectors() -> dict[str, Connector]:
    return dict(_registry)


def get_connector(name: str) -> Connector | None:
    return _registry.get(name)


def get_actions() -> dict[str, Action]:
    result: dict[str, Action] = {}
    for connector in _registry.values():
        for action in connector.actions():
            result[action.name] = action
    return result


def get_action(name: str) -> Action | None:
    return get_actions().get(name)

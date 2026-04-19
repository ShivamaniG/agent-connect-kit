from agent_connect_kit.connectors.base import Action, Connector
from agent_connect_kit.connectors.github.actions import ALL_ACTIONS


class GitHubConnector(Connector):
    name = "github"

    def actions(self) -> list[Action]:
        return list(ALL_ACTIONS)

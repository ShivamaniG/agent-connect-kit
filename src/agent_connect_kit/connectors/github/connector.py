from agent_connect_kit.connectors.base import Action, Connector


class GitHubConnector(Connector):
    name = "github"

    def actions(self) -> list[Action]:
        # M5 adds github.list_repos, M6 adds github.create_issue.
        return []

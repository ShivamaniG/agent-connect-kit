from agent_connect_kit.config import get_settings
from agent_connect_kit.connectors.base import Action, Connector
from agent_connect_kit.connectors.discord.actions import ALL_ACTIONS


class DiscordConnector(Connector):
    name = "discord"
    requires_user_connection = False

    def get_service_credentials(self) -> str:
        token = get_settings().discord_bot_token
        if not token:
            raise RuntimeError(
                "DISCORD_BOT_TOKEN is not set. "
                "Register a bot at https://discord.com/developers/applications "
                "and add the token to your .env."
            )
        return token

    def actions(self) -> list[Action]:
        return list(ALL_ACTIONS)

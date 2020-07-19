# Just make sure hooks are imported
from rcon.discord_chat import DiscordWebhookHandler
from rcon.player_history import handle_on_connect

DiscordWebhookHandler.init_env_vars()

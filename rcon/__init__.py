# Just make sure hooks are imported
from rcon import hooks
from rcon.auto_kick import auto_kick
from rcon.discord_chat import handle_on_chat, handle_on_kill, handle_on_tk
from rcon.recent_actions import update_kills, update_tks
from rcon.watchlist import watchdog

import os

import rcon.settings

# Allows importing the models in the maintenance container to run database migrations
if not os.getenv("HLL_MAINTENANCE_CONTAINER") and not os.getenv(
    "HLL_WH_SERVICE_CONTAINER"
):
    # Just make sure hooks are imported so the code registering the hooks will run
    from rcon import hooks
    from rcon.auto_kick import auto_kick
    from rcon.automods.tk_autoban import auto_ban_if_tks_right_after_connection
    from rcon.discord_chat import handle_on_chat, handle_on_kill, handle_on_tk
    from rcon.recent_actions import update_kills, update_tks
    from rcon.watchlist import watchdog

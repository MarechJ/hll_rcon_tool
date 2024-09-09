import os

# Allows importing the models in the maintenance container to run database migrations
if not os.getenv("HLL_MAINTENANCE_CONTAINER"):

    # Import all the sub modules that represent a user setting
    # so that .utils.all_subclasses() can properly report subclasses
    # for exporting settings through the CLI
    from . import (
        auto_broadcast,
        auto_kick,
        auto_mod_level,
        auto_mod_no_leader,
        auto_mod_seeding,
        auto_mod_solo_tank,
        ban_tk_on_connect,
        camera_notification,
        chat_commands,
        expired_vips,
        gtx_server_name,
        log_line_webhooks,
        log_stream,
        message_on_connect,
        name_kicks,
        rcon_connection_settings,
        rcon_server_settings,
        real_vip,
        scorebot,
        standard_messages,
        steam,
        vac_game_bans,
        vote_map,
        webhooks,
    )

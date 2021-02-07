import logging
from functools import wraps

from rcon.player_history import save_player, save_start_player_session, ban_if_blacklisted, ban_if_has_vac_bans, save_end_player_session
from rcon.game_logs import on_connected, on_disconnected

logger = logging.getLogger(__name__)

def inject_steam_id_64(func):
    @wraps(func)
    def wrapper(rcon, struct_log):
        name = struct_log['player']
        info = rcon.get_player_info(name)
        steam_id_64 = info.get('steam_id_64')
        if not steam_id_64:
            logger.warning("Can't get player steam_id for %s", name)
            return

        return func(rcon, struct_log, steam_id_64)
    return wrapper


@on_connected
@inject_steam_id_64
def handle_on_connect(rcon, struct_log, steam_id_64):
    timestamp = int(struct_log['timestamp_ms']) / 1000
    save_player(struct_log['player'], steam_id_64, timestamp=int(struct_log['timestamp_ms']) / 1000)
    save_start_player_session(steam_id_64, timestamp=timestamp)
    ban_if_blacklisted(rcon, steam_id_64, struct_log['player'])
    ban_if_has_vac_bans(rcon, steam_id_64, struct_log['player'])


@on_disconnected
@inject_steam_id_64
def handle_on_disconnect(rcon, struct_log, steam_id_64):
    save_end_player_session(steam_id_64, struct_log['timestamp_ms'] / 1000)

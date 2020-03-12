import logging

from rcon.models import init_db, enter_session, PlayerName, PlayerSteamID
from rcon.game_logs import on_connected
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)

def _save_steam_id(sess, steam_id_64):
    steamid = sess.query(PlayerSteamID).filter(
        PlayerSteamID.steam_id_64 == steam_id_64
    ).one_or_none()

    if not steamid:
        steamid = PlayerSteamID(steam_id_64=steam_id_64)
        sess.add(steamid)
        logger.info("Adding first time seen steamid %s", steam_id_64)
        sess.commit()

    return steamid

def _save_player_alias(sess, steamid, player_name):
    name = sess.query(PlayerName).filter(
        PlayerName.name == player_name, 
        PlayerName.steamid == steamid
    ).one_or_none()


    if not name:
        name = PlayerName(name=player_name, steamid=steamid)
        sess.add(name)
        logger.info("Adding player %s with new name %s", steamid.steam_id_64, player_name)
        sess.commit()
        
    return name

def save_player(player_name, steam_id_64):
    with enter_session() as sess:
        steamid = _save_steam_id(sess, steam_id_64)
        _save_player_alias(sess, steamid, player_name)

@on_connected
def handle_on_connect(rcon: Rcon, struct_log):
    name = struct_log['player']
    if not name:
        logger.warning("Can't get player name from logs %s", struct_log)
        return

    info = rcon.get_player_info(name)
    steam_id_64 = info.get('steam_id_64')
    if not steam_id_64:
        logger.warning("Can't get player steam_id for %s", name)
        return

    save_player(name, steam_id_64)

if __name__ == '__main__':
    save_player('Achile5115', '76561198172574911')
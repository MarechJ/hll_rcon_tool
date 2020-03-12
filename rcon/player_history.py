import logging

from rcon.models import init_db, session, PlayerName, PlayerSteamID
from rcon.game_logs import on_connected

logger = logging.getLogger(__name__)

def save_player(player_name, steam_id_64):
    with session() as sess:
        steamid = sess.query(PlayerSteamID).fitler(PlayerSteamID.steam_id_64 == steam_id_64).one_or_none()
        if not steamid:
            steamid = PlayerSteamID(steam_id_64=steam_id_64)
            session.add(steamid)
            logger.info("Adding first time seen steamid %s", steam_id_64)
            session.commit()

        name = sess.query(PlayerName).filter(
            PlayerName == player_name, 
            PlayerName.steamid == steamid
        ).one_or_none()

        if not name:
            name = PlayerSteamID(name=player_name, steamid=steamid)
            sess.add(name)
            logger.info("Adding player %s with new name %s", steam_id_64, player_name)
            session.commit()

@on_connected
def handle_on_connect(rcon, struct_log):
    print(struct_log)
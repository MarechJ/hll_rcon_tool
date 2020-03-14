import logging
import datetime
from functools import wraps
from sqlalchemy import func

from rcon.models import init_db, enter_session, PlayerName, PlayerSteamID, PlayerSession
from rcon.game_logs import on_connected, on_disconnected
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)


def get_player(sess, steam_id_64):
  return sess.query(PlayerSteamID).filter(
       PlayerSteamID.steam_id_64 == steam_id_64
       ).one_or_none()

def get_players_by_appearance(sess, page=1, page_size=1000):
    if page <= 0:
        raise ValueError('page needs to be >= 1')
    if page_size <= 0:
        raise ValueError('page_size needs to be >= 1')

    query = sess.query(
        PlayerSession, 
        func.min(func.coalesce(PlayerSession.start, PlayerSession.created)), 
        func.max(func.coalesce(PlayerSession.end, PlayerSession.created))
    ).group_by(PlayerSession.playersteamid_id)
    players = query.order_by(func.max(PlayerSession.end)).limit(page_size).offset((page - 1) * page_size).all()
    total = query.count()
    
    return {
        'total': total,
        'players': [
            {
                'steam_id_64': p[0].steamid.steam_id_64,
                'names': [n.name for n in p[0].steamid.names],
                'first_seen_timestamp_ms': int(p[1].timestamp() * 1000),
                'last_seen_timestamp_ms': int(p[2].timestamp() * 1000),
                'blacklisted': p[0].steamid.blacklisted
            }
            for p in players
        ],
        'page': page,
        'page_size': page_size
    }

def _save_steam_id(sess, steam_id_64):
    steamid = get_player(sess, steam_id_64)

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
        logger.info("Adding player %s with new name %s",
                    steamid.steam_id_64, player_name)
        sess.commit()

    return name


def save_player(player_name, steam_id_64):
    with enter_session() as sess:
        steamid = _save_steam_id(sess, steam_id_64)
        _save_player_alias(sess, steamid, player_name)


def save_start_player_session(steam_id_64, timestamp_ms):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            logger.error(
                "Can't record player session for %s, player not found", steam_id_64)
            return

        sess.add(
            PlayerSession(
                steamid=player,
                start=datetime.datetime.fromtimestamp(timestamp_ms/1000)
            )
        )
        logger.info("Recorded player %s session start at %s", 
            steam_id_64, datetime.datetime.fromtimestamp(timestamp_ms/1000)
        )
        sess.commit()


def save_end_player_session(steam_id_64, timestamp_ms):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            logger.error(
                "Can't record player session for %s, player not found", steam_id_64)
            return

        last_session = sess.query(PlayerSession).filter(
            PlayerSession.steamid == player
        ).order_by(PlayerSession.created.desc()).first()

        if last_session.end:
            logger.warning("Last session was already ended for %s. Creating a new one instead", steam_id_64)
            last_session = PlayerSession(
                steamid=player,
            )
        last_session.end = datetime.datetime.fromtimestamp(
            timestamp_ms / 1000
        )
        logger.info("Recorded player %s session end at %s", steam_id_64, last_session.end)
        sess.commit()


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
def handle_on_connect(rcon: Rcon, struct_log, steam_id_64):
    save_player(struct_log['player'], steam_id_64)
    save_start_player_session(steam_id_64, struct_log['timestamp_ms'])


@on_disconnected
@inject_steam_id_64
def handle_on_disconnect(rcon: Rcon, struct_log, steam_id_64):
    save_end_player_session(steam_id_64, struct_log['timestamp_ms'])


if __name__ == '__main__':
    save_player('Achile5115', '76561198172574911')
    save_start_player_session(
        '76561198172574911', datetime.datetime.now().timestamp()
    )
    save_end_player_session(
        '76561198172574911', 
        int((datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp() * 1000)
    ) 
    save_end_player_session(
        '76561198172574911', 
        int((datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp() * 1000)
    ) 

    save_player('Dr.WeeD', '4242')
    save_start_player_session(
        '4242', datetime.datetime.now().timestamp()
    )
    save_end_player_session(
        '4242', 
        int((datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp() * 1000)
    ) 
    save_end_player_session(
        '4242', 
        int((datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp() * 1000)
    ) 

    import pprint
    with enter_session() as sess:
        pprint.pprint(get_players_by_appearance(sess))
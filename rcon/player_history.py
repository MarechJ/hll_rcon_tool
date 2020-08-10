import logging
import datetime
from functools import wraps
from sqlalchemy import func
from sqlalchemy.orm import contains_eager
import math

from rcon.models import (
    init_db, enter_session, PlayerName, 
    PlayerSteamID, PlayerSession, BlacklistedPlayer, PlayerBanLog,
    PlayersAction, PlayerFlag
)
from rcon.queries import get_player, save_player, get_set_player, add_player_action
from rcon.blacklist import ban_if_blacklisted
from rcon.game_logs import on_connected, on_disconnected
from rcon.commands import CommandFailedError
from rcon.cache_utils import ttl_cache, invalidates
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)


def get_player_profile(steam_id_64, nb_sessions):
    with enter_session() as sess:
        player = sess.query(PlayerSteamID).filter(
            PlayerSteamID.steam_id_64 == steam_id_64
        ).one_or_none()
        if player is None:
            return
        return player.to_dict(limit_sessions=nb_sessions)


def get_players_by_appearance(page=1, page_size=500, last_seen_from: datetime.datetime = None, last_seen_till: datetime.datetime = None, player_name = None, blacklisted = None, steam_id_64 = None):
    if page <= 0:
        raise ValueError('page needs to be >= 1')
    if page_size <= 0:
        raise ValueError('page_size needs to be >= 1')

    with enter_session() as sess:
        sub = sess.query(
            PlayerSession.playersteamid_id,
            func.min(func.coalesce(PlayerSession.start,
                                   PlayerSession.created)).label('first'),
            func.max(func.coalesce(PlayerSession.end,
                                   PlayerSession.created)).label('last')
        ).group_by(PlayerSession.playersteamid_id).subquery()
        query = sess.query(PlayerSteamID, sub.c.first, sub.c.last).outerjoin(
            sub, sub.c.playersteamid_id == PlayerSteamID.id)

        if steam_id_64:
            query = query.filter(PlayerSteamID.steam_id_64.ilike("%{}%".format(steam_id_64)))
        if player_name:
            query = query.join(PlayerSteamID.names).filter(PlayerName.name.ilike("%{}%".format(player_name))).options(contains_eager(PlayerSteamID.names))
        if blacklisted is True:
            query = query.join(PlayerSteamID.blacklist).filter(BlacklistedPlayer.is_blacklisted == True).options(contains_eager(PlayerSteamID.blacklist))
        if last_seen_from:
            query = query.filter(sub.c.last >= last_seen_from)
        if last_seen_till:
            query = query.filter(sub.c.last <= last_seen_till)

        total = query.count()
        page = min(max(math.ceil(total / page_size), 1), page) 
        players = query.order_by(func.coalesce(sub.c.last, PlayerSteamID.created).desc()).limit(
            page_size).offset((page - 1) * page_size).all()
       
        # TODO: Why not returning the whole player dict + the extra aggregated fields?
        # Perf maybe a bit crappier but that's not too much of a concern here
        return {
            'total': total,
            'players': [
                {
                    'steam_id_64': p[0].steam_id_64,
                    'names': [n.name for n in p[0].names],
                    'first_seen_timestamp_ms': int(p[1].timestamp() * 1000) if p[1] else None,
                    'last_seen_timestamp_ms': int(p[2].timestamp() * 1000) if p[2] else None,
                    'penalty_count': p[0].get_penalty_count(),
                    'blacklisted': p[0].blacklist.is_blacklisted if p[0].blacklist else False,
                    'flags': [f.to_dict() for f in p[0].flags],
                    'ban_logs': [b.to_dict() for b in p[0].ban_logs]
                }
                for p in players
            ],
            'page': page,
            'page_size': page_size
        }

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
                    steam_id_64, datetime.datetime.fromtimestamp(
                        timestamp_ms/1000)
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
            logger.warning(
                "Last session was already ended for %s. Creating a new one instead", steam_id_64)
            last_session = PlayerSession(
                steamid=player,
            )
        last_session.end = datetime.datetime.fromtimestamp(
            timestamp_ms / 1000
        )
        logger.info("Recorded player %s session end at %s",
                    steam_id_64, last_session.end)
        sess.commit()


def add_flag_to_player(steam_id_64, flag, comment=None, player_name=None):
    with enter_session() as sess:
        player = get_set_player(sess, player_name=player_name, steam_id_64=steam_id_64)
        exits = sess.query(PlayerFlag).filter(PlayerFlag.playersteamid_id == player.id, PlayerFlag.flag == flag).all()
        if exits:
            logger.warning("Flag already exists")
            raise CommandFailedError("Flag already exists")
        new = PlayerFlag(flag=flag, comment=comment, steamid=player)
        sess.add(new)
        sess.commit()
        res = player.to_dict()
        return res, new.to_dict()
    

def remove_flag(flag_id):
    with enter_session() as sess:
        exits = sess.query(PlayerFlag).filter(PlayerFlag.id == int(flag_id)).one_or_none()
        if not exits:
            logger.warning("Flag does not exists")
            raise CommandFailedError("Flag does not exists")
        player = exits.steamid.to_dict()
        flag = exits.to_dict()
        sess.delete(exits)
        sess.commit()

    return player, flag


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
    save_player(struct_log['player'], steam_id_64)
    save_start_player_session(steam_id_64, struct_log['timestamp_ms'])
    ban_if_blacklisted(rcon, steam_id_64, struct_log['player'])


@on_disconnected
@inject_steam_id_64
def handle_on_disconnect(rcon, struct_log, steam_id_64):
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
    save_player('Second Achile5115', '76561198172574911')
    save_player('Dr.WeeD', '4242')
    save_player('Dr.WeeD2', '4242')
    save_player('Dr.WeeD3', '4242')
    save_player('Dr.WeeD4', '4242')
    save_player('Dr.WeeD5', '4242')
    save_player('Dr.WeeD6', '4242')
    save_player("test", '76561197984877751')
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
    add_player_to_blacklist("4242", "test")
    remove_player_from_blacklist("4242")

    import pprint
    pprint.pprint(get_players_by_appearance())

    add_flag_to_player("76561198156263725", "🐷")


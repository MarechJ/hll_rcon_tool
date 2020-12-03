from rcon.cache_utils import ttl_cache, invalidates
import os
import logging
import datetime
from functools import wraps
from sqlalchemy import func
from sqlalchemy.orm import contains_eager
import math

from rcon.extended_commands import Rcon
from rcon.models import (
    init_db, enter_session, PlayerName,
    PlayerSteamID, PlayerSession, BlacklistedPlayer,
    PlayersAction, PlayerFlag
)
from rcon.discord import send_to_discord_audit, dict_to_discord
from rcon.game_logs import on_connected, on_disconnected
from rcon.commands import CommandFailedError

from rcon.steam_utils import get_player_bans, STEAM_KEY


MAX_DAYS_SINCE_BAN = os.getenv('BAN_ON_VAC_HISTORY_DAYS', 0)
AUTO_BAN_REASON = os.getenv(
    'BAN_ON_VAC_HISTORY_REASON', 'VAC ban history ({DAYS_SINCE_LAST_BAN} days ago)')
MAX_GAME_BAN_THRESHOLD = os.getenv('MAX_GAME_BAN_THRESHOLD', 0)


logger = logging.getLogger(__name__)


def get_player(sess, steam_id_64):
    return sess.query(PlayerSteamID).filter(
        PlayerSteamID.steam_id_64 == steam_id_64
    ).one_or_none()


def get_player_profile(steam_id_64, nb_sessions):
    with enter_session() as sess:
        player = sess.query(PlayerSteamID).filter(
            PlayerSteamID.steam_id_64 == steam_id_64
        ).one_or_none()
        if player is None:
            return
        return player.to_dict(limit_sessions=nb_sessions)


def get_profiles(steam_ids, nb_sessions=0):
    with enter_session() as sess:
        players = sess.query(PlayerSteamID).filter(
            PlayerSteamID.steam_id_64.in_(steam_ids)
        ).all()

        return [p.to_dict(limit_sessions=nb_sessions) for p in players]


def _get_set_player(sess, player_name, steam_id_64):
    player = get_player(sess, steam_id_64)
    if player is None:
        player = _save_steam_id(sess, steam_id_64)
    if player_name:
        _save_player_alias(sess, player, player_name)

    return player


def get_players_by_appearance(page=1, page_size=500, last_seen_from: datetime.datetime = None, last_seen_till: datetime.datetime = None, player_name=None, blacklisted=None, steam_id_64=None):
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
            query = query.filter(PlayerSteamID.steam_id_64.ilike(
                "%{}%".format(steam_id_64)))
        if player_name:
            query = query.join(PlayerSteamID.names).filter(PlayerName.name.ilike(
                "%{}%".format(player_name))).options(contains_eager(PlayerSteamID.names))
        if blacklisted is True:
            query = query.join(PlayerSteamID.blacklist).filter(
                BlacklistedPlayer.is_blacklisted == True).options(contains_eager(PlayerSteamID.blacklist))
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
                    'flags': [f.to_dict() for f in p[0].flags]
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


def save_player_action(rcon, action_type, player_name, by, reason='', steam_id_64=None):
    with enter_session() as sess:
        _steam_id_64 = steam_id_64 or rcon.get_player_info(player_name)['steam_id_64']
        player = _get_set_player(sess, player_name, _steam_id_64)
        sess.add(
            PlayersAction(
                action_type=action_type.upper(),
                steamid=player,
                reason=reason,
                by=by
            )
        )

def safe_save_player_action(rcon, action_type, player_name, by, reason='', steam_id_64=None):
    try:
        return save_player_action(rcon, action_type, player_name, by, reason, steam_id_64)
    except Exception as e:
        logger.exception("Failed to record player action: %s %s",
                         action_type, player_name)
        return False


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


def ban_if_blacklisted(rcon:Rcon, steam_id_64, name):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)

        if not player:
            logger.error(
                "Can't check blacklist, player not found %s", steam_id_64)
            return

        if player.blacklist and player.blacklist.is_blacklisted:
            logger.info("Player %s was banned due blacklist, reason: %s", str(
                player), player.blacklist.reason)
            rcon.do_perma_ban(steam_id_64=steam_id_64, reason=player.blacklist.reason, by="BLACKLIST")
            # TODO save author of blacklist
            safe_save_player_action(
                rcon=rcon, player_name=name, action_type="PERMABAN", reason=player.blacklist.reason, by='BLACKLIST', steam_id_64=steam_id_64
            )
            try:
                send_to_discord_audit(
                    f"`BLACKLIST` -> {dict_to_discord(dict(player=name, reason=player.blacklist.reason))}", "BLACKLIST")
            except:
                logger.error("Unable to send blacklist to audit log")


def should_ban(bans, max_game_bans, max_days_since_ban):
    try:
        days_since_last_ban = int(bans['DaysSinceLastBan'])
        number_of_game_bans = int(bans.get('NumberOfGameBans', 0))
    except ValueError:  # In case DaysSinceLastBan can be null
        return

    has_a_ban = bans.get(
        'VACBanned') == True or number_of_game_bans >= max_game_bans

    if days_since_last_ban <= 0:
        return False

    if days_since_last_ban <= max_days_since_ban and has_a_ban:
        return True

    return False


def ban_if_has_vac_bans(rcon: Rcon, steam_id_64, name):
    try:
        max_days_since_ban = int(MAX_DAYS_SINCE_BAN)
        max_game_bans = float(
            'inf') if int(MAX_GAME_BAN_THRESHOLD) <= 0 else int(MAX_GAME_BAN_THRESHOLD)
    except ValueError:  # No proper value is given
        logger.error(
            "Invalid value given for environment variable BAN_ON_VAC_HISTORY_DAYS or MAX_GAME_BAN_THRESHOLD")
        return

    if max_days_since_ban <= 0:
        return  # Feature is disabled

    with enter_session() as sess:
        player = get_player(sess, steam_id_64)

        if not player:
            logger.error(
                "Can't check VAC history, player not found %s", steam_id_64)
            return

        bans = get_player_bans(steam_id_64)
        if not bans or not isinstance(bans, dict):
            logger.warning(
                "Can't fetch Bans for player %s, received %s", steam_id_64, bans)
            # Player couldn't be fetched properly (logged by get_player_bans)
            return

        if should_ban(bans, max_game_bans, max_days_since_ban):
            reason = AUTO_BAN_REASON.format(DAYS_SINCE_LAST_BAN=bans.get(
                'DaysSinceLastBan'), MAX_DAYS_SINCE_BAN=str(max_days_since_ban))
            logger.info("Player %s was banned due VAC history, last ban: %s days ago", str(
                player), bans.get('DaysSinceLastBan'))
            rcon.do_perma_ban(steam_id_64=steam_id_64, reason=reason, admin_name="A BOT")
            safe_save_player_action(
                rcon=rcon, player_name=name, action_type="PERMABAN", reason=reason, by='AUTOBAN', steam_id_64=player.steam_id_64
            )

            try:
                audit_params = dict(
                    player=name,
                    steam_id_64=player.steam_id_64,
                    reason=reason,
                    days_since_last_ban=bans.get('DaysSinceLastBan'),
                    vac_banned=bans.get('VACBanned'),
                    number_of_game_bans=bans.get('NumberOfGameBans')
                )
                send_to_discord_audit(
                    f"`VAC/GAME BAN` -> {dict_to_discord(audit_params)}", "AUTOBAN")
            except:
                logger.exception("Unable to send vac ban to audit log")


def add_flag_to_player(steam_id_64, flag, comment=None, player_name=None):
    with enter_session() as sess:
        player = _get_set_player(
            sess, player_name=player_name, steam_id_64=steam_id_64)
        exits = sess.query(PlayerFlag).filter(
            PlayerFlag.playersteamid_id == player.id, PlayerFlag.flag == flag).all()
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
        exits = sess.query(PlayerFlag).filter(
            PlayerFlag.id == int(flag_id)).one_or_none()
        if not exits:
            logger.warning("Flag does not exists")
            raise CommandFailedError("Flag does not exists")
        player = exits.steamid.to_dict()
        flag = exits.to_dict()
        sess.delete(exits)
        sess.commit()

    return player, flag


def add_player_to_blacklist(steam_id_64, reason, name=None):
    # TODO save author of blacklist
    with enter_session() as sess:
        player = _get_set_player(
            sess, steam_id_64=steam_id_64, player_name=name)
        if not player:
            raise CommandFailedError(
                f"Player with steam id {steam_id_64} not found")

        if player.blacklist:
            if player.blacklist.is_blacklisted:
                logger.warning("Player %s was already blacklisted with %s, updating reason to %s", str(
                    player), player.blacklist.reason, reason)
            player.blacklist.is_blacklisted = True
            player.blacklist.reason = reason
        else:
            logger.info("Player %s blacklisted for %s", str(player), reason)
            sess.add(
                BlacklistedPlayer(
                    steamid=player, is_blacklisted=True, reason=reason)
            )

        sess.commit()


def remove_player_from_blacklist(steam_id_64):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            raise CommandFailedError(
                f"Player with steam id {steam_id_64} not found")

        if not player.blacklist:
            raise CommandFailedError(f"Player {player} was not blacklisted")

        player.blacklist.is_blacklisted = False
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
def handle_on_connect(rcon, struct_log, steam_id_64):
    save_player(struct_log['player'], steam_id_64)
    save_start_player_session(steam_id_64, struct_log['timestamp_ms'])
    ban_if_blacklisted(rcon, steam_id_64, struct_log['player'])
    ban_if_has_vac_bans(rcon, steam_id_64, struct_log['player'])


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

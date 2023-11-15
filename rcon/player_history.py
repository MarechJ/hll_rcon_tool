import datetime
import logging
import math
import os
import unicodedata
from functools import cmp_to_key

from sqlalchemy import func
from sqlalchemy.orm import contains_eager, selectinload
from sqlalchemy.sql.functions import ReturnTypeFromArgs

from rcon.commands import CommandFailedError
from rcon.models import (
    BlacklistedPlayer,
    PlayerComment,
    PlayerFlag,
    PlayerName,
    PlayersAction,
    PlayerSession,
    PlayerSteamID,
    SteamInfo,
    WatchList,
    enter_session,
)


class unaccent(ReturnTypeFromArgs):
    pass


logger = logging.getLogger(__name__)


def player_has_flag(player_dict, flag):
    flags = player_dict.get("flags") or []

    return flag in {flag["flag"] for flag in flags}


def get_player(sess, steam_id_64) -> PlayerSteamID | None:
    return (
        sess.query(PlayerSteamID)
        .filter(PlayerSteamID.steam_id_64 == steam_id_64)
        .one_or_none()
    )


def get_player_profile(steam_id_64, nb_sessions):
    with enter_session() as sess:
        player = (
            sess.query(PlayerSteamID)
            .filter(PlayerSteamID.steam_id_64 == steam_id_64)
            .one_or_none()
        )
        if player is None:
            return
        return player.to_dict(limit_sessions=nb_sessions)


def get_player_profile_by_ids(sess, ids):
    return (
        sess.query(PlayerSteamID)
        .filter(PlayerSteamID.id.in_(ids))
        .options(
            selectinload(PlayerSteamID.names),
            selectinload(PlayerSteamID.received_actions),
            selectinload(PlayerSteamID.blacklist),
            selectinload(PlayerSteamID.flags),
            selectinload(PlayerSteamID.watchlist),
            selectinload(PlayerSteamID.steaminfo),
        )
        .all()
    )


def get_player_profile_by_steam_ids(sess, steam_ids):
    return (
        sess.query(PlayerSteamID)
        .filter(PlayerSteamID.steam_id_64.in_(steam_ids))
        .options(
            selectinload(PlayerSteamID.names),
            selectinload(PlayerSteamID.received_actions),
            selectinload(PlayerSteamID.blacklist),
            selectinload(PlayerSteamID.flags),
            selectinload(PlayerSteamID.watchlist),
            selectinload(PlayerSteamID.steaminfo),
        )
        .all()
    )


def get_player_profile_by_id(id, nb_sessions):
    with enter_session() as sess:
        player = sess.query(PlayerSteamID).filter(PlayerSteamID.id == id).one_or_none()
        if player is None:
            return
        return player.to_dict(limit_sessions=nb_sessions)


def _get_profiles(sess, steam_ids, nb_sessions=0):
    return (
        sess.query(PlayerSteamID).filter(PlayerSteamID.steam_id_64.in_(steam_ids)).all()
    )


def get_profiles(steam_ids, nb_sessions=1):
    with enter_session() as sess:
        players = _get_profiles(sess, steam_ids, nb_sessions)

        return [p.to_dict(limit_sessions=nb_sessions) for p in players]


def _get_set_player(sess, player_name, steam_id_64, timestamp=None):
    player = get_player(sess, steam_id_64)
    if player is None:
        player = _save_steam_id(sess, steam_id_64)
    if player_name:
        _save_player_alias(
            sess, player, player_name, timestamp or datetime.datetime.now().timestamp()
        )

    return player


def remove_accent(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("utf-8")


def get_players_by_appearance(
    page=1,
    page_size=500,
    last_seen_from: datetime.datetime = None,
    last_seen_till: datetime.datetime = None,
    player_name=None,
    blacklisted=None,
    steam_id_64=None,
    is_watched=None,
    exact_name_match=False,
    ignore_accent=True,
    flags=None,
    country=None,
):
    if page <= 0:
        raise ValueError("page needs to be >= 1")
    if page_size <= 0:
        raise ValueError("page_size needs to be >= 1")

    with enter_session() as sess:
        sub = (
            sess.query(
                PlayerSession.playersteamid_id,
                func.min(
                    func.coalesce(PlayerSession.start, PlayerSession.created)
                ).label("first"),
                func.max(func.coalesce(PlayerSession.end, PlayerSession.created)).label(
                    "last"
                ),
            )
            .group_by(PlayerSession.playersteamid_id)
            .subquery()
        )
        query = sess.query(PlayerSteamID, sub.c.first, sub.c.last).outerjoin(
            sub, sub.c.playersteamid_id == PlayerSteamID.id
        )

        if steam_id_64:
            query = query.filter(
                PlayerSteamID.steam_id_64.ilike("%{}%".format(steam_id_64))
            )

        if player_name:
            search = PlayerName.name
            if ignore_accent:
                search = unaccent(PlayerName.name)
                player_name = remove_accent(player_name)
            if not exact_name_match:
                query = query.join(PlayerSteamID.names).filter(
                    search.ilike("%{}%".format(player_name))
                )
            else:
                query = query.join(PlayerSteamID.names).filter(search == player_name)

        if blacklisted is True:
            query = (
                query.join(PlayerSteamID.blacklist)
                .filter(BlacklistedPlayer.is_blacklisted == True)
                .options(contains_eager(PlayerSteamID.blacklist))
            )
        if is_watched is True:
            query = (
                query.join(PlayerSteamID.watchlist)
                .filter(WatchList.is_watched == True)
                .options(contains_eager(PlayerSteamID.watchlist))
            )

        if flags:
            if not isinstance(flags, list):
                flags = [flags]
            query = query.join(PlayerSteamID.flags).filter(PlayerFlag.flag.in_(flags))

        if country:
            query = query.join(PlayerSteamID.steaminfo).filter(
                SteamInfo.country == country.upper()
            )

        if last_seen_from:
            query = query.filter(sub.c.last >= last_seen_from)
        if last_seen_till:
            query = query.filter(sub.c.last <= last_seen_till)

        total = query.count()
        page = min(max(math.ceil(total / page_size), 1), page)
        players = (
            query.order_by(func.coalesce(sub.c.last, PlayerSteamID.created).desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
            .all()
        )

        def sort_name_match(v, v2):
            if not player_name:
                return 0
            search = player_name.lower()
            v = v.lower()
            v2 = v2.lower()
            if ignore_accent:
                v = remove_accent(v)
                v2 = remove_accent(v2)

            if search in v and search in v2:
                return 0
            if search in v:
                return -1
            return 1

        return {
            "total": total,
            "players": [
                {
                    # TODO the lazyloading here makes it super slow on large limit
                    **p[0].to_dict(limit_sessions=0),
                    "names_by_match": sorted(
                        (n.name for n in p[0].names), key=cmp_to_key(sort_name_match)
                    ),
                    "first_seen_timestamp_ms": int(p[1].timestamp() * 1000)
                    if p[1]
                    else None,
                    "last_seen_timestamp_ms": int(p[2].timestamp() * 1000)
                    if p[2]
                    else None,
                    "vip_expiration": p[0].vip.expiration if p[0].vip else None,
                }
                for p in players
            ],
            "page": page,
            "page_size": page_size,
        }


def _save_steam_id(sess, steam_id_64):
    steamid = get_player(sess, steam_id_64)

    if not steamid:
        steamid = PlayerSteamID(steam_id_64=steam_id_64)
        sess.add(steamid)
        logger.info("Adding first time seen steamid %s", steam_id_64)
        sess.commit()

    return steamid


def _save_player_alias(sess, steamid, player_name, timestamp=None):
    name = (
        sess.query(PlayerName)
        .filter(PlayerName.name == player_name, PlayerName.steamid == steamid)
        .one_or_none()
    )

    if timestamp:
        dt = datetime.datetime.fromtimestamp(timestamp)
    else:
        dt = datetime.datetime.now()
    if not name:
        name = PlayerName(name=player_name, steamid=steamid, last_seen=dt)
        sess.add(name)
        logger.info(
            "Adding player %s with new name %s", steamid.steam_id_64, player_name
        )
        sess.commit()
    else:
        name.last_seen = dt
        sess.commit()

    return name


def save_player(player_name, steam_id_64, timestamp=None):
    with enter_session() as sess:
        steamid = _save_steam_id(sess, steam_id_64)
        _save_player_alias(
            sess, steamid, player_name, timestamp or datetime.datetime.now()
        )


def save_player_action(
    rcon, action_type, player_name, by, reason="", steam_id_64=None, timestamp=None
):
    with enter_session() as sess:
        _steam_id_64 = (
            steam_id_64
            or rcon.get_player_info(player_name, can_fail=True)["steam_id_64"]
        )
        player = _get_set_player(sess, player_name, _steam_id_64, timestamp=timestamp)
        sess.add(
            PlayersAction(
                action_type=action_type.upper(), steamid=player, reason=reason, by=by
            )
        )


def safe_save_player_action(
    rcon, action_type, player_name, by, reason="", steam_id_64=None
):
    try:
        return save_player_action(
            rcon, action_type, player_name, by, reason, steam_id_64
        )
    except Exception as e:
        logger.exception(
            "Failed to record player action: %s %s", action_type, player_name
        )
        return False


def save_start_player_session(
    steam_id_64, timestamp, server_name=None, server_number=None
):
    server_name = server_name or os.getenv("SERVER_SHORT_NAME")
    server_number = server_number or os.getenv("SERVER_NUMBER")

    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            logger.error(
                "Can't record player session for %s, player not found", steam_id_64
            )
            return

        start_time = datetime.datetime.fromtimestamp(timestamp)
        already_saved = (
            sess.query(PlayerSession)
            .filter(PlayerSession.steamid == player)
            .filter(PlayerSession.start == start_time)
            .first()
        )

        if already_saved is not None:
            logger.info(
                f"Player session starting at {start_time} for player {steam_id_64} already recorded, skipping..."
            )
            return

        sess.add(
            PlayerSession(
                steamid=player,
                start=start_time,
                server_name=server_name,
                server_number=server_number,
            )
        )
        logger.info(
            "Recorded player %s session start at %s",
            steam_id_64,
            datetime.datetime.fromtimestamp(timestamp),
        )
        sess.commit()


def save_end_player_session(steam_id_64, timestamp):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            logger.error(
                "Can't record player session for %s, player not found", steam_id_64
            )
            return

        last_session = (
            sess.query(PlayerSession)
            .filter(PlayerSession.steamid == player)
            .order_by(PlayerSession.created.desc())
            .first()
        )

        if last_session.end:
            logger.warning(
                "Last session was already ended for %s. Creating a new one instead",
                steam_id_64,
            )
            last_session = PlayerSession(
                steamid=player,
            )
        last_session.end = datetime.datetime.fromtimestamp(timestamp)
        logger.info(
            "Recorded player %s session end at %s", steam_id_64, last_session.end
        )
        sess.commit()


def add_flag_to_player(steam_id_64, flag, comment=None, player_name=None):
    with enter_session() as sess:
        player = _get_set_player(sess, player_name=player_name, steam_id_64=steam_id_64)
        exits = (
            sess.query(PlayerFlag)
            .filter(PlayerFlag.playersteamid_id == player.id, PlayerFlag.flag == flag)
            .all()
        )
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
        exits = (
            sess.query(PlayerFlag).filter(PlayerFlag.id == int(flag_id)).one_or_none()
        )
        if not exits:
            logger.warning("Flag does not exists")
            raise CommandFailedError("Flag does not exists")
        player = exits.steamid.to_dict()
        flag = exits.to_dict()
        sess.delete(exits)
        sess.commit()

    return player, flag


def add_player_to_blacklist(steam_id_64, reason, name=None, by=None):
    # TODO save author of blacklist
    with enter_session() as sess:
        player = _get_set_player(sess, steam_id_64=steam_id_64, player_name=name)
        if not player:
            raise CommandFailedError(f"Player with steam id {steam_id_64} not found")

        if player.blacklist:
            if player.blacklist.is_blacklisted:
                logger.warning(
                    "Player %s was already blacklisted with %s, updating reason to %s",
                    str(player),
                    player.blacklist.reason,
                    reason,
                )
            player.blacklist.is_blacklisted = True
            player.blacklist.reason = reason
            player.blacklist.by = by
        else:
            logger.info("Player %s blacklisted for %s", str(player), reason)
            sess.add(
                BlacklistedPlayer(
                    steamid=player, is_blacklisted=True, reason=reason, by=by
                )
            )

        sess.commit()


def remove_player_from_blacklist(steam_id_64):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            raise CommandFailedError(f"Player with steam id {steam_id_64} not found")

        if not player.blacklist:
            raise CommandFailedError(f"Player {player} was not blacklisted")

        player.blacklist.is_blacklisted = False
        sess.commit()


def get_player_messages(steam_id_64):
    with enter_session() as sess:
        player = (
            sess.query(PlayerSteamID).filter_by(steam_id_64=steam_id_64).one_or_none()
        )
        if player:
            return [
                action.to_dict()
                for action in player.received_actions
                if action.action_type == "MESSAGE"
            ]
        else:
            raise Exception


def get_player_comments(steam_id_64):
    with enter_session() as sess:
        player = sess.query(PlayerSteamID).filter_by(steam_id_64=steam_id_64).one()
        return [c.to_dict() for c in player.comments]


def post_player_comments(steam_id_64, comment, user="Bot"):
    with enter_session() as sess:
        player = sess.query(PlayerSteamID).filter_by(steam_id_64=steam_id_64).one()
        player.comments.append(PlayerComment(content=comment, by=user))
        sess.commit()


if __name__ == "__main__":
    save_player("Achile5115", "76561198172574911")
    save_start_player_session("76561198172574911", datetime.datetime.now().timestamp())
    save_end_player_session(
        "76561198172574911",
        int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
            * 1000
        ),
    )
    save_end_player_session(
        "76561198172574911",
        int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
            * 1000
        ),
    )
    save_player("Second Achile5115", "76561198172574911")
    save_player("Dr.WeeD", "4242")
    save_player("Dr.WeeD2", "4242")
    save_player("Dr.WeeD3", "4242")
    save_player("Dr.WeeD4", "4242")
    save_player("Dr.WeeD5", "4242")
    save_player("Dr.WeeD6", "4242")
    save_player("test", "76561197984877751")
    save_start_player_session("4242", datetime.datetime.now().timestamp())
    save_end_player_session(
        "4242",
        int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
            * 1000
        ),
    )
    save_end_player_session(
        "4242",
        int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
            * 1000
        ),
    )
    add_player_to_blacklist("4242", "test")
    remove_player_from_blacklist("4242")

    import pprint

    pprint.pprint(get_players_by_appearance())

    add_flag_to_player("76561198156263725", "🐷")

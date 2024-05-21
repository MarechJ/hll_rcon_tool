import datetime
import logging
import math
import os
import unicodedata
from functools import cmp_to_key

from sqlalchemy import func, or_
from sqlalchemy.orm import contains_eager, selectinload, Session
from sqlalchemy.sql.functions import ReturnTypeFromArgs

from rcon.commands import CommandFailedError
from rcon.models import (
    BlacklistRecord,
    PlayerActionType,
    PlayerComment,
    PlayerFlag,
    PlayerID,
    PlayerName,
    PlayersAction,
    PlayerSession,
    SteamInfo,
    WatchList,
    enter_session,
)
from rcon.types import PlayerCommentType, PlayerFlagType, PlayerProfileType
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig


class unaccent(ReturnTypeFromArgs):
    pass


logger = logging.getLogger(__name__)


def player_has_flag(player_dict, flag) -> bool:
    flags = player_dict.get("flags") or []

    return flag in {flag["flag"] for flag in flags}


def get_player(sess: Session, player_id: str) -> PlayerID | None:
    return sess.query(PlayerID).filter(PlayerID.player_id == player_id).one_or_none()


def get_player_profile(player_id, nb_sessions):
    with enter_session() as sess:
        player = (
            sess.query(PlayerID).filter(PlayerID.player_id == player_id).one_or_none()
        )
        if player is None:
            return
        return player.to_dict(limit_sessions=nb_sessions)


def get_player_profile_by_ids(sess, ids):
    return (
        sess.query(PlayerID)
        .filter(PlayerID.id.in_(ids))
        .options(
            selectinload(PlayerID.names),
            selectinload(PlayerID.received_actions),
            selectinload(PlayerID.b),
            selectinload(PlayerID.flags),
            selectinload(PlayerID.watchlist),
            selectinload(PlayerID.steaminfo),
        )
        .all()
    )


def get_player_profile_by_player_ids(sess, player_ids):
    return (
        sess.query(PlayerID)
        .filter(PlayerID.player_id.in_(player_ids))
        .options(
            selectinload(PlayerID.names),
            selectinload(PlayerID.received_actions),
            selectinload(PlayerID.blacklists),
            selectinload(PlayerID.flags),
            selectinload(PlayerID.watchlist),
            selectinload(PlayerID.steaminfo),
        )
        .all()
    )


def get_player_profile_by_id(id, nb_sessions):
    with enter_session() as sess:
        player = sess.query(PlayerID).filter(PlayerID.id == id).one_or_none()
        if player is None:
            return
        return player.to_dict(limit_sessions=nb_sessions)


def _get_profiles(sess, player_ids, nb_sessions=0):
    return sess.query(PlayerID).filter(PlayerID.player_id.in_(player_ids)).all()


def get_profiles(player_ids, nb_sessions=1):
    with enter_session() as sess:
        players = _get_profiles(sess, player_ids, nb_sessions)

        return [p.to_dict(limit_sessions=nb_sessions) for p in players]


def _get_set_player(
    sess,
    player_id: str,
    player_name: str | None = None,
    timestamp: float | None = None,
):
    player = get_player(sess, player_id)
    if player is None:
        player = _save_player_id(sess, player_id)
    if player_name:
        _save_player_alias(
            sess, player, player_name, timestamp or datetime.datetime.now().timestamp()
        )

    return player


def remove_accent(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("utf-8")


def get_players_by_appearance(
    page: int = 1,
    page_size: int = 500,
    last_seen_from: datetime.datetime | None = None,
    last_seen_till: datetime.datetime | None = None,
    player_id: str | None = None,
    player_name: str | None = None,
    blacklisted: bool | None = None,
    is_watched: bool | None = None,
    exact_name_match: bool = False,
    ignore_accent: bool = True,
    flags: str | list[str] | None = None,
    country: str | None = None,
):
    if page <= 0:
        raise ValueError("page needs to be >= 1")
    if page_size <= 0:
        raise ValueError("page_size needs to be >= 1")

    with enter_session() as sess:
        sub = (
            sess.query(
                PlayerSession.player_id_id,
                func.min(
                    func.coalesce(PlayerSession.start, PlayerSession.created)
                ).label("first"),
                func.max(func.coalesce(PlayerSession.end, PlayerSession.created)).label(
                    "last"
                ),
            )
            .group_by(PlayerSession.player_id_id)
            .subquery()
        )
        query = sess.query(PlayerID, sub.c.first, sub.c.last).outerjoin(
            sub, sub.c.player_id_id == PlayerID.id
        )

        if player_id:
            query = query.filter(PlayerID.player_id.ilike("%{}%".format(player_id)))

        if player_name:
            search = PlayerName.name
            if ignore_accent:
                search = unaccent(PlayerName.name)
                player_name = remove_accent(player_name)
            if not exact_name_match:
                query = query.join(PlayerID.names).filter(
                    search.ilike("%{}%".format(player_name))
                )
            else:
                query = query.join(PlayerID.names).filter(search == player_name)

        if blacklisted is True:
            query = query.filter(
                sess.query(BlacklistRecord)
                .where(
                    BlacklistRecord.player_id_id == PlayerID.id,
                    or_(
                        BlacklistRecord.expires_at.is_(None),
                        BlacklistRecord.expires_at < func.now(),
                    )
                )
                .exists()
            )
        if is_watched is True:
            query = (
                query.join(PlayerID.watchlist)
                .filter(WatchList.is_watched == True)
                .options(contains_eager(PlayerID.watchlist))
            )

        if flags:
            if not isinstance(flags, list):
                flags = [flags]
            query = query.join(PlayerID.flags).filter(PlayerFlag.flag.in_(flags))

        if country:
            query = query.join(PlayerID.steaminfo).filter(
                SteamInfo.country == country.upper()
            )

        if last_seen_from:
            query = query.filter(sub.c.last >= last_seen_from)
        if last_seen_till:
            query = query.filter(sub.c.last <= last_seen_till)

        total = query.count()
        page = min(max(math.ceil(total / page_size), 1), page)
        players = (
            query.order_by(func.coalesce(sub.c.last, PlayerID.created).desc())
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
                    "first_seen_timestamp_ms": (
                        int(p[1].timestamp() * 1000) if p[1] else None
                    ),
                    "last_seen_timestamp_ms": (
                        int(p[2].timestamp() * 1000) if p[2] else None
                    ),
                    "vip_expiration": p[0].vip.expiration if p[0].vip else None,
                }
                for p in players
            ],
            "page": page,
            "page_size": page_size,
        }


def _save_player_id(sess, player_id: str) -> PlayerID:
    player = get_player(sess, player_id)

    if not player:
        player = PlayerID(player_id=player_id)
        sess.add(player)
        logger.info("Adding first time seen %s", player_id)
        sess.commit()

    return player


def _save_player_alias(sess, player: PlayerID, player_name: str, timestamp=None):
    name = (
        sess.query(PlayerName)
        .filter(PlayerName.name == player_name, PlayerName.player == player)
        .one_or_none()
    )

    if timestamp:
        dt = datetime.datetime.fromtimestamp(timestamp)
    else:
        dt = datetime.datetime.now()
    if not name:
        name = PlayerName(name=player_name, player=player, last_seen=dt)
        sess.add(name)
        logger.info("Adding player %s with new name %s", player.player_id, player_name)
        sess.commit()
    else:
        name.last_seen = dt
        sess.commit()

    return name


def save_player(player_name: str, player_id: str, timestamp: int | None = None) -> None:
    """Create a PlayerID record if non existent and save the player name alias"""
    with enter_session() as sess:
        player = _save_player_id(sess, player_id)
        _save_player_alias(
            sess, player, player_name, timestamp or datetime.datetime.now().timestamp()
        )


def save_player_action(
    rcon,
    action_type,
    player_name: str,
    by: str,
    reason: str = "",
    player_id: str | None = None,
    timestamp=None,
):
    with enter_session() as sess:
        player_id = (
            player_id or rcon.get_player_info(player_name, can_fail=True)["player_id"]
        )
        player = _get_set_player(
            sess, player_name=player_name, player_id=player_id, timestamp=timestamp
        )
        sess.add(
            PlayersAction(
                action_type=action_type.upper(), player=player, reason=reason, by=by
            )
        )


def safe_save_player_action(
    rcon,
    action_type,
    player_name: str,
    by: str,
    reason: str = "",
    player_id: str | None = None,
):
    try:
        return save_player_action(rcon, action_type, player_name, by, reason, player_id)
    except Exception as e:
        logger.exception(
            "Failed to record player action: %s %s", action_type, player_name
        )
        return False


def save_start_player_session(
    player_id: str, timestamp, server_name: str | None = None, server_number=None
):
    config = RconServerSettingsUserConfig.load_from_db()

    server_name = server_name or config.short_name
    server_number = server_number or os.getenv("SERVER_NUMBER")

    with enter_session() as sess:
        player = get_player(sess, player_id)
        if not player:
            logger.error(
                "Can't record player session for %s, player not found", player_id
            )
            return

        start_time = datetime.datetime.fromtimestamp(timestamp)
        already_saved = (
            sess.query(PlayerSession)
            .filter(PlayerSession.player == player)
            .filter(PlayerSession.start == start_time)
            .first()
        )

        if already_saved is not None:
            logger.info(
                f"Player session starting at {start_time} for player {player_id} already recorded, skipping..."
            )
            return

        sess.add(
            PlayerSession(
                player=player,
                start=start_time,
                server_name=server_name,
                server_number=server_number,
            )
        )
        logger.info(
            "Recorded player %s session start at %s",
            player_id,
            datetime.datetime.fromtimestamp(timestamp),
        )
        sess.commit()


def save_end_player_session(player_id: str, timestamp):
    with enter_session() as sess:
        player = get_player(sess, player_id)
        if not player:
            logger.error(
                "Can't record player session for %s, player not found", player_id
            )
            return

        last_session = (
            sess.query(PlayerSession)
            .filter(PlayerSession.player == player)
            .order_by(PlayerSession.created.desc())
            .first()
        )

        if last_session is None:
            logger.warning(
                "Can't record player session for %s, last session not found",
                player_id,
            )
            return

        if last_session.end:
            logger.warning(
                "Last session was already ended for %s. Creating a new one instead",
                player_id,
            )
            last_session = PlayerSession(
                player=player,
            )
        last_session.end = datetime.datetime.fromtimestamp(timestamp)
        logger.info("Recorded player %s session end at %s", player_id, last_session.end)
        sess.commit()


def add_flag_to_player(
    player_id: str,
    flag: str,
    comment: str | None = None,
    player_name: str | None = None,
) -> tuple[PlayerProfileType, PlayerFlagType]:
    with enter_session() as sess:
        player = _get_set_player(sess, player_name=player_name, player_id=player_id)
        exists = (
            sess.query(PlayerFlag)
            .filter(PlayerFlag.player_id_id == player.id, PlayerFlag.flag == flag)
            .all()
        )
        if exists:
            logger.warning("Flag already exists")
            raise CommandFailedError("Flag already exists")
        new = PlayerFlag(flag=flag, comment=comment, player=player)
        sess.add(new)
        sess.commit()
        res = player.to_dict()
        return res, new.to_dict()


def remove_flag(
    flag_id: int | None = None, player_id: str | None = None, flag: str | None = None
) -> tuple[PlayerProfileType, PlayerFlagType]:
    with enter_session() as sess:
        if isinstance(flag_id, int):
            exists = (
                sess.query(PlayerFlag)
                .filter(PlayerFlag.id == int(flag_id))
                .one_or_none()
            )
        else:
            exists = (
                sess.query(PlayerFlag)
                .filter(PlayerID.player_id == player_id)
                .filter(PlayerFlag.flag == flag)
                .one_or_none()
            )

        if not exists:
            logger.warning("Flag does not exists")
            raise CommandFailedError("Flag does not exists")
        player = exists.player.to_dict()
        old_flag = exists.to_dict()
        sess.delete(exists)
        sess.commit()

    return player, old_flag


def get_player_messages(player_id: str) -> list[PlayerActionType]:
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one_or_none()
        actions: list[PlayerActionType] = []
        if player:
            actions = [
                action.to_dict()
                for action in player.received_actions
                if action.action_type == "MESSAGE"
            ]

        return actions


def get_player_comments(player_id: str) -> list[PlayerCommentType]:
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one()
        return [c.to_dict() for c in player.comments]


def post_player_comment(player_id: str, comment, user: str = "Bot"):
    with enter_session() as sess:
        player = sess.query(PlayerID).filter_by(player_id=player_id).one()
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

    import pprint

    pprint.pprint(get_players_by_appearance())

    add_flag_to_player("76561198156263725", "🐷")

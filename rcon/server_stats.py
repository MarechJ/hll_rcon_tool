import os
from rcon.player_history import get_players_by_time
from rcon.models import (
    Maps,
    enter_session,
    PlayerSession,
    PlayerName,
    PlayerSteamID,
    ServerCount,
    PlayerAtCount,
)
import datetime
import pandas as pd
import math
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from rcon.cache_utils import ttl_cache
import logging

logger = logging.getLogger(__name__)


def trunc_datetime_to_hour(dt):
    return dt.replace(second=0, microsecond=0, minute=0)


def index_range_objs_per_hours(time_range_objects):
    """
    To quickly lookup which map was running at a certain time we index them by hours
    """
    indexed_objs_by_hours = {}

    for obj in time_range_objects:
        start_hour = trunc_datetime_to_hour(obj.start)
        end_hour = trunc_datetime_to_hour(obj.end or datetime.datetime.now())
        indexed_objs_by_hours.setdefault(start_hour, []).append(obj)
        if start_hour != end_hour:
            # add entries for all hours in the range.
            # This is necessary for map that strech several hours (mostly when server is empty)
            delta = end_hour - start_hour
            for h in range(1, math.ceil(delta.total_seconds() / 60 / 60)):
                indexed_objs_by_hours.setdefault(
                    start_hour + datetime.timedelta(hours=h), []
                ).append(obj)
            indexed_objs_by_hours.setdefault(end_hour, []).append(obj)

    return indexed_objs_by_hours


def get_obj_for_minute(minute, indexed_objs, first_only=True):
    matches = []
    for o in indexed_objs.get(trunc_datetime_to_hour(minute), []):
        end = o.end or datetime.datetime.now()
        if o.start <= minute <= end:
            if first_only:
                return o
            matches.append(o)

    return matches


def save_server_stats_for_last_hours(hours=24):
    start = datetime.datetime.now() - datetime.timedelta(hours=hours)
    end = datetime.datetime.now() - datetime.timedelta(hours=1)
    start.replace(minute=0, second=0, microsecond=0)
    end.replace(minute=0, second=0, microsecond=0)
    series = pd.date_range(start=start, end=end, freq="H")
    server_number = os.getenv("SERVER_NUMBER")

    logger.info("Saving stats from %s to %s", start, end)
    with enter_session() as sess:
        existing_hours = (
            sess.query(func.date_trunc("hour", ServerCount.datapoint_time))
            .filter(ServerCount.datapoint_time.between(start, end))
            .group_by(func.date_trunc("hour", ServerCount.datapoint_time))
            .all()
        )
        logger.debug("Existing hourly data points: %s", existing_hours)
        for hour in series.to_list():
            if hour in existing_hours:
                logger.debug("%s is already in the DB. Skipping", hour)
                continue
            # TODO catch failure per hour, not to block the whole batch
            stats = _get_server_stats(
                sess,
                start=hour,
                end=hour + datetime.timedelta(hours=1),
                by_map=False,
                return_models=True,
            )
            for item in stats:
                server_count = ServerCount(
                    server_number=server_number,
                    map_id=item["map"].id,  # TODO that might be None and crash
                    count=item["count"],
                    datapoint_time=item["minute"],
                )
                sess.add(server_count)
                sess.commit()
                players_at_counts = [
                    PlayerAtCount(servercount_id=server_count.id, playersteamid_id=player.id)
                    for player in item["players"]
                ]
                sess.bulk_save_objects(players_at_counts)
                sess.commit()


# @ttl_cache(60 * 10)
def get_server_stats_for_range(start=None, end=None, by_map=False):
    if start is None:
        start = datetime.datetime.now() - datetime.timedelta(hours=24)
    if end is None:
        end = datetime.datetime.now() - datetime.timedelta(hours=0)

    if start > end:
        raise ValueError("Start time can't be after end time")

    start.replace(second=0, microsecond=0)
    end.replace(second=0, microsecond=0)

    with enter_session() as sess:
        return _get_server_stats(sess, start, end, by_map)


def _get_server_stats(sess, start, end, by_map, return_models=False):

    # Crete a list of minutes for the given time window
    # Bear in mind that a huge window will impact perf a lot
    series = pd.date_range(start=start, end=end, freq="T")
    series = series.to_list()

    maps = (
        sess.query(Maps)
        .filter(or_(Maps.start.between(start, end), Maps.end.between(start, end)))
        .all()
    )
    indexed_map_hours = index_range_objs_per_hours(maps)

    # Get all players withing the time window
    q = (
        sess.query(PlayerSession)
        .filter(
            and_(
                PlayerSession.start >= start,
                or_(PlayerSession.end <= end, PlayerSession.end == None),
            )
        )
        .options(joinedload(PlayerSession.steamid))
    )
    indexed_sessions = index_range_objs_per_hours(q.all())

    stats = []
    if by_map:
        stats = {}
    for minute in series:
        # For every minute of the time window we add:
        # The map, and all the players that had a session at that minute
        # This algo is quite crappy but it works decently enough
        present_players = []
        map_ = get_obj_for_minute(minute, indexed_map_hours)
        # find the map that was running at that minute
        # for m in indexed_map_hours.get(trunc_datetime_to_hour(minute), []):
        #     if m.start <= minute <= m.end:
        #         map_ = m
        #         break

        # for player_session in sessions:
        #     if not player_session.start:
        #         # TODO handle current players
        #         continue
        #     session_end = player_session.end or end
        #     if player_session.start <= minute <= session_end:
        #         present_players.append(player_session.steamid.names[0].name)
        for player_session in get_obj_for_minute(
            minute, indexed_sessions, first_only=False
        ):
            if not return_models:
                present_players.append(
                    (
                        player_session.steamid.names[0].name,
                        player_session.steamid.steam_id_64,
                    )
                )
            else:
                present_players.append(player_session.steamid)
        map_name = map_.map_name if map_ else None
        item = {
            "minute": minute,
            "map": map_name if not return_models else map_,
            "count": len(present_players),
            "players": present_players,
        }
        if by_map:
            stats.setdefault(map_name, []).append(item)
        else:
            stats.append(item)
    return stats


if __name__ == "__main__":
    save_server_stats_for_last_hours()
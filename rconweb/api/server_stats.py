from os import stat
from rcon.player_history import get_players_by_time
from rcon.models import Maps, enter_session, PlayerSession, PlayerName, PlayerSteamID
import datetime
import pandas as pd
import math
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, session
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from django.views.decorators.csrf import csrf_exempt
from .auth import api_response, login_required
from rcon.cache_utils import ttl_cache
from .views import ctl, _get_data

@csrf_exempt
def get_server_stats(request):
    #data = _get_data(request)

    return api_response(
        result=_get_server_stats(by_map=True), error=None, failed=False, command="get_server_stats"
    )


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
       

@ttl_cache(60 * 10)
def _get_server_stats(start=None, end=None, by_map=False):
    if start is None:
        start = datetime.datetime.now() - datetime.timedelta(hours=24)
    if end is None:
        end = datetime.datetime.now() - datetime.timedelta(hours=0)

    if start > end:
        raise ValueError("Start time can't be after end time")

    start.replace(second=0, microsecond=0)
    end.replace(second=0, microsecond=0)

    with enter_session() as sess:
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
            for player_session in get_obj_for_minute(minute, indexed_sessions, first_only=False):
                present_players.append((player_session.steamid.names[0].name, player_session.steamid.steam_id_64))

            map_name = map_.map_name if map_ else None
            item = {
                "minute": minute,
                "map": map_name,
                "count": len(present_players),
                "players": present_players,
            }
            if by_map:
                stats.setdefault(map_name, []).append(item)
            else:
                stats.append(item)
    return stats

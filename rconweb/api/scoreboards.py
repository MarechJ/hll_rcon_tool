import logging
import os
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rcon import game_logs
from rcon.commands import CommandFailedError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.models import (
    LogLine,
    Maps,
    PlayerName,
    PlayerStats,
    PlayerSteamID,
    enter_session,
)
from rcon.recorded_commands import RecordedRcon
from rcon.scoreboard import (
    LiveStats,
    TimeWindowStats,
    current_game_stats,
    get_cached_live_game_stats,
)
from rcon.settings import SERVER_INFO
from rcon.steam_utils import get_steam_profile
from rcon.utils import LONG_HUMAN_MAP_NAMES, MapsHistory, map_name

from .auth import api_response, login_required, stats_login_required
from .views import _get_data, ctl

logger = logging.getLogger("rconweb")


@csrf_exempt
@stats_login_required
def live_scoreboard(request):
    stats = LiveStats()
    config = get_config()

    try:
        result = stats.get_cached_stats()
        result = {
            "snapshot_timestamp": result["snapshot_timestamp"],
            "refresh_interval_sec": config.get("LIVE_STATS", {}).get(
                "refresh_stats_seconds", 30
            ),
            "stats": result["stats"],
        }
        error = (None,)
        failed = False
    except Exception as e:
        logger.exception("Unable to produce live stats")
        result = {}
        error = ""
        failed = True

    return api_response(
        result=result, error=error, failed=failed, command="live_scoreboard"
    )


@csrf_exempt
@stats_login_required
def get_scoreboard_maps(request):
    data = _get_data(request)

    page_size = min(int(data.get("limit", 100)), 1000)
    page = max(1, int(data.get("page", 1)))
    server_number = data.get("server_number", os.getenv("SERVER_NUMBER"))

    with enter_session() as sess:
        query = (
            sess.query(Maps)
            .filter(Maps.server_number == server_number)
            .order_by(Maps.start.desc())
        )
        total = query.count()
        res = query.limit(page_size).offset((page - 1) * page_size).all()

        return api_response(
            result={
                "page": page,
                "page_size": page_size,
                "total": total,
                "maps": [
                    dict(
                        just_name=map_name(r.map_name),
                        long_name=LONG_HUMAN_MAP_NAMES.get(r.map_name, r.map_name),
                        **r.to_dict(),
                    )
                    for r in res
                ],
            },
            failed=False,
            command="get_scoreboard_maps",
        )


@csrf_exempt
@stats_login_required
def get_map_scoreboard(request):
    data = _get_data(request)
    error = None
    failed = False
    game = None

    try:
        map_id = int(data.get("map_id", None))
        with enter_session() as sess:
            game = sess.query(Maps).filter(Maps.id == map_id).one_or_none()
            # import ipdb; ipdb.set_trace()
            if not game:
                error = "No map for this ID"
                failed = True
            else:
                game = game.to_dict(with_stats=True)
    except Exception as e:
        game = None
        error = repr(e)
        failed = True

    return api_response(
        result=game, error=error, failed=failed, command="get_map_scoreboard"
    )


@csrf_exempt
@stats_login_required
def get_live_game_stats(request):
    stats = None
    error_ = None
    failed = True

    try:
        stats = get_cached_live_game_stats()
        failed = False
    except Exception as e:
        logger.exception("Failed to get live game stats")
        error_ = repr(e)

    return api_response(
        result=stats, error=error_, failed=failed, command="get_live_game_stats"
    )


@csrf_exempt
@login_required()
def date_scoreboard(request):
    try:
        start = datetime.fromtimestamp(request.GET.get("start"))
    except (ValueError, KeyError, TypeError) as e:
        start = datetime.now() - timedelta(minutes=60)
    try:
        end = datetime.fromtimestamp(request.GET.get("end"))
    except (ValueError, KeyError, TypeError) as e:
        end = datetime.now()

    stats = TimeWindowStats()

    try:
        result = stats.get_players_stats_at_time(start, end)
        error_ = (None,)
        failed = False

    except Exception as e:
        logger.exception("Unable to produce date stats")
        result = {}
        error_ = ""
        failed = True

    return api_response(
        result=result, error=error_, failed=failed, command="date_scoreboard"
    )

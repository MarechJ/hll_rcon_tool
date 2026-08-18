import logging
import os
from datetime import UTC, datetime

from django.views.decorators.csrf import csrf_exempt

from rcon.api_commands import get_rcon_api
from rcon.game import get_game_profile
from rcon.maps import Layer
from rcon.models import Maps, enter_session
from rcon.player_stats import LiveStats, get_cached_live_game_stats
from rcon.types import GameEnum
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.utils import MapsHistory

from .auth import api_response, stats_login_required
from .decorators import require_http_methods
from .views import _get_data

logger = logging.getLogger("rconweb")


def parse_recorded_layer(record: Maps) -> Layer:
    """Resolve a stored map name against the game the match was played on.

    Every row carries the game it belongs to, so historical records stay
    correct even after a server switches games. Resolving against the WWII
    catalog unconditionally leaves Vietnam matches with a placeholder layer:
    the ID title-cased into a name ("Wdevc") and default WWII factions.
    """
    return get_game_profile(GameEnum.from_int(record.game)).parse_layer(
        record.map_name
    )


@csrf_exempt
@stats_login_required
@require_http_methods(["GET"])
def get_live_scoreboard(request):
    """Return stats for all currently connected players (stats are reset on disconnect, not match start)"""
    stats = LiveStats()
    config = RconServerSettingsUserConfig.load_from_db()
    try:
        result = stats.get_cached_stats()
        result = {
            "snapshot_timestamp": result["snapshot_timestamp"],
            "refresh_interval_sec": config.live_stats_refresh_seconds,
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
@require_http_methods(["GET"])
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

        maps = []
        for record in res:
            layer = parse_recorded_layer(record)
            r = record.to_dict()
            maps.append(
                dict(
                    map=layer,
                    id=r["id"],
                    creation_time=r["creation_time"],
                    start=r["start"],
                    end=r["end"],
                    server_number=r["server_number"],
                    player_stats=r["player_stats"],
                    result=r["result"],
                )
            )

        return api_response(
            result={
                "page": page,
                "page_size": page_size,
                "total": total,
                "maps": maps,
            },
            failed=False,
            command="get_scoreboard_maps",
        )


@csrf_exempt
@stats_login_required
@require_http_methods(["GET"])
def get_map_scoreboard(request):
    data = _get_data(request)
    error = None
    failed = False

    try:
        map_id = int(data.get("map_id", None))
        with enter_session() as sess:
            game = sess.query(Maps).filter(Maps.id == map_id).one_or_none()
            if not game:
                error = "No map for this ID"
                failed = True
            else:
                layer = parse_recorded_layer(game)
                game = game.to_dict(with_stats=True)
                game["map"] = layer

                logs = get_rcon_api().get_historical_logs(
                    action="KILL",
                    from_=game["start"],
                    till=game["end"],
                    limit=100000,
                    time_sort="asc",
                    exact_action=True,
                    server_filter=str(game["server_number"]),
                )
                encounters = {
                    stats["player_id"]: [] for stats in game["player_stats"]
                }
                
                for log in logs:
                    ts = int(
                        (log["event_time"].replace(tzinfo=UTC) - game["start"].replace(tzinfo=UTC)).total_seconds()
                    )
                    killer_id = log["player1_id"]
                    victim_id = log["player2_id"]
                    if killer_id in encounters:
                        encounters[killer_id].append(
                            {
                                "action": "KILL",
                                "player_id": victim_id,
                                "player_name": log["player2_name"],
                                "ts": ts,
                                "weapon": log["weapon"],
                            }
                        )
                    if victim_id in encounters:
                        encounters[victim_id].append(
                            {
                                "action": "DEATH",
                                "player_id": killer_id,
                                "player_name": log["player1_name"],
                                "ts": ts,
                                "weapon": log["weapon"],
                            }
                        )

                for stats in game["player_stats"]:
                    stats["encounters"] = encounters[stats["player_id"]]
    except Exception as e:
        game = None
        error = repr(e)
        failed = True

    return api_response(
        result=game,
        arguments=data,
        error=error,
        failed=failed,
        command="get_map_scoreboard",
    )


@csrf_exempt
@stats_login_required
@require_http_methods(["GET"])
def get_live_game_stats(request):
    """Return stats for the currently playing match"""
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
@stats_login_required
@require_http_methods(["GET"])
def get_map_history(request):
    data = _get_data(request)
    res = MapsHistory()[:]
    if data.get("pretty"):
        res = [
            dict(
                name=i["name"],
                start=(
                    datetime.fromtimestamp(i["start"]).isoformat()
                    if i["start"]
                    else None
                ),
                end=datetime.fromtimestamp(i["end"]).isoformat() if i["end"] else None,
            )
            for i in res
        ]
    return api_response(
        result=res, command="get_map_history", arguments={}, failed=False
    )


@csrf_exempt
@stats_login_required
@require_http_methods(["GET"])
def get_previous_map(request):
    command_name = "get_previous_map"
    try:
        prev_map = MapsHistory()[1]
        res = {
            "name": prev_map["name"],
            "start": (
                datetime.fromtimestamp(prev_map["start"]).isoformat()
                if prev_map["start"]
                else None
            ),
            "end": (
                datetime.fromtimestamp(prev_map["end"]).isoformat()
                if prev_map["end"]
                else None
            ),
        }

        return api_response(result=res, command=command_name, failed=False)
    except IndexError:
        return api_response(result=None, command=command_name, failed=False)
    except Exception as e:
        logger.exception(e)
        return api_response(
            result=None, command=command_name, failed=True, error=str(e)
        )

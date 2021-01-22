import datetime
import logging
import json

from dateutil import parser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.utils import MapsHistory
from rcon.recorded_commands import RecordedRcon
from rcon.commands import CommandFailedError
from rcon.steam_utils import get_steam_profile
from rcon.settings import SERVER_INFO
from rcon.player_history import (
    get_players_by_appearance,
    add_player_to_blacklist,
    remove_player_from_blacklist,
    get_player_profile,
    get_player_profile_by_id,
    add_flag_to_player,
    remove_flag,
)
from rcon.game_logs import ChatLoop
from rcon.user_config import AutoBroadcasts, InvalidConfigurationError, StandardMessages
from rcon.cache_utils import RedisCached, get_redis_pool
from .auth import login_required, api_response
from .utils import _get_data
from rcon.discord import send_to_discord_audit


logger = logging.getLogger("rconweb")

@csrf_exempt
@login_required
def get_map_history(request):
    data = _get_data(request)
    res = MapsHistory()[:]
    if data.get("pretty"):
        res = [
            dict(
                name=i["name"],
                start=datetime.datetime.fromtimestamp(i["start"]).isoformat()
                if i["start"]
                else None,
                end=datetime.datetime.fromtimestamp(i["end"]).isoformat()
                if i["end"]
                else None,
            )
            for i in res
        ]
    return api_response(
        result=res, command="get_map_history", arguments={}, failed=False
    )



@csrf_exempt
@login_required
def get_player(request):
    data = _get_data(request)
    res = {}
    try:
        if s := data.get("steam_id_64"):
            res = get_player_profile(s, nb_sessions=data.get("nb_sessions", 10))
        else:
            res = get_player_profile_by_id(
                data["id"], nb_sessions=data.get("nb_sessions", 10)
            )
        failed = bool(res)
    except:
        logger.exception("Unable to get player %s", data)
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "get_player_profile",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required
def flag_player(request):
    data = _get_data(request)
    res = None
    try:
        player, flag = add_flag_to_player(
            steam_id_64=data["steam_id_64"],
            flag=data["flag"],
            comment=data.get("comment"),
        )
        res = flag
        send_to_discord_audit(
            "`flag`: steam_id_64: `{}` player: `{}` flag: `{}`comment:`{}`".format(
                data["steam_id_64"],
                " | ".join(n["name"] for n in player["names"]),
                flag["flag"],
                data.get("comment", ""),
            ),
            request.user.username,
        )
    except KeyError:
        logger.warning("Missing parameters")
        # TODO return 400
    except CommandFailedError:
        logger.exception("Failed to flag")
    return JsonResponse(
        {"result": res, "command": "flag_player", "arguments": data, "failed": not res}
    )


@csrf_exempt
@login_required
def unflag_player(request):
    # Note is this really not restful
    data = _get_data(request)
    res = None
    try:
        player, flag = remove_flag(data["flag_id"])
        res = flag
        send_to_discord_audit(
            "`unflag`: flag: `{}` player: `{}`".format(
                flag["flag"], " | ".join(n["name"] for n in player["names"])
            ),
            request.user.username,
        )
    except KeyError:
        logger.warning("Missing parameters")
        # TODO return 400
    except CommandFailedError:
        logger.exception("Failed to remove flag")
    return JsonResponse(
        {"result": res, "command": "flag_player", "arguments": data, "failed": not res}
    )

@csrf_exempt
@login_required
def players_history(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET

    type_map = {
        "last_seen_from": parser.parse,
        "last_seen_till": parser.parse,
        "player_name": str,
        "blacklisted": bool,
        "is_watched": bool,
        "steam_id_64": str,
        "page": int,
        "page_size": int,
        "ignore_accent": bool,
        "exact_name_match": bool,
    }

    try:
        arguments = {}
        for k, v in data.items():
            if k not in type_map:
                continue
            arguments[k] = type_map[k](v)

        res = get_players_by_appearance(**arguments)
        failed = False
    except:
        logger.exception("Unable to get player history")
        res = {}
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "players_history",
            "arguments": data,
            "failed": failed,
        }
    )
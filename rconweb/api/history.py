import datetime
import json
import logging

from dateutil import parser
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rcon import player_history
from rcon.commands import CommandFailedError
from rcon.discord import send_to_discord_audit
from rcon.player_history import (
    add_flag_to_player,
    get_player_comments,
    get_player_profile,
    get_player_profile_by_id,
    get_players_by_appearance,
    post_player_comments,
    remove_flag,
)
from rcon.utils import MapsHistory

from .audit_log import record_audit
from .auth import api_response, login_required, stats_login_required
from .decorators import require_content_type
from .utils import _get_data

logger = logging.getLogger("rconweb")


@csrf_exempt
@stats_login_required
@require_http_methods(['GET'])
def get_previous_map(request):
    command_name = "get_previous_map"
    try:
        prev_map = MapsHistory()[1]
        res = {
            "name": prev_map['name'],
            "start": datetime.datetime.fromtimestamp(prev_map['start']).isoformat() if prev_map['start'] else None,
            "end": datetime.datetime.fromtimestamp(prev_map['end']).isoformat() if prev_map['end'] else None,
        }

        return api_response(result=res, command=command_name, failed=False)
    except IndexError:
        return api_response(result=None,command=command_name, failed=False)
    except Exception as e:
        logger.exception(e)
        return api_response(result=None, command=command_name, failed=True, error=str(e))


@csrf_exempt
@stats_login_required
@require_http_methods(['GET'])
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
@login_required()
@permission_required("api.can_view_player_profile", raise_exception=True)
@require_http_methods(['GET'])
def get_player(request):
    data = _get_data(request)
    res = {}

    try:
        nb_sessions = int(data.get("nb_sessions", 10))
    except ValueError:
        nb_sessions = 10

    try:
        if s := data.get("steam_id_64"):
            res = get_player_profile(s, nb_sessions=nb_sessions)
        else:
            res = get_player_profile_by_id(data["id"], nb_sessions=nb_sessions)
        failed = False
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
@login_required()
@permission_required("api.can_flag_player", raise_exception=True)
@record_audit
@require_http_methods(['POST'])
@require_content_type()
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
@login_required()
@permission_required("api.can_unflag_player", raise_exception=True)
@record_audit
@require_http_methods(['POST'])
@require_content_type()
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
@login_required()
@permission_required("api.can_view_player_history", raise_exception=True)
@require_http_methods(['POST'])
@require_content_type()
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
        "country": str,
        "flags": lambda s: [f for f in s.split(",") if f] if s else "",
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


@csrf_exempt
@login_required()
@permission_required("api.can_view_player_messages", raise_exception=True)
@require_http_methods(['GET'])
def get_player_messages(request):
    data = _get_data(request)
    res = None
    try:
        res = player_history.get_player_messages(steam_id_64=data.get("steam_id_64"))
        failed = False
    except:
        logger.exception("Unable to get player message history")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "player_messages",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_player_comments", raise_exception=True)
@require_http_methods(['GET'])
def get_player_comment(request):
    data = _get_data(request)
    res = None
    try:
        res = get_player_comments(steam_id_64=data["steam_id_64"])
        failed = False
    except:
        logger.exception("Unable to get player comments")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "player_comments",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required()
@permission_required("api.can_add_player_comments", raise_exception=True)
@require_http_methods(['POST'])
@require_content_type()
@record_audit
def post_player_comment(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET

    try:
        post_player_comments(
            steam_id_64=data["steam_id_64"],
            comment=data["comment"],
            user=request.user.username,
        )
        failed = False
    except:
        failed = True
        logger.exception("Unable to get player comments")

    return JsonResponse(
        {
            "result": "",
            "command": "player_comments",
            "arguments": data,
            "failed": failed,
        }
    )

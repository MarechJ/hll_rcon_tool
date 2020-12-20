import inspect
import logging
import json
import datetime
from functools import wraps
import os
from redis import StrictRedis

from dateutil import parser
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

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
from rcon import game_logs
from rcon.game_logs import ChatLoop
from rcon.user_config import AutoBroadcasts, InvalidConfigurationError, StandardMessages
from rcon.cache_utils import RedisCached, get_redis_pool
from .auth import login_required, api_response
from .utils import _get_data
from .multi_servers import forward_request
from rcon.discord import send_to_discord_audit
from subprocess import run, PIPE
import unicodedata

logger = logging.getLogger("rconweb")


@csrf_exempt
def get_version(request):
    res = run(["git", "describe", "--tags"], stdout=PIPE, stderr=PIPE)
    return HttpResponse(res.stdout.decode())


from rcon.models import LogLine, PlayerSteamID, PlayerName, enter_session
from sqlalchemy import or_, and_


@csrf_exempt
@login_required
def get_historical_logs(request):
    data = _get_data(request)
    player_name = data.get("player_name")
    action = data.get("log_type")
    steam_id_64 = data.get("steam_id_64")
    limit = int(data.get("limit", 1000))
    from_ = data.get("from")
    till = data.get("till")
    time_sort = data.get("time_sort", "desc")

    with enter_session() as sess:
        names = []
        name_filters = []

        q = sess.query(LogLine)
        if action:
            q = q.filter(LogLine.type.ilike(f"%{action}%"))

        time_filter = []
        if from_:
            from_ = parser.parse(from_)
            time_filter.append(LogLine.event_time >= from_)

        if till:
            till = parser.parse(till)
            time_filter.append(LogLine.event_time <= till)

        q = q.filter(and_(*time_filter))

        if steam_id_64:
            # Handle not found
            player = (
                sess.query(PlayerSteamID)
                .filter(PlayerSteamID.steam_id_64 == steam_id_64)
                .one_or_none()
            )
            id_ = player.id if player else 0
            q = q.filter(
                or_(LogLine.player1_steamid == id_, LogLine.player2_steamid == id_)
            )

        if player_name:
            name_filters.extend(
                [
                    LogLine.player1_name.ilike("%{}%".format(player_name)),
                    LogLine.player2_name.ilike("%{}%".format(player_name)),
                ]
            )

        if name_filters:
            q = q.filter(or_(*name_filters))

        res = (
            q.order_by(
                LogLine.event_time.desc()
                if time_sort == "desc"
                else LogLine.event_time.asc()
            )
            .limit(limit)
            .all()
        )

        lines = []
        for r in res:
            r = r.to_dict()
            r["event_time"] = r["event_time"].timestamp()
            lines.append(r)
        return api_response(
            lines,
            command="get_historical_logs",
            arguments=dict(limit=limit, player_name=player_name, action=action),
            failed=False,
        )


@csrf_exempt
@login_required
def get_recent_logs(request):
    data = _get_data(request)
    start = int(data.get("start", 0))
    end = int(data.get("end", 10000))
    player_search = data.get("filter_player")
    action_filter = data.get("filter_action")

    return api_response(
        result=game_logs.get_recent_logs(
            start=start,
            end=end,
            player_search=player_search,
            action_filter=action_filter,
        ),
        command="get_recent_logs",
        arguments=dict(
            start=start,
            end=end,
            filter_player=player_search,
            filter_action=action_filter,
        ),
        failed=False,
    )





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
def clear_cache(request):
    res = RedisCached.clear_all_caches(get_redis_pool())
    audit("clear_cache", request, {})
    return JsonResponse(
        {
            "result": res,
            "command": "clear_cache",
            "arguments": None,
            "failed": res is None,
        }
    )


@csrf_exempt
@login_required
def get_auto_broadcasts_config(request):
    failed = False
    config = None

    try:
        broadcasts = AutoBroadcasts()
        config = {
            "messages": ["{} {}".format(m[0], m[1]) for m in broadcasts.get_messages()],
            "randomized": broadcasts.get_randomize(),
            "enabled": broadcasts.get_enabled(),
        }
    except:
        logger.exception("Error fetch broadcasts config")
        failed = True

    return JsonResponse(
        {
            "result": config,
            "command": "get_auto_broadcasts_config",
            "arguments": None,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required
def set_auto_broadcasts_config(request):
    failed = False
    res = None
    data = _get_data(request)
    broadcasts = AutoBroadcasts()
    config_keys = {
        "messages": broadcasts.set_messages,
        "randomized": broadcasts.set_randomize,
        "enabled": broadcasts.set_enabled,
    }
    try:
        for k, v in data.items():
            if k in config_keys:
                config_keys[k](v)
                audit(set_auto_broadcasts_config.__name__, request, {k: v})
    except InvalidConfigurationError as e:
        failed = True
        res = str(e)

    return JsonResponse(
        {
            "result": res,
            "command": "set_auto_broadcasts_config",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required
def get_standard_messages(request):
    failed = False
    data = _get_data(request)

    try:
        msgs = StandardMessages()
        res = msgs.get_messages(data["message_type"])
    except CommandFailedError as e:
        failed = True
        res = repr(e)
    except:
        logger.exception("Error fetching standard messages config")
        failed = True
        res = "Error setting standard messages config"

    return JsonResponse(
        {
            "result": res,
            "command": "get_standard_messages",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required
def set_standard_messages(request):
    failed = False
    data = _get_data(request)

    try:
        msgs = StandardMessages()
        res = msgs.set_messages(data["message_type"], data["messages"])
        send_to_discord_audit("set_standard_messages", request.user.username)
    except CommandFailedError as e:
        failed = True
        res = repr(e)
    except:
        logger.exception("Error setting standard messages config")
        failed = True
        res = "Error setting standard messages config"

    return JsonResponse(
        {
            "result": res,
            "command": "get_standard_messages",
            "arguments": data,
            "failed": failed,
        }
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
def blacklist_player(request):
    data = _get_data(request)
    res = {}
    try:
        name = data["name"] if "name" in data else None
        ctl.do_perma_ban(
            steam_id_64=data["steam_id_64"], reason=data["reason"], by=name
        )
        # add_player_to_blacklist(data["steam_id_64"], data["reason"], name)
        audit("Blacklist", request, data)
        failed = False
    except:
        logger.exception("Unable to blacklist player")
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
@login_required
def unblacklist_player(request):
    data = _get_data(request)
    res = {}
    try:
        remove_player_from_blacklist(data["steam_id_64"])
        audit("unblacklist", request, data)
        failed = False
    except:
        logger.exception("Unable to unblacklist player")
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
        "steam_id_64": str,
        "page": int,
        "page_size": int,
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


def audit(func_name, request, arguments):
    dont_audit = ["get_"]

    try:
        if any(func_name.startswith(s) for s in dont_audit):
            return
        args = dict(**arguments)
        try:
            del args["by"]
        except KeyError:
            pass
        arguments = " ".join([f"{k}: `{v}`" for k, v in args.items()])
        send_to_discord_audit(
            "`{}`: {}".format(func_name, arguments), request.user.username
        )
    except:
        logger.exception("Can't send audit log")


# This is were all the RCON commands are turned into HTTP endpoints
def wrap_method(func, parameters):
    @csrf_exempt
    @login_required
    @wraps(func)
    def wrapper(request):
        logger = logging.getLogger("rconweb")
        arguments = {}
        data = {}
        failure = False
        others = None
        data = _get_data(request)

        for pname, param in parameters.items():
            if pname == "by":
                arguments[pname] = request.user.username
            elif param.default != inspect._empty:
                arguments[pname] = data.get(pname)
            else:
                try:
                    arguments[pname] = data[pname]
                except KeyError:
                    # TODO raise 400
                    raise

        try:
            logger.debug("%s %s", func.__name__, arguments)
            res = func(**arguments)
            audit(func.__name__, request, arguments)
        except CommandFailedError:
            failure = True
            res = None
        
        if data.get('forward'):
            try:
                others = forward_request(request)
            except: 
                logger.exception("Unexpected error while forwarding request")
        # logger.debug("%s %s -> %s", func.__name__, arguments, res)
        return JsonResponse(dict(
            result=res,
            command=func.__name__,
            arguments=data,
            failed=failure,
            forwards_results=others,
        ))

    return wrapper


ctl = RecordedRcon(SERVER_INFO)


def make_table(scoreboard):
    return "\n".join(
        ["Rank  Name                  Ratio Kills Death"]
        + [
            f"{('#'+ str(idx+1)).ljust(6)}{obj['player'].ljust(27)}{obj['ratio'].ljust(6)}{str(obj['(real) kills']).ljust(6)}{str(obj['(real) death']).ljust(5)}"
            for idx, obj in enumerate(scoreboard)
        ]
    )


def make_tk_table(scoreboard):
    justification = [6, 27, 10, 10, 14, 14]
    headers = ["Rank", "Name", "Time(min)", "Teamkills", "Death-by-TK", "TK/Minutes"]
    keys = [
        "idx",
        "player",
        "Estimated play time (minutes)",
        "Teamkills",
        "Death by TK",
        "TK Minutes",
    ]

    return "\n".join(
        ["".join(h.ljust(justification[idx]) for idx, h in enumerate(headers))]
        + [
            "".join(
                [
                    str({"idx": f"#{idx}", **obj}[key]).ljust(justification[i])
                    for i, key in enumerate(keys)
                ]
            )
            for idx, obj in enumerate(scoreboard)
        ]
    )


@csrf_exempt
def text_scoreboard(request):
    try:
        minutes = abs(int(request.GET.get("minutes")))
    except (ValueError, KeyError, TypeError):
        minutes = 180

    name = ctl.get_name()
    try:
        scoreboard = ctl.get_scoreboard(minutes, "ratio")
        text = make_table(scoreboard)
        scoreboard = ctl.get_scoreboard(minutes, "(real) kills")
        text2 = make_table(scoreboard)
    except CommandFailedError:
        text, text2 = "No logs"

    return HttpResponse(
        f"""<div>
        <h1>{name}</h1>
        <h1>Scoreboard (last {minutes} min. 2min delay)</h1>
        <h6>Real death only (redeploy / suicides not included). Kills counted only if player is not revived</h6>
        <p>
        See for last:
        <a href="/api/scoreboard?minutes=120">120 min</a>
        <a href="/api/scoreboard?minutes=90">90 min</a>
        <a href="/api/scoreboard?minutes=60">60 min</a>
        <a href="/api/scoreboard?minutes=30">30 min</a>
        </p>
        <div style="float:left; margin-right:20px"><h3>By Ratio</h3><pre>{text}</pre></div>
        <div style="float:left; margin-left:20px"><h3>By Kills</h3><pre>{text2}</pre></div>
        </div>
        """
    )


@csrf_exempt
def text_tk_scoreboard(request):
    name = ctl.get_name()
    try:
        scoreboard = ctl.get_teamkills_boards()
        text = make_tk_table(scoreboard)
        scoreboard = ctl.get_teamkills_boards("Teamkills")
        text2 = make_tk_table(scoreboard)
    except CommandFailedError:
        text, text2 = "No logs"

    return HttpResponse(
        f"""<div>
        <h1>{name}</h1>
        <div style="float:left; margin-right:20px"><h3>By TK / Minute</h3><pre>{text}</pre></div>
        <div style="float:left; margin-left:20px"><h3>By Total TK</h3><pre>{text2}</pre></div>
        </div>
        """
    )


from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms


class DocumentForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


@csrf_exempt
@login_required
def upload_vips(request):
    message = "Upload a VIP file!"
    send_to_discord_audit("upload_vips", request.user.username)
    # Handle file upload
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            message = ""
            vips = ctl.get_vip_ids()
            for vip in vips:
                ctl.do_remove_vip(vip["steam_id_64"])
            message = f"{len(vips)} removed\n"
            count = 0
            for name, data in request.FILES.items():
                if name.endswith(".json"):
                    message = "JSON is not handled yet"
                    break
                else:
                    for l in data:
                        try:
                            l = l.decode()
                            steam_id, name = l.split(" ", 1)
                            if len(steam_id) != 17:
                                raise ValueError
                            ctl.do_add_vip(name.strip(), steam_id)
                            count += 1
                        except UnicodeDecodeError:
                            message = "File encoding is not supported. Must use UTF8"
                            break
                        except ValueError:
                            message += f"Line: '{l}' is invalid, skipped\n"
                        except CommandFailedError:
                            message = "The game serveur returned an error while adding a VIP. You need to upload again"
                            break

                    message += f"{count} added"
        else:
            message = "The form is not valid. Fix the following error:"
    else:
        form = DocumentForm()  # An empty, unbound form

    # Render list page with the documents and the form
    context = {"form": form, "message": message}
    return render(request, "list.html", context)


@csrf_exempt
@login_required
def download_vips(request):
    vips = ctl.get_vip_ids()
    response = HttpResponse(
        "\n".join([f"{vip['steam_id_64']} {vip['name']}" for vip in vips]),
        content_type="text/plain",
    )
    response[
        "Content-Disposition"
    ] = f"attachment; filename={datetime.datetime.now().isoformat()}_vips.txt"
    return response


@login_required
@csrf_exempt
def get_connection_info(request):
    return api_response({'name': ctl.get_name(), 'port': os.getenv('RCONWEB_PORT')})


PREFIXES_TO_EXPOSE = ["get_", "set_", "do_"]

commands = [
    ("player", get_player),
    ("players_history", players_history),
    ("blacklist_player", blacklist_player),
    ("unblacklist_player", unblacklist_player),
    ("scoreboard", text_scoreboard),
    ("tk", text_tk_scoreboard),
    ("get_auto_broadcasts_config", get_auto_broadcasts_config),
    ("set_auto_broadcasts_config", set_auto_broadcasts_config),
    ("clear_cache", clear_cache),
    ("flag_player", flag_player),
    ("unflag_player", unflag_player),
    ("upload_vips", upload_vips),
    ("download_vips", download_vips),
    ("get_standard_messages", get_standard_messages),
    ("set_standard_messages", set_standard_messages),
    ("get_map_history", get_map_history),
    ("get_version", get_version),
    ("get_recent_logs", get_recent_logs),
    ("get_historical_logs", get_historical_logs),
    ("get_connection_info", get_connection_info),
]

logger.info("Initializing endpoint - %s", os.environ)

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
        continue

    commands.append((name, wrap_method(func, inspect.signature(func).parameters)))


# Warm the cache as fetching steam profile 1 by 1 takes a while
if not os.getenv("DJANGO_DEBUG", None):
    try:
        logger.info("Warming up the cache this may take minutes")
        ctl.get_players()
    except:
        logger.exception("Failed to warm the cache")
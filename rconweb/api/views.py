import inspect
import logging
from functools import wraps
import os
from subprocess import run, PIPE

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from rcon.config import get_config
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
from rcon.discord import send_to_discord_audit
from rcon.game_logs import ChatLoop
from rcon.user_config import AutoBroadcasts, InvalidConfigurationError, StandardMessages
from rcon.cache_utils import RedisCached, get_redis_pool

from .auth import login_required, api_response
from .utils import _get_data
from .multi_servers import forward_request, forward_command


logger = logging.getLogger("rconweb")


@csrf_exempt
def get_version(request):
    res = run(["git", "describe", "--tags"], stdout=PIPE, stderr=PIPE)
    return HttpResponse(res.stdout.decode())


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
def blacklist_player(request):
    data = _get_data(request)
    res = {}
    try:
        name = data["name"] if "name" in data else None
        # Using the the perma ban by steamid actually sucks because the player won't see the reason for his ban
        # Also it could seem interesting to use it, so that if the player is on the server at the time of the
        # Blacklist he'd be banned immediately, however that's not the case, which is apparently a bug
        # ctl.do_perma_ban(
        #     steam_id_64=data["steam_id_64"], reason=data["reason"], by=name
        # )
        add_player_to_blacklist(data["steam_id_64"], data["reason"], name, request.user.username)
        audit("Blacklist", request, data)
        failed = False
    except:
        logger.exception("Unable to blacklist player")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "blacklist_player",
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
        if get_config()["BANS"]["unblacklist_does_unban"]:
            ctl.do_unban(data["steam_id_64"])  # also remove bans
            if get_config()["MULTI_SERVERS"]["broadcast_unbans"]:
                forward_command(
                    "/api/do_unban",
                    json=data,
                    sessionid=request.COOKIES.get("sessionid"),
                )
        failed = False
    except:
        logger.exception("Unable to unblacklist player")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "unblacklist_player",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required
def unban(request):
    data = _get_data(request)
    res = {}
    results = None

    try:
        ctl.do_unban(data["steam_id_64"])  # also remove bans
        audit("unban", request, data)
        if get_config()["MULTI_SERVERS"]["broadcast_unbans"]:
            results = forward_command(
                "/api/do_unban", json=data, sessionid=request.COOKIES.get("sessionid")
            )
        if get_config()["BANS"]["unban_does_unblacklist"]:
            try:
                remove_player_from_blacklist(data["steam_id_64"])
            except CommandFailedError:
                logger.warning("Player %s was not on blacklist", data["steam_id_64"])
        failed = False
    except:
        logger.exception("Unable to unban player")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "unban_player",
            "arguments": data,
            "failed": failed,
            "forward_results": results
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

        if data.get("forward"):
            try:
                others = forward_request(request)
            except:
                logger.exception("Unexpected error while forwarding request")
        # logger.debug("%s %s -> %s", func.__name__, arguments, res)
        return JsonResponse(
            dict(
                result=res,
                command=func.__name__,
                arguments=data,
                failed=failure,
                forwards_results=others,
            )
        )

    return wrapper


ctl = RecordedRcon(SERVER_INFO)


@login_required
@csrf_exempt
def get_connection_info(request):
    return api_response(
        {"name": ctl.get_name(), "port": os.getenv("RCONWEB_PORT")},
        failed=False,
        command="get_connection_info",
    )


PREFIXES_TO_EXPOSE = ["get_", "set_", "do_"]

commands = [
    ("blacklist_player", blacklist_player),
    ("unblacklist_player", unblacklist_player),
    ("get_auto_broadcasts_config", get_auto_broadcasts_config),
    ("set_auto_broadcasts_config", set_auto_broadcasts_config),
    ("clear_cache", clear_cache),
    ("get_standard_messages", get_standard_messages),
    ("set_standard_messages", set_standard_messages),
    ("get_version", get_version),
    ("get_connection_info", get_connection_info),
    ("unban", unban),
]

logger.info("Initializing endpoint")

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
        logger.info("Cache warm up done")
    except:
        logger.exception("Failed to warm the cache")
import inspect
import logging
import os
import traceback
from functools import wraps
from subprocess import PIPE, run

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.broadcast import get_votes_status
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.commands import CommandFailedError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.gtx import GTXFtp
from rcon.player_history import (add_player_to_blacklist,
                                 remove_player_from_blacklist)
from rcon.recorded_commands import RecordedRcon
from rcon.extended_commands import MOD_ALLOWED_CMDS
from rcon.settings import SERVER_INFO
from rcon.user_config import (AutoBroadcasts, AutoVoteKickConfig, CameraConfig,
                              DiscordHookConfig, InvalidConfigurationError,
                              StandardMessages)
from rcon.utils import LONG_HUMAN_MAP_NAMES, MapsHistory, map_name
from rcon.watchlist import PlayerWatch
from rcon.workers import temporary_broadcast, temporary_welcome

from .auth import api_response, login_required
from .multi_servers import forward_command, forward_request
from .utils import _get_data

logger = logging.getLogger("rconweb")
ctl = RecordedRcon(SERVER_INFO)


def set_temp_msg(request, func, name):
    data = _get_data(request)
    failed = False
    error = None
    try:
        func(ctl, data["msg"], data["seconds"])
    except Exception as e:
        failed = True
        error = repr(e)

    return api_response(failed=failed, error=error, result=None, command=name)


@csrf_exempt
@login_required(True)
def set_name(request):
    data = _get_data(request)
    failed = False
    error = None
    try:
        gtx = GTXFtp.from_config()
        gtx.change_server_name(data["name"])
    except Exception as e:
        failed = True
        error = repr(e)
    return api_response(failed=failed, error=error, result=None, command="set_server_name")



@csrf_exempt
@login_required(True)
def set_temp_broadcast(request):
    return set_temp_msg(request, temporary_broadcast, "set_temp_broadcast")


@csrf_exempt
@login_required(True)
def set_temp_welcome(request):
    return set_temp_msg(request, temporary_welcome, "set_temp_welcome")


@csrf_exempt
def get_version(request):
    res = run(["git", "describe", "--tags"], stdout=PIPE, stderr=PIPE)
    return api_response(res.stdout.decode(), failed=False, command="get_version")


@csrf_exempt
def public_info(request):
    status = ctl.get_status()
    try:
        current_map = MapsHistory()[0]
    except IndexError:
        logger.error("Can't get current map time, map_recorder is probably offline")
        current_map = {"name": status["map"], "start": None, "end": None}
    current_map = dict(
        just_name=map_name(current_map["name"]),
        human_name=LONG_HUMAN_MAP_NAMES.get(current_map["name"], current_map["name"]),
        **current_map,
    )
    vote_status = get_votes_status(none_on_fail=True)
    next_map = ctl.get_next_map()
    return api_response(
        result=dict(
            current_map=current_map,
            **status,
            vote_status=vote_status,
            next_map=next_map,
            public_stats_port=os.getenv('PUBLIC_STATS_PORT', "Not defined"),
            public_stats_port_https=os.getenv('PUBLIC_STATS_PORT_HTTPS', "Not defined")
        ),
        failed=False,
        command="public_info",
    )


@csrf_exempt
@login_required(True)
def get_hooks(request):
    return api_response(
        result=DiscordHookConfig.get_all_hook_types(as_dict=True),
        command="get_hooks",
        failed=False,
    )


@csrf_exempt
@login_required(True)
def set_hooks(request):
    data = _get_data(request)

    hook_config = DiscordHookConfig(for_type=data["name"])
    hook_config.set_hooks(data["hooks"])

    audit("set_hooks", request, data)
    return api_response(
        result=DiscordHookConfig.get_all_hook_types(),
        command="get_hooks",
        failed=False,
    )


@csrf_exempt
@login_required(True)
def get_camera_config(request):
    config = CameraConfig()
    return api_response(
        result={
            "broadcast": config.is_broadcast(),
            "welcome": config.is_welcome(),
        },
        command="get_camera_config",
        failed=False,
    )


@csrf_exempt
@login_required(True)
def get_votekick_autotoggle_config(request):
    config = AutoVoteKickConfig()
    return api_response(
        result={
            "min_ingame_mods": config.get_min_ingame_mods(),
            "min_online_mods": config.get_min_online_mods(),
            "is_enabled": config.is_enabled(),
            "condition_type": config.get_condition_type(),
        },
        command="get_votekick_autotoggle_config",
        failed=False,
    )


@csrf_exempt
@login_required(True)
def set_votekick_autotoggle_config(request):
    config = AutoVoteKickConfig()
    data = _get_data(request)
    funcs = {
        "min_ingame_mods": config.set_min_ingame_mods,
        "min_online_mods": config.set_min_online_mods,
        "is_enabled": config.set_is_enabled,
        "condition_type": config.set_condition_type,
    }

    for k, v in data.items():
        try:
            funcs[k](v)
        except KeyError:
            return api_response(
                error="{} invalid key".format(k),
                command="set_votekick_autotoggle_config",
            )

        audit("set_votekick_autotoggle_config", request, {k: v})

    return api_response(
        command="set_votekick_autotoggle_config",
        failed=False,
    )


@csrf_exempt
@login_required(True)
def set_camera_config(request):
    config = CameraConfig()
    data = _get_data(request)

    funcs = {
        "broadcast": config.set_broadcast,
        "welcome": config.set_welcome,
    }

    for k, v in data.items():
        if not isinstance(v, bool):
            return api_response(
                error="Values must be boolean", command="set_camera_config"
            )
        try:
            funcs[k](v)
        except KeyError:
            return api_response(
                error="{} invalid key".format(k), command="set_camera_config"
            )

        audit("set_camera_config", request, {k: v})

    return api_response(
        result={
            "broadcast": config.is_broadcast(),
            "welcome": config.is_welcome(),
        },
        command="set_camera_config",
        failed=False,
    )


def _do_watch(request, add: bool):
    data = _get_data(request)
    error = None
    failed = True
    result = None

    try:
        watcher = PlayerWatch(data["steam_id_64"])
        if add:
            params = dict(
                reason=data["reason"],
                comment=data.get("comment"),
                player_name=data.get("player_name"),
            )
            result = watcher.watch(**params)
            audit("do_watch_player", request, params)
        else:
            result = watcher.unwatch()
            audit("do_unwatch_player", request, dict(steam_id_64=data["steam_id_64"]))
        failed = False
    except KeyError as e:
        error = f"No {e.args} provided"
    except CommandFailedError as e:
        error = e.args[0]

    return api_response(
        result=result,
        arguments=data,
        error=error,
        command="do_watch_player",
        failed=failed,
    )


@csrf_exempt
@login_required()
def do_watch_player(request):
    return _do_watch(request, add=True)


@csrf_exempt
@login_required()
def do_unwatch_player(request):
    return _do_watch(request, add=False)


@csrf_exempt
@login_required()
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
@login_required(True)
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
@login_required(True)
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
@login_required(True)
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
@login_required()
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
        add_player_to_blacklist(
            data["steam_id_64"], data["reason"], name, request.user.username
        )
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
@login_required()
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
@login_required()
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
            "forward_results": results,
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
def wrap_method(func, parameters, command_name, require_perms=False):
    @csrf_exempt
    @login_required(require_perms)
    @wraps(func)
    def wrapper(request):
        logger = logging.getLogger("rconweb")
        arguments = {}
        data = {}
        failure = False
        others = None
        error = ""
        data = _get_data(request)

        for pname, param in parameters.items():
            if pname == "by":
                arguments[pname] = request.user.username
            elif param.default != inspect._empty:
                arguments[pname] = data.get(pname, param.default)
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
        except CommandFailedError as e:
            failure = True
            error = e.args[0] if e.args else None
            res = None

        response = JsonResponse(
            dict(
                result=res,
                command=func.__name__,
                arguments=data,
                failed=failure,
                error=error,
                forward_results=others,
            )
        )
        if data.get("forward"):
            if command_name == "do_temp_ban" and not get_config().get(
                "MULTI_SERVERS", {}
            ).get("broadcast_temp_bans", True):
                logger.debug("Not broadcasting temp ban due to settings")
                return response
            try:
                others = forward_request(request)
            except:
                logger.exception("Unexpected error while forwarding request")
        # logger.debug("%s %s -> %s", func.__name__, arguments, res)
        return response

    return wrapper


@login_required()
@csrf_exempt
def get_connection_info(request):
    return api_response(
        {
            "name": ctl.get_name(),
            "port": os.getenv("RCONWEB_PORT"),
            "link": os.getenv("RCONWEB_SERVER_URL"),
        },
        failed=False,
        command="get_connection_info",
    )

@csrf_exempt
@login_required(True)
def run_raw_command(request):
    data = _get_data(request)
    command = data.get('command')
    if not command:
        res = "Parameter \"command\" must not be none"
    else:
        try:
            res = ctl._request(command, can_fail=True, log_info=True)
        except CommandFailedError:
            res = "Command returned FAIL"
        except:
            logging.exception("Internal error when executing raw command")
            res = "Internal error!\n\n" + traceback.format_exc()
    return HttpResponse(res, content_type="text/plain")


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
    ("get_hooks", get_hooks),
    ("set_hooks", set_hooks),
    ("do_unwatch_player", do_unwatch_player),
    ("do_watch_player", do_watch_player),
    ("public_info", public_info),
    ("set_camera_config", set_camera_config),
    ("get_camera_config", get_camera_config),
    ("set_votekick_autotoggle_config", set_votekick_autotoggle_config),
    ("get_votekick_autotoggle_config", get_votekick_autotoggle_config),
    ("set_name", set_name),
    ("run_raw_command", run_raw_command),
]

logger.info("Initializing endpoint")

try:
    # Dynamically register all the methods from ServerCtl
    for name, func in inspect.getmembers(ctl):
        if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
            continue

        require_perms = name not in MOD_ALLOWED_CMDS

        commands.append((name, wrap_method(func, inspect.signature(func).parameters, name, require_perms=require_perms)))
    logger.info("Done Initializing endpoint")
except:
    logger.exception("Failed to initialized endpoints - Most likely bad configuration")
    raise

# Warm the cache as fetching steam profile 1 by 1 takes a while
if not os.getenv("DJANGO_DEBUG", None):
    try:
        logger.warning("Warming up the cache this may take minutes")
        ctl.get_players()
        logger.warning("Cache warm up done")
    except:
        logger.exception("Failed to warm the cache")
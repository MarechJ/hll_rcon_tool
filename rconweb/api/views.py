import inspect
import logging
import os
import traceback
from functools import wraps
from subprocess import PIPE, run
from typing import Callable, List

import pydantic
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from rcon.broadcast import get_votes_status
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.commands import CommandFailedError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.gtx import GTXFtp
from rcon.player_history import add_player_to_blacklist, remove_player_from_blacklist
from rcon.rcon import Rcon
from rcon.settings import SERVER_INFO
from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.user_config.camera import CameraNotificationUserConfig
from rcon.user_config.standard_messages import (
    StandardBroadcastMessagesUserConfig,
    StandardPunishmentMessagesUserConfig,
    StandardWelcomeMessagesUserConfig,
    get_all_message_types,
)
from rcon.user_config.utils import InvalidConfigurationError
from rcon.user_config.webhooks import (
    CameraWebhooksUserConfig,
    WatchlistWebhooksUserConfig,
    get_all_hook_types,
)
from rcon.utils import LONG_HUMAN_MAP_NAMES, MapsHistory, map_name
from rcon.watchlist import PlayerWatch
from rcon.workers import temporary_broadcast, temporary_welcome

from .audit_log import auto_record_audit, record_audit
from .auth import api_response, login_required
from .multi_servers import forward_command, forward_request
from .utils import _get_data

logger = logging.getLogger("rconweb")
ctl = Rcon(SERVER_INFO)


def _validate_user_config(
    model: AutoBroadcastUserConfig | CameraNotificationUserConfig,
    data: QueryDict,
    command_name: str,
    dry_run=True,
):
    error_msg = None
    try:
        model.save_to_db(values=data, dry_run=dry_run)  # type: ignore
    except pydantic.ValidationError as e:
        error_msg = str(e)
        # error_msg = e.json()
        logger.warning(error_msg)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=data
        )
    except InvalidConfigurationError as e:
        error_msg = str(e)
        logger.warning(error_msg)
        # logger.error(e)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=data
        )
    except Exception as e:
        error_msg = str(e)
        logger.exception(e)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=data
        )


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


# TODO: this is not an exposed endpoint
@csrf_exempt
@login_required()
@record_audit
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
    return api_response(
        failed=failed, error=error, result=None, command="set_server_name"
    )


# TODO: this is not an exposed endpoint
@csrf_exempt
@login_required()
@record_audit
def set_temp_broadcast(request):
    return set_temp_msg(request, temporary_broadcast, "set_temp_broadcast")


# TODO: this is not an exposed endpoint
@csrf_exempt
@login_required()
@record_audit
def set_temp_welcome(request):
    return set_temp_msg(request, temporary_welcome, "set_temp_welcome")


@csrf_exempt
def get_version(request):
    res = run(["git", "describe", "--tags"], stdout=PIPE, stderr=PIPE)
    return api_response(res.stdout.decode(), failed=False, command="get_version")


@csrf_exempt
def public_info(request):
    gamestate = ctl.get_gamestate()
    curr_players, max_players = tuple(map(int, ctl.get_slots().split("/")))
    try:
        current_map_start = MapsHistory(max_len=1)[0]["start"]
    except IndexError:
        logger.error("Can't get current map time, map_recorder is probably offline")
        current_map_start = None

    def explode_map_info(game_map: str, start) -> dict:
        return dict(
            just_name=map_name(game_map),
            human_name=LONG_HUMAN_MAP_NAMES.get(game_map, game_map),
            name=game_map,
            start=start,
        )

    return api_response(
        result=dict(
            current_map=explode_map_info(gamestate["current_map"], current_map_start),
            next_map=explode_map_info(gamestate["next_map"], None),
            player_count=curr_players,
            max_player_count=max_players,
            players=dict(
                allied=gamestate["num_allied_players"],
                axis=gamestate["num_axis_players"],
            ),
            score=dict(allied=gamestate["allied_score"], axis=gamestate["axis_score"]),
            # TODO: fix key
            raw_time_remaining=gamestate["raw_time_remaining"],
            vote_status=get_votes_status(none_on_fail=True),
            name=ctl.get_name(),
            short_name=os.getenv("SERVER_SHORT_NAME", "HLL RCON"),
            public_stats_port=os.getenv("PUBLIC_STATS_PORT", "Not defined"),
            public_stats_port_https=os.getenv("PUBLIC_STATS_PORT_HTTPS", "Not defined"),
        ),
        failed=False,
        command="public_info",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_discord_webhooks", raise_exception=True)
def get_all_discord_webhooks(request):
    command_name = "get_all_discord_webhooks"

    error_msg = None
    try:
        hooks = get_all_hook_types(as_dict=True)
        return api_response(result=hooks, command=command_name, failed=False)
    except:
        return api_response(command=command_name, error=error_msg)


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_watchlist_discord_webhooks", raise_exception=True)
def get_watchlist_discord_webhooks(request):
    command_name = "get_watchlist_discord_webhooks"

    try:
        config = WatchlistWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_watchlist_discord_webhooks", raise_exception=True)
def validate_watchlist_discord_webhooks(request):
    command_name = "validate_watchlist_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        WatchlistWebhooksUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_watchlist_discord_webhooks", raise_exception=True)
def set_watchlist_discord_webhooks(request):
    command_name = "set_watchlist_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        WatchlistWebhooksUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_camera_discord_webhooks", raise_exception=True)
def get_camera_discord_webhooks(request):
    command_name = "get_camera_discord_webhooks"

    try:
        config = CameraWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_camera_discord_webhooks", raise_exception=True)
def validate_camera_discord_webhooks(request):
    command_name = "validate_camera_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        CameraWebhooksUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_camera_discord_webhooks", raise_exception=True)
def set_camera_discord_webhooks(request):
    command_name = "set_camera_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        CameraWebhooksUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_camera_config", raise_exception=True)
def get_camera_config(request):
    command_name = "get_camera_config"

    try:
        config = CameraNotificationUserConfig()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.can_change_camera_config", raise_exception=True)
def validate_camera_config(request):
    command_name = "validate_camera_config"
    data = _get_data(request)

    response = _validate_user_config(
        CameraNotificationUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_camera_config", raise_exception=True)
@record_audit
def set_camera_config(request):
    command_name = "set_camera_config"
    data = _get_data(request)

    response = _validate_user_config(
        CameraNotificationUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_votekick_autotoggle_config", raise_exception=True)
def get_votekick_autotoggle_config(request):
    command_name = "get_votekick_autotoggle_config"

    try:
        config = AutoVoteKickUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO different permission?
@permission_required("api.can_change_votekick_autotoggle_config", raise_exception=True)
def validate_votekick_autotoggle_config(request):
    command_name = "validate_votekick_autotoggle_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoVoteKickUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_votekick_autotoggle_config", raise_exception=True)
@record_audit
def set_votekick_autotoggle_config(request):
    command_name = "set_votekick_autotoggle_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoVoteKickUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
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
                by=request.user.username,
                player_name=data.get("player_name"),
                steam_id_64=data.get("steam_id_64"),
            )
            # watch(self, reason: str, by: str, player_name: str = "")
            result = watcher.watch(
                reason=params["reason"],
                by=params["by"],
                player_name=params["player_name"],
            )
            audit("do_watch_player", request, params)
        else:
            result = watcher.unwatch()
            audit(
                "do_unwatch_player",
                request,
                dict(
                    player_name=data.get("player_name"), steam_id_64=data["steam_id_64"]
                ),
            )
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
@permission_required("api.can_add_player_watch", raise_exception=True)
@record_audit
def do_watch_player(request):
    return _do_watch(request, add=True)


@csrf_exempt
@login_required()
@permission_required("api.can_remove_player_watch", raise_exception=True)
@record_audit
def do_unwatch_player(request):
    return _do_watch(request, add=False)


@csrf_exempt
@login_required()
@permission_required("api.can_clear_crcon_cache", raise_exception=True)
@record_audit
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
@login_required()
@permission_required("api.can_view_auto_broadcast_config", raise_exception=True)
def get_auto_broadcasts_config(request):
    command_name = "get_auto_broadcasts_config"

    try:
        config = AutoBroadcastUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permissions?
@permission_required("api.can_change_auto_broadcast_config", raise_exception=True)
def validate_auto_broadcasts_config(request):
    command_name = "validate_auto_broadcasts_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoBroadcastUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_auto_broadcast_config", raise_exception=True)
@record_audit
def set_auto_broadcasts_config(request):
    command_name = "set_auto_broadcasts_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoBroadcastUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_standard_welcome_messages", raise_exception=True)
def get_standard_welcome_messages(request):
    command_name = "get_standard_welcome_messages"

    try:
        config = StandardWelcomeMessagesUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_welcome_messages", raise_exception=True)
def validate_standard_welcome_messages(request):
    command_name = "validate_standard_welcome_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardWelcomeMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_welcome_messages", raise_exception=True)
def set_standard_welcome_messages(request):
    command_name = "set_standard_welcome_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardWelcomeMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_standard_broadcast_messages", raise_exception=True)
def get_standard_broadcast_messages(request):
    command_name = "get_standard_broadcast_messages"

    try:
        config = StandardBroadcastMessagesUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_broadcast_messages", raise_exception=True)
def validate_standard_broadcast_messages(request):
    command_name = "validate_standard_broadcast_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardBroadcastMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_broadcast_messages", raise_exception=True)
def set_standard_broadcast_messages(request):
    command_name = "set_standard_broadcast_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardBroadcastMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_standard_punishment_messages", raise_exception=True)
def get_standard_punishments_messages(request):
    command_name = "get_standard_punishments_messages"

    try:
        config = StandardPunishmentMessagesUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required(
    "api.can_change_standard_punishment_messages", raise_exception=True
)
def validate_standard_punishments_messages(request):
    command_name = "validate_standard_punishments_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardPunishmentMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required(
    "api.can_change_standard_punishment_messages", raise_exception=True
)
def set_standard_punishments_messages(request):
    command_name = "set_standard_punishments_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardPunishmentMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
# TODO: login required?
@permission_required("api.can_view_shared_standard_messages", raise_exception=True)
def get_all_standard_messages(request) -> JsonResponse:
    command_name = "get_standard_messages"

    error_msg = None
    try:
        messages = get_all_message_types(as_dict=True)
        return api_response(result=messages, command=command_name, failed=False)
    except:
        return api_response(command=command_name, error=error_msg)


@csrf_exempt
@login_required()
@permission_required("api.can_blacklist_players", raise_exception=True)
@record_audit
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
@permission_required("api.can_unblacklist_players", raise_exception=True)
@record_audit
def unblacklist_player(request):
    data = _get_data(request)
    res = {}

    potential_failed_unbans: List[str] = []
    try:
        remove_player_from_blacklist(data["steam_id_64"])
        audit("unblacklist", request, data)
        if get_config()["BANS"]["unblacklist_does_unban"]:
            # also remove bans
            potential_failed_unbans = ctl.do_unban(data["steam_id_64"])
            if get_config()["MULTI_SERVERS"]["broadcast_unbans"]:
                forward_command(
                    "/api/do_unban",
                    json=data,
                    sessionid=request.COOKIES.get("sessionid"),
                )

        failed = False

        if potential_failed_unbans:
            raise CommandFailedError(", ".join(potential_failed_unbans))
    except:
        logger.exception("Unable to unblacklist player")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "unblacklist_player",
            "arguments": data,
            "failed": failed,
            "error": ", ".join(potential_failed_unbans),
        }
    )


# TODO: this seems redundant with do_unban in RecordedRcon?
@csrf_exempt
@login_required()
@permission_required(
    {
        "api.can_remove_temp_bans",
        "api.can_remove_perma_bans",
        "api.can_unblacklist_players",
    },
    raise_exception=True,
)
@record_audit
def unban(request):
    data = _get_data(request)
    res = {}
    results = None

    potential_failed_unbans: List[str] = []
    try:
        # also remove bans
        potential_failed_unbans = ctl.do_unban(data["steam_id_64"])
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

        if potential_failed_unbans:
            raise CommandFailedError(", ".join(potential_failed_unbans))

    except:
        logger.exception("Unable to unban player")
        failed = True

    return JsonResponse(
        {
            "result": res,
            "command": "unban_player",
            "arguments": data,
            "failed": failed,
            "error": ", ".join(potential_failed_unbans),
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
def expose_api_endpoint(func, command_name, permissions: list[str] | set[str] | str):
    @csrf_exempt
    @login_required()
    @auto_record_audit(command_name)
    @permission_required(permissions, raise_exception=True)
    @wraps(func)
    def wrapper(request):
        logger = logging.getLogger("rconweb")
        parameters = inspect.signature(func).parameters
        command_name = func.__name__
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
@permission_required("api.can_view_connection_info", raise_exception=True)
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
@login_required()
@permission_required("api.can_run_raw_commands", raise_exception=True)
def run_raw_command(request):
    data = _get_data(request)
    command = data.get("command")
    if not command:
        res = 'Parameter "command" must not be none'
    else:
        try:
            res = ctl._request(command, can_fail=True, log_info=True)
        except CommandFailedError:
            res = "Command returned FAIL"
        except:
            logging.exception("Internal error when executing raw command")
            res = "Internal error!\n\n" + traceback.format_exc()
    return HttpResponse(res, content_type="text/plain")


ENDPOINT_PERMISSIONS: dict[Callable, list[str] | set[str] | str] = {
    ctl.do_add_admin: "api.can_add_admin_roles",
    ctl.do_add_map_to_rotation: "api.can_add_map_to_rotation",
    ctl.do_add_maps_to_rotation: "api.can_add_maps_to_rotation",
    ctl.do_add_vip: "api.can_add_vip",
    ctl.do_ban_profanities: "api.can_ban_profanities",
    ctl.do_kick: "api.can_kick_players",
    ctl.do_message_player: "api.can_message_players",
    ctl.do_perma_ban: {
        "api.can_perma_ban_players",
        "api.can_blacklist_players",
    },
    ctl.do_punish: "api.can_punish_players",
    ctl.do_remove_admin: "api.can_remove_admin_roles",
    ctl.do_remove_all_vips: "api.can_remove_all_vips",
    ctl.do_remove_map_from_rotation: "api.can_remove_map_from_rotation",
    ctl.do_remove_maps_from_rotation: "api.can_remove_maps_from_rotation",
    ctl.do_remove_perma_ban: "api.can_remove_perma_bans",
    ctl.do_remove_temp_ban: "api.can_remove_temp_bans",
    ctl.do_remove_vip: "api.can_remove_vip",
    ctl.do_reset_votekick_threshold: "api.can_reset_votekick_threshold",
    ctl.do_save_setting: {
        "api.can_change_team_switch_cooldown",
        "api.can_change_autobalance_threshold",
        "api.can_change_autobalance_enabled",
        "api.can_change_idle_autokick_time",
        "api.can_change_max_ping_autokick",
        "api.can_change_queue_length",
        "api.can_change_vip_slots",
        "api.can_change_votekick_enabled",
        "api.can_change_votekick_threshold",
    },
    ctl.do_switch_player_now: "api.can_switch_players_immediately",
    ctl.do_switch_player_on_death: "api.can_switch_players_on_death",
    ctl.do_temp_ban: "api.can_temp_ban_players",
    ctl.do_unban_profanities: "api.can_unban_profanities",
    ctl.do_unban: {
        "api.can_view_temp_bans",
        "api.can_view_perma_bans",
        "api.can_remove_temp_bans",
        "api.can_remove_perma_bans",
    },
    ctl.get_admin_groups: "api.can_view_admin_groups",
    ctl.get_admin_ids: "api.can_view_admin_ids",
    ctl.get_autobalance_enabled: "api.can_view_autobalance_enabled",
    ctl.get_autobalance_threshold: "api.can_view_autobalance_threshold",
    ctl.get_ban: "api.can_view_player_bans",
    ctl.get_bans: {"api.can_view_temp_bans", "api.can_view_perma_bans"},
    ctl.get_broadcast_message: "api.can_view_broadcast_message",
    ctl.get_current_map_sequence: "api.can_view_current_map_sequence",
    ctl.get_detailed_player_info: "api.can_view_detailed_player_info",
    ctl.get_gamestate: "api.can_view_gamestate",
    ctl.get_idle_autokick_time: "api.can_view_idle_autokick_time",
    ctl.get_logs: "api.can_view_game_logs",
    ctl.get_map_rotation: "api.can_view_map_rotation",
    ctl.get_map_shuffle_enabled: "api.can_view_map_shuffle_enabled",
    ctl.get_map: "api.can_view_current_map",
    ctl.get_maps: "api.can_view_all_maps",
    ctl.get_max_ping_autokick: "api.can_view_max_ping_autokick",
    ctl.get_name: "api.can_view_server_name",
    ctl.get_next_map: "api.can_view_next_map",
    ctl.get_online_console_admins: "api.can_view_online_console_admins",
    ctl.get_perma_bans: "api.can_view_perma_bans",
    ctl.get_player_info: "api.can_view_player_info",
    ctl.get_playerids: "api.can_view_playerids",
    ctl.get_players_fast: "api.can_view_players",
    ctl.get_players: "api.can_view_get_players",
    ctl.get_profanities: "api.can_view_profanities",
    ctl.get_queue_length: "api.can_view_queue_length",
    ctl.get_round_time_remaining: "api.can_view_round_time_remaining",
    ctl.get_server_settings: {
        "api.can_view_team_switch_cooldown",
        "api.can_view_autobalance_threshold",
        "api.can_view_autobalance_enabled",
        "api.can_view_idle_autokick_time",
        "api.can_view_max_ping_autokick",
        "api.can_view_queue_length",
        "api.can_view_vip_slots",
        "api.can_view_votekick_enabled",
        "api.can_view_votekick_threshold",
    },
    ctl.get_slots: "api.can_view_player_slots",
    ctl.get_status: "api.can_view_get_status",
    ctl.get_structured_logs: "api.can_view_structured_logs",
    ctl.get_team_objective_scores: "api.can_view_team_objective_scores",
    ctl.get_team_switch_cooldown: "api.can_view_team_switch_cooldown",
    ctl.get_detailed_players: "api.can_view_detailed_players",
    ctl.get_team_view: "api.can_view_team_view",
    ctl.get_temp_bans: "api.can_view_temp_bans",
    ctl.get_timed_logs: "api.can_view_timed_logs",
    ctl.get_vip_ids: "api.can_view_vip_ids",
    ctl.get_vip_slots_num: "api.can_view_vip_slots",
    ctl.get_vips_count: "api.can_view_vip_count",
    ctl.get_votekick_enabled: "api.can_view_votekick_enabled",
    ctl.get_votekick_threshold: "api.can_view_votekick_threshold",
    ctl.get_welcome_message: "api.can_view_welcome_message",
    ctl.set_autobalance_enabled: "api.can_change_autobalance_enabled",
    ctl.set_autobalance_threshold: "api.can_change_autobalance_threshold",
    ctl.set_broadcast: "api.can_change_broadcast_message",
    ctl.set_idle_autokick_time: "api.can_change_idle_autokick_time",
    ctl.set_map_shuffle_enabled: "api.can_change_map_shuffle_enabled",
    ctl.set_map: {
        "api.can_change_current_map",
        "api.can_add_map_to_rotation",
        "api.can_remove_map_from_rotation",
    },
    ctl.set_maprotation: {
        "api.can_add_map_to_rotation",
        "api.can_remove_map_from_rotation",
        "api.can_view_map_rotation",
    },
    ctl.set_max_ping_autokick: "api.can_change_max_ping_autokick",
    ctl.set_profanities: {
        "api.can_view_profanities",
        "api.can_ban_profanities",
        "api.can_unban_profanities",
    },
    ctl.set_queue_length: "api.can_change_queue_length",
    ctl.set_team_switch_cooldown: "api.can_change_team_switch_cooldown",
    ctl.set_vip_slots_num: "api.can_change_vip_slots",
    ctl.set_votekick_enabled: "api.can_change_votekick_enabled",
    ctl.set_votekick_threshold: "api.can_change_votekick_threshold",
    ctl.set_welcome_message: "api.can_change_welcome_message",
}

PREFIXES_TO_EXPOSE = ["get_", "set_", "do_"]

commands = [
    ("blacklist_player", blacklist_player),
    ("unblacklist_player", unblacklist_player),
    ("get_auto_broadcasts_config", get_auto_broadcasts_config),
    ("validate_auto_broadcasts_config", validate_auto_broadcasts_config),
    ("set_auto_broadcasts_config", set_auto_broadcasts_config),
    ("clear_cache", clear_cache),
    ("get_all_standard_messages", get_all_standard_messages),
    # ("set_standard_messages", set_standard_messages),
    ("get_standard_welcome_messages", get_standard_welcome_messages),
    ("validate_standard_welcome_messages", validate_standard_welcome_messages),
    ("set_standard_welcome_messages", set_standard_welcome_messages),
    ("get_standard_broadcast_messages", get_standard_broadcast_messages),
    ("validate_standard_broadcast_messages", validate_standard_broadcast_messages),
    ("set_standard_broadcast_messages", set_standard_broadcast_messages),
    ("get_standard_punishments_messages", get_standard_punishments_messages),
    ("validate_standard_punishments_messages", validate_standard_punishments_messages),
    ("set_standard_punishments_messages", set_standard_punishments_messages),
    ("get_version", get_version),
    ("get_connection_info", get_connection_info),
    ("unban", unban),
    ("get_all_discord_webhooks", get_all_discord_webhooks),
    ("get_camera_discord_webhooks", get_camera_discord_webhooks),
    ("validate_camera_discord_webhooks", validate_camera_discord_webhooks),
    ("set_camera_discord_webhooks", set_camera_discord_webhooks),
    ("get_watchlist_discord_webhooks", get_watchlist_discord_webhooks),
    ("validate_watchlist_discord_webhooks", validate_watchlist_discord_webhooks),
    ("set_watchlist_discord_webhooks", set_watchlist_discord_webhooks),
    ("do_unwatch_player", do_unwatch_player),
    ("do_watch_player", do_watch_player),
    ("public_info", public_info),
    ("set_camera_config", set_camera_config),
    ("validate_camera_config", validate_camera_config),
    ("get_camera_config", get_camera_config),
    ("get_votekick_autotoggle_config", get_votekick_autotoggle_config),
    ("validate_votekick_autotoggle_config", validate_votekick_autotoggle_config),
    ("set_votekick_autotoggle_config", set_votekick_autotoggle_config),
    ("set_name", set_name),
    ("run_raw_command", run_raw_command),
]

logger.info("Initializing endpoint")

try:
    # Dynamically register all the methods from ServerCtl
    for name, func in inspect.getmembers(ctl):
        if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
            continue

        commands.append(
            (name, expose_api_endpoint(func, name, ENDPOINT_PERMISSIONS[func])),
        )
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

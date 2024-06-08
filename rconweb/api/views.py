import inspect
import logging
import os
import sys
import traceback
from functools import wraps
from subprocess import PIPE, run
from typing import Any, Callable

import pydantic
from django.contrib.auth.decorators import permission_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)
from django.views.decorators.csrf import csrf_exempt

from discord.utils import escape_markdown
from rcon.api_commands import get_rcon_api
from rcon.commands import CommandFailedError
from rcon.discord import send_to_discord_audit
from rcon.types import (
    PublicInfoMapType,
    PublicInfoNameType,
    PublicInfoPlayerType,
    PublicInfoScoreType,
    PublicInfoType,
)
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.utils import InvalidKeysConfigurationError
from rcon.utils import MapsHistory, get_server_number
from rcon.vote_map import VoteMap
from rconweb.settings import TAG_VERSION

from .audit_log import auto_record_audit, record_audit
from .auth import AUTHORIZATION, RconJsonResponse, api_response, login_required
from .decorators import require_content_type, require_http_methods
from .multi_servers import forward_command
from .utils import _get_data

logger = logging.getLogger("rconweb")

rcon_api = get_rcon_api()


@csrf_exempt
@login_required()
@permission_required("api.can_restart_webserver", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
def restart_gunicorn(request):
    """Restart gunicorn workers which reconnects Rcon endpoint instances"""
    exit_code = os.system(f"cat /code/rconweb/gunicorn.pid | xargs kill -HUP")
    error_msg = None
    if exit_code == 0:
        result = "Web server restarted successfully"
        failed = False
    else:
        result = "Web server failed to restart"
        failed = True
        error_msg = exit_code

    return api_response(result=result, failed=failed, error=error_msg)


def set_temp_msg(request, func, name):
    data = _get_data(request)
    failed = False
    error = None
    try:
        func(rcon_api, data["msg"], data["seconds"])
    except Exception as e:
        failed = True
        error = repr(e)

    return api_response(failed=failed, error=error, result=None, command=name)


@csrf_exempt
@require_http_methods(["GET"])
def get_version(request):
    res = run(["git", "describe", "--tags"], stdout=PIPE, stderr=PIPE)
    return api_response(res.stdout.decode(), failed=False, command="get_version")


@csrf_exempt
@require_http_methods(["GET"])
def get_public_info(request):
    try:
        current_map_start = MapsHistory(max_len=1)[0]["start"]
    except IndexError:
        logger.error("Can't get current map time, map_recorder is probably offline")
        current_map_start = None

    config = RconServerSettingsUserConfig.load_from_db()
    gamestate = rcon_api.get_gamestate()
    slots = rcon_api.get_slots()
    current_players = slots["current_players"]
    max_players = slots["max_players"]

    current_map: PublicInfoMapType = {
        "map": gamestate["current_map"],
        "start": current_map_start,
    }

    next_map: PublicInfoMapType = {
        "map": gamestate["next_map"],
        "start": None,
    }

    score: PublicInfoScoreType = {
        "allied": gamestate["allied_score"],
        "axis": gamestate["axis_score"],
    }
    players: PublicInfoPlayerType = {
        "allied": gamestate["num_allied_players"],
        "axis": gamestate["num_axis_players"],
    }
    vote_status = VoteMap().get_vote_overview()

    public_stats_port = os.getenv("PUBLIC_STATS_PORT", None)
    public_stats_port_https = os.getenv("PUBLIC_STATS_PORT_HTTPS", None)
    name: PublicInfoNameType = {
        "name": rcon_api.get_name(),
        "short_name": config.short_name,
        "public_stats_port": int(public_stats_port) if public_stats_port else None,
        "public_stats_port_https": (
            int(public_stats_port_https) if public_stats_port_https else None
        ),
    }

    res: PublicInfoType = {
        "current_map": current_map,
        "next_map": next_map,
        "player_count": current_players,
        "max_player_count": max_players,
        "player_count_by_team": players,
        "score": score,
        "time_remaining": gamestate["time_remaining"].total_seconds(),
        "vote_status": vote_status,
        "name": name,
    }

    return api_response(
        result=res,
        failed=False,
        command="get_public_info",
    )


def audit(func_name, request, arguments):
    # A few get_ methods can be called w/ POST but don't modify anything
    # so filtering like this should work since this is only for the RconAPI exposed
    # endpoints, manually defined endpoints use the @record_audit endpoint
    dont_audit = ["get_", "validate_"]

    try:
        if any(func_name.startswith(s) for s in dont_audit):
            return
        args = dict(**arguments)
        try:
            del args["by"]
        except KeyError:
            pass
        arguments = " ".join(
            [f"{k}: `{escape_markdown(str(v))}`" for k, v in args.items()]
        )
        send_to_discord_audit(
            message=f"{arguments}",
            command_name=func_name,
            by=request.user.username,
            md_escape_message=False,
        )
    except:
        logger.exception("Can't send audit log")


# This is were all the RCON commands are turned into HTTP endpoints
def expose_api_endpoint(
    func: Callable,
    command_name: str,
    permissions: list[str] | set[str] | str,
    endpoint_allowed_http_methods: dict[Callable, list[str]],
):
    @csrf_exempt
    @login_required()
    @auto_record_audit(command_name)
    @permission_required(permissions, raise_exception=True)
    @require_http_methods(endpoint_allowed_http_methods[func])
    @wraps(func)
    def wrapper(request: HttpRequest):
        parameters = inspect.signature(func).parameters
        arguments = {}
        failure = False
        others = None
        error: str | None = None
        errors_as_json: bool = False
        res: Any = None
        data = _get_data(request)

        json_invalid_content_type_error = f"InvalidContentType: {request.method} {request.path} was called with {request.content_type}, expected one of {','.join(['application/json'])}"
        if request.method not in endpoint_allowed_http_methods[func]:
            return HttpResponseNotAllowed([request.method])
        # There's nothing in RconAPI that will accept file uploads or any other weird content types
        # but if we added that we would have to update this
        elif request.method == "POST" and request.content_type != "application/json":
            logger.info(json_invalid_content_type_error)

        # This is a total hack to avoid having to name every single parameter for
        # every single user config endpoint
        if "kwargs" in parameters.keys():
            if data.pop("errors_as_json", None):
                errors_as_json = True
            arguments = data
            arguments["by"] = request.user.username
        else:
            # Scrape out special case parameters, like the author of a request is the user name making the request
            # This does not cast argument types, so things that come in from GET parameters are all going to be strings
            # so we need to handle this properly inside methods if the types matter
            for pname, param in parameters.items():
                if pname == "by":
                    arguments[pname] = request.user.username
                elif param.default != inspect._empty:
                    arguments[pname] = data.get(pname, param.default)
                else:
                    try:
                        arguments[pname] = data[pname]
                    except KeyError:
                        logger.error(
                            f"Bad request for {request.method} {request.path} {pname=} {param=}"
                        )
                        return HttpResponseBadRequest(
                            f"Missing mandatory parameter: {pname}"
                        )

        try:
            logger.debug("%s %s", command_name, arguments)
            res = func(**arguments)

            # A few get_ methods can be called w/ POST but don't modify anything
            # so filtering like this should work since this is only for the RconAPI exposed
            # endpoints, manually defined endpoints use the @record_audit endpoint
            # also skip auditing user config endpoints, those are handled in RconAPI
            if (
                not command_name.startswith("get_")
                and not command_name.startswith("validate_")
                and not command_name.endswith("_config")
            ):
                audit(command_name, request, arguments)

        # This is a bit janky but catch any UserConfig validation errors that have bubbled up and convert
        # the error message as required
        except pydantic.ValidationError as e:
            if errors_as_json:
                error = e.json()
            else:
                error = str(e)
        except InvalidKeysConfigurationError as e:
            if errors_as_json:
                error = e.asdict()
            else:
                error = str(e)
        except CommandFailedError as e:
            failure = True
            error = e.args[0] if e.args else None

        response = RconJsonResponse(
            dict(
                result=res,
                command=command_name,
                arguments=data,
                failed=failure,
                error=error,
                forward_results=others,
                version=TAG_VERSION,
            ),
        )

        # Handle all the special cases of forwarding commands here so we don't
        # have to pass in HTTP requests, sessionids, auth headers, etc. to RconAPI
        # using forward_command and not forward_request so that the `forwarded`parameter
        # is passed to avoid infinite loops of forwarding
        config = RconServerSettingsUserConfig.load_from_db()
        if config.broadcast_unbans and func == rcon_api.unban:
            try:
                forward_command(
                    path=request.path,
                    sessionid=request.COOKIES.get("sessionid"),
                    auth_header=request.headers.get(AUTHORIZATION),
                    json=data,
                )
            except Exception as e:
                logger.error("Unexpected error while forwarding request: %s", e)
        # Handle all the other non special case forwarding
        elif data.get("forward"):
            try:
                forward_command(
                    path=request.path,
                    sessionid=request.COOKIES.get("sessionid"),
                    auth_header=request.headers.get(AUTHORIZATION),
                    json=data,
                )
            except Exception as e:
                logger.error("Unexpected error while forwarding request: %s", e)

        return response

    return wrapper


@login_required()
@permission_required("api.can_view_connection_info", raise_exception=True)
@csrf_exempt
@require_http_methods(["GET"])
def get_connection_info(request):
    config = RconServerSettingsUserConfig.load_from_db()
    return api_response(
        {
            "name": rcon_api.get_name(),
            "port": os.getenv("RCONWEB_PORT"),
            "link": str(config.server_url) if config.server_url else config.server_url,
            "server_number": int(get_server_number()),
        },
        failed=False,
        command="get_connection_info",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_run_raw_commands", raise_exception=True)
# Specifically allow GET requests because some raw commands are very simple
# and can be used with query parameters in your browser
@require_http_methods(["GET", "POST"])
@require_content_type()
def run_raw_command(request):
    data = _get_data(request)
    command = data.get("command")
    if not command:
        res = 'Parameter "command" must not be none'
    else:
        try:
            res = rcon_api._str_request(command, can_fail=True, log_info=True)
        except CommandFailedError:
            res = "Command returned FAIL"
        except:
            logging.exception("Internal error when executing raw command")
            res = "Internal error!\n\n" + traceback.format_exc()
    return HttpResponse(res, content_type="text/plain")


ENDPOINT_PERMISSIONS: dict[Callable, list[str] | set[str] | str] = {
    rcon_api.add_admin: "api.can_add_admin_roles",
    rcon_api.add_map_to_rotation: "api.can_add_map_to_rotation",
    rcon_api.add_map_to_votemap_whitelist: "api.can_add_map_to_whitelist",
    rcon_api.add_maps_to_rotation: "api.can_add_maps_to_rotation",
    rcon_api.add_maps_to_votemap_whitelist: "api.can_add_maps_to_whitelist",
    rcon_api.add_vip: "api.can_add_vip",
    rcon_api.ban_profanities: "api.can_ban_profanities",
    rcon_api.clear_cache: "api.can_clear_crcon_cache",
    rcon_api.flag_player: "api.can_flag_player",
    rcon_api.kick: "api.can_kick_players",
    rcon_api.message_player: "api.can_message_players",
    rcon_api.perma_ban: {
        "api.can_perma_ban_players",
    },
    rcon_api.punish: "api.can_punish_players",
    rcon_api.remove_admin: "api.can_remove_admin_roles",
    rcon_api.remove_all_vips: "api.can_remove_all_vips",
    rcon_api.remove_map_from_rotation: "api.can_remove_map_from_rotation",
    rcon_api.remove_map_from_votemap_whitelist: "api.can_remove_map_from_whitelist",
    rcon_api.remove_maps_from_rotation: "api.can_remove_maps_from_rotation",
    rcon_api.remove_maps_from_votemap_whitelist: "api.can_remove_maps_from_whitelist",
    rcon_api.remove_perma_ban: "api.can_remove_perma_bans",
    rcon_api.remove_temp_ban: "api.can_remove_temp_bans",
    rcon_api.remove_vip: "api.can_remove_vip",
    rcon_api.reset_map_votemap_whitelist: "api.can_reset_map_whitelist",
    rcon_api.reset_votekick_thresholds: "api.can_reset_votekick_threshold",
    rcon_api.set_votemap_whitelist: "api.can_set_map_whitelist",
    rcon_api.switch_player_now: "api.can_switch_players_immediately",
    rcon_api.switch_player_on_death: "api.can_switch_players_on_death",
    rcon_api.temp_ban: "api.can_temp_ban_players",
    rcon_api.unban_profanities: "api.can_unban_profanities",
    rcon_api.unban: {
        "api.can_remove_temp_bans",
        "api.can_remove_perma_bans",
    },
    rcon_api.unflag_player: "api.can_unflag_player",
    rcon_api.unwatch_player: "api.can_remove_player_watch",
    rcon_api.watch_player: "api.can_add_player_watch",
    rcon_api.get_admin_groups: "api.can_view_admin_groups",
    rcon_api.get_admin_ids: "api.can_view_admin_ids",
    rcon_api.get_admin_pings_discord_webhooks_config: "api.can_view_admin_pings_discord_webhooks_config",
    rcon_api.get_audit_discord_webhooks_config: "api.can_view_audit_discord_webhooks_config",
    rcon_api.get_auto_broadcasts_config: "api.can_view_auto_broadcast_config",
    rcon_api.get_auto_mod_level_config: "api.can_view_auto_mod_level_config",
    rcon_api.get_auto_mod_no_leader_config: "api.can_view_auto_mod_no_leader_config",
    rcon_api.get_auto_mod_seeding_config: "api.can_view_auto_mod_seeding_config",
    rcon_api.get_auto_mod_solo_tank_config: "api.can_view_auto_mod_solo_tank_config",
    rcon_api.get_autobalance_enabled: "api.can_view_autobalance_enabled",
    rcon_api.get_autobalance_threshold: "api.can_view_autobalance_threshold",
    rcon_api.get_ban: "api.can_view_player_bans",
    rcon_api.get_bans: {"api.can_view_temp_bans", "api.can_view_perma_bans"},
    rcon_api.get_broadcast_message: "api.can_view_broadcast_message",
    rcon_api.get_camera_discord_webhooks_config: "api.can_view_camera_discord_webhooks_config",
    rcon_api.get_camera_notification_config: "api.can_view_camera_config",
    rcon_api.get_chat_commands_config: "api.can_view_chat_commands_config",
    rcon_api.get_chat_discord_webhooks_config: "api.can_view_chat_discord_webhooks_config",
    rcon_api.get_current_map_sequence: "api.can_view_current_map_sequence",
    rcon_api.get_detailed_player_info: "api.can_view_detailed_player_info",
    rcon_api.get_detailed_players: "api.can_view_detailed_players",
    rcon_api.get_expired_vip_config: "api.get_expired_vip_config",
    rcon_api.get_gamestate: "api.can_view_gamestate",
    rcon_api.get_historical_logs: "api.can_view_historical_logs",
    rcon_api.get_idle_autokick_time: "api.can_view_idle_autokick_time",
    rcon_api.get_ingame_mods: "api.can_view_ingame_admins",
    rcon_api.get_kills_discord_webhooks_config: "api.can_view_kills_discord_webhooks_config",
    rcon_api.get_log_line_webhook_config: "api.get_log_line_webhook_config",
    rcon_api.get_logs: "api.can_view_game_logs",
    rcon_api.get_map_rotation: "api.can_view_map_rotation",
    rcon_api.get_map_shuffle_enabled: "api.can_view_map_shuffle_enabled",
    rcon_api.get_votemap_whitelist: "api.can_view_map_whitelist",
    rcon_api.get_map: "api.can_view_current_map",
    rcon_api.get_maps: "api.can_view_all_maps",
    rcon_api.get_max_ping_autokick: "api.can_view_max_ping_autokick",
    rcon_api.get_name_kick_config: "api.can_view_name_kick_config",
    rcon_api.get_name: "api.can_view_server_name",
    rcon_api.get_next_map: "api.can_view_next_map",
    rcon_api.get_online_mods: "api.can_view_online_admins",
    rcon_api.get_perma_bans: "api.can_view_perma_bans",
    rcon_api.get_player_info: "api.can_view_player_info",
    rcon_api.get_player_profile: "api.can_view_player_profile",
    rcon_api.get_playerids: "api.can_view_playerids",
    rcon_api.get_player_comments: "api.can_view_player_comments",
    rcon_api.post_player_comment: "api.can_add_player_comments",
    rcon_api.get_player_messages: "api.can_view_player_messages",
    rcon_api.get_players_history: "api.can_view_player_history",
    rcon_api.get_players: "api.can_view_get_players",
    rcon_api.get_profanities: "api.can_view_profanities",
    rcon_api.get_queue_length: "api.can_view_queue_length",
    rcon_api.get_rcon_connection_settings_config: "api.can_view_rcon_connection_settings_config",
    rcon_api.get_rcon_server_settings_config: "api.can_view_rcon_server_settings_config",
    rcon_api.get_real_vip_config: "api.can_view_real_vip_config",
    rcon_api.get_recent_logs: "api.can_view_recent_logs",
    rcon_api.get_round_time_remaining: "api.can_view_round_time_remaining",
    rcon_api.get_scorebot_config: "api.can_view_scorebot_config",
    rcon_api.get_server_name_change_config: "api.get_server_name_change_config",
    rcon_api.get_server_settings: {
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
    rcon_api.get_slots: "api.can_view_player_slots",
    rcon_api.get_standard_broadcast_messages: "api.can_view_standard_broadcast_messages",
    rcon_api.get_standard_punishments_messages: "api.can_view_standard_punishment_messages",
    rcon_api.get_standard_welcome_messages: "api.can_view_standard_welcome_messages",
    rcon_api.get_status: "api.can_view_get_status",
    rcon_api.get_steam_config: "api.can_view_steam_config",
    rcon_api.get_structured_logs: "api.can_view_structured_logs",
    rcon_api.get_team_objective_scores: "api.can_view_team_objective_scores",
    rcon_api.get_team_switch_cooldown: "api.can_view_team_switch_cooldown",
    rcon_api.get_team_view: "api.can_view_team_view",
    rcon_api.get_temp_bans: "api.can_view_temp_bans",
    rcon_api.get_tk_ban_on_connect_config: "api.can_view_tk_ban_on_connect_config",
    rcon_api.get_vac_game_bans_config: "api.can_view_vac_game_bans_config",
    rcon_api.get_vip_ids: "api.can_view_vip_ids",
    rcon_api.get_vip_slots_num: "api.can_view_vip_slots",
    rcon_api.get_vips_count: "api.can_view_vip_count",
    rcon_api.get_votekick_autotoggle_config: "api.can_view_votekick_autotoggle_config",
    rcon_api.get_votekick_enabled: "api.can_view_votekick_enabled",
    rcon_api.get_votekick_thresholds: "api.can_view_votekick_threshold",
    rcon_api.get_votemap_config: "api.can_view_votemap_config",
    rcon_api.get_votemap_status: "api.can_view_votemap_status",
    rcon_api.get_watchlist_discord_webhooks_config: "api.can_view_watchlist_discord_webhooks_config",
    rcon_api.get_welcome_message: "api.can_view_welcome_message",
    # TODO: update this name
    rcon_api.reset_votemap_state: "api.can_reset_votemap_state",
    rcon_api.set_admin_pings_discord_webhooks_config: "api.can_change_admin_pings_discord_webhooks_config",
    rcon_api.set_audit_discord_webhooks_config: "api.can_change_audit_discord_webhooks_config",
    rcon_api.set_auto_broadcasts_config: "api.can_change_auto_broadcast_config",
    rcon_api.set_auto_mod_level_config: "api.can_change_auto_mod_level_config",
    rcon_api.set_auto_mod_no_leader_config: "api.can_change_auto_mod_no_leader_config",
    rcon_api.set_auto_mod_seeding_config: "api.can_change_auto_mod_seeding_config",
    rcon_api.set_auto_mod_solo_tank_config: "api.can_change_auto_mod_solo_tank_config",
    rcon_api.set_autobalance_enabled: "api.can_change_autobalance_enabled",
    rcon_api.set_autobalance_threshold: "api.can_change_autobalance_threshold",
    rcon_api.set_broadcast: "api.can_change_broadcast_message",
    rcon_api.set_camera_discord_webhooks_config: "api.can_change_camera_discord_webhooks_config",
    rcon_api.set_camera_notification_config: "api.can_change_camera_config",
    rcon_api.set_chat_commands_config: "api.can_change_chat_commands_config",
    rcon_api.set_chat_discord_webhooks_config: "api.can_change_chat_discord_webhooks_config",
    rcon_api.set_expired_vip_config: "api.can_change_expired_vip_config",
    rcon_api.set_idle_autokick_time: "api.can_change_idle_autokick_time",
    rcon_api.set_kills_discord_webhooks_config: "api.can_change_kills_discord_webhooks_config",
    rcon_api.set_log_line_webhook_config: "api.can_change_log_line_discord_webhook_config",
    rcon_api.set_map_shuffle_enabled: "api.can_change_map_shuffle_enabled",
    rcon_api.set_map: "api.can_change_current_map",
    rcon_api.set_maprotation: {
        "api.can_add_map_to_rotation",
        "api.can_remove_map_from_rotation",
        "api.can_view_map_rotation",
    },
    rcon_api.set_max_ping_autokick: "api.can_change_max_ping_autokick",
    rcon_api.set_name_kick_config: "api.can_change_name_kick_config",
    rcon_api.set_profanities: {
        "api.can_view_profanities",
        "api.can_ban_profanities",
        "api.can_unban_profanities",
    },
    rcon_api.set_queue_length: "api.can_change_queue_length",
    rcon_api.set_rcon_connection_settings_config: "api.can_change_rcon_connection_settings_config",
    rcon_api.set_rcon_server_settings_config: "api.can_change_rcon_server_settings_config",
    rcon_api.set_real_vip_config: "api.can_change_real_vip_config",
    rcon_api.set_scorebot_config: "api.can_change_scorebot_config",
    rcon_api.set_server_name_change_config: "api.can_change_server_name_change_config",
    rcon_api.set_server_name: "api.can_change_server_name",
    rcon_api.set_standard_broadcast_messages: "api.can_change_standard_broadcast_messages",
    rcon_api.set_standard_punishments_messages: "api.can_change_standard_punishment_messages",
    rcon_api.set_standard_welcome_messages: "api.can_change_standard_welcome_messages",
    rcon_api.set_steam_config: "api.can_change_steam_config",
    rcon_api.set_team_switch_cooldown: "api.can_change_team_switch_cooldown",
    rcon_api.set_tk_ban_on_connect_config: "api.can_change_tk_ban_on_connect_config",
    rcon_api.set_vac_game_bans_config: "api.can_change_vac_game_bans_config",
    rcon_api.set_vip_slots_num: "api.can_change_vip_slots",
    rcon_api.set_votekick_autotoggle_config: "api.can_change_votekick_autotoggle_config",
    rcon_api.set_votekick_enabled: "api.can_change_votekick_enabled",
    rcon_api.set_votekick_thresholds: "api.can_change_votekick_threshold",
    rcon_api.set_votemap_config: "api.can_change_votemap_config",
    rcon_api.set_watchlist_discord_webhooks_config: "api.can_change_watchlist_discord_webhooks_config",
    rcon_api.set_welcome_message: "api.can_change_welcome_message",
    rcon_api.validate_admin_pings_discord_webhooks_config: "api.can_change_admin_pings_discord_webhooks_config",
    rcon_api.validate_audit_discord_webhooks_config: "api.can_change_audit_discord_webhooks_config",
    rcon_api.validate_auto_broadcasts_config: "api.can_change_auto_broadcast_config",
    rcon_api.validate_auto_mod_level_config: "api.can_change_auto_mod_level_config",
    rcon_api.validate_auto_mod_no_leader_config: "api.can_change_auto_mod_no_leader_config",
    rcon_api.validate_auto_mod_seeding_config: "api.can_change_auto_mod_seeding_config",
    rcon_api.validate_auto_mod_solo_tank_config: "api.can_change_auto_mod_solo_tank_config",
    rcon_api.validate_camera_discord_webhooks_config: "api.can_change_camera_discord_webhooks_config",
    rcon_api.validate_camera_notification_config: "api.can_change_camera_config",
    rcon_api.validate_chat_commands_config: "api.can_change_chat_commands_config",
    rcon_api.validate_chat_discord_webhooks_config: "api.can_change_chat_discord_webhooks_config",
    rcon_api.validate_expired_vip_config: "api.can_change_expired_vip_config",
    rcon_api.validate_kills_discord_webhooks_config: "api.can_change_kills_discord_webhooks_config",
    rcon_api.validate_log_line_webhook_config: "api.can_change_log_line_discord_webhook_config",
    rcon_api.validate_name_kick_config: "api.can_change_name_kick_config",
    rcon_api.validate_rcon_connection_settings_config: "api.can_change_rcon_connection_settings_config",
    rcon_api.validate_rcon_server_settings_config: "api.can_change_rcon_server_settings_config",
    rcon_api.validate_real_vip_config: "api.can_change_real_vip_config",
    rcon_api.validate_scorebot_config: "api.can_change_scorebot_config",
    rcon_api.validate_server_name_change_config: "api.can_change_server_name_change_config",
    rcon_api.validate_standard_broadcast_messages: "api.can_change_standard_broadcast_messages",
    rcon_api.validate_standard_punishments_messages: "api.can_change_standard_punishment_messages",
    rcon_api.validate_standard_welcome_messages: "api.can_change_standard_welcome_messages",
    rcon_api.validate_steam_config: "api.can_change_steam_config",
    rcon_api.validate_tk_ban_on_connect_config: "api.can_change_tk_ban_on_connect_config",
    rcon_api.validate_vac_game_bans_config: "api.can_change_vac_game_bans_config",
    rcon_api.validate_votekick_autotoggle_config: "api.can_change_votekick_autotoggle_config",
    rcon_api.validate_votemap_config: "api.can_change_votemap_config",
    rcon_api.validate_watchlist_discord_webhooks_config: "api.can_change_watchlist_discord_webhooks_config",
    rcon_api.get_log_stream_config: "api.can_view_log_stream_config",
    rcon_api.set_log_stream_config: "api.can_change_log_stream_config",
    rcon_api.validate_log_stream_config: "api.can_change_log_stream_config",
    rcon_api.get_date_scoreboard: "api.can_view_date_scoreboard",
    rcon_api.get_blacklists: "api.can_view_blacklists",
    rcon_api.get_blacklist: "api.can_view_blacklists",
    rcon_api.create_blacklist: "api.can_create_blacklists",
    rcon_api.edit_blacklist: "api.can_change_blacklists",
    rcon_api.delete_blacklist: "api.can_delete_blacklists",
    rcon_api.get_blacklist_records: "can_view_blacklists",
    rcon_api.add_blacklist_record: "api.can_add_blacklist_records",
    rcon_api.edit_blacklist_record: "api.can_change_blacklist_records",
    rcon_api.delete_blacklist_record: "api.can_delete_blacklist_records",
    rcon_api.unblacklist_player: {
        "api.can_delete_blacklist_records",
        "api.can_remove_temp_bans",
        "api.can_remove_perma_bans",
    },
}

PREFIXES_TO_EXPOSE = [
    "get_",
    "set_",
    "do_",
    "reset_",
    "validate_",
]

# TODO: remove deprecated endpoints
DEPRECATED_ENDPOINTS = (
    "date_scoreboard",
    "flag_player",
    "unflag_player",
    "player",
    "unban",
)

RCON_ENDPOINT_HTTP_METHODS: dict[Callable, list[str]] = {
    rcon_api.add_admin: ["POST"],
    rcon_api.add_map_to_rotation: ["POST"],
    rcon_api.add_map_to_votemap_whitelist: ["POST"],
    rcon_api.add_maps_to_rotation: ["POST"],
    rcon_api.add_maps_to_votemap_whitelist: ["POST"],
    rcon_api.add_vip: ["POST"],
    rcon_api.ban_profanities: ["POST"],
    rcon_api.clear_cache: ["POST"],
    rcon_api.flag_player: ["POST"],
    rcon_api.get_admin_groups: ["GET"],
    rcon_api.get_admin_ids: ["GET"],
    rcon_api.get_admin_pings_discord_webhooks_config: ["GET"],
    rcon_api.get_audit_discord_webhooks_config: ["GET"],
    rcon_api.get_auto_broadcasts_config: ["GET"],
    rcon_api.get_auto_mod_level_config: ["GET"],
    rcon_api.get_auto_mod_no_leader_config: ["GET"],
    rcon_api.get_auto_mod_seeding_config: ["GET"],
    rcon_api.get_auto_mod_solo_tank_config: ["GET"],
    rcon_api.get_autobalance_enabled: ["GET"],
    rcon_api.get_autobalance_threshold: ["GET"],
    rcon_api.get_ban: ["GET"],
    rcon_api.get_bans: ["GET"],
    rcon_api.get_broadcast_message: ["GET"],
    rcon_api.get_camera_discord_webhooks_config: ["GET"],
    rcon_api.get_camera_notification_config: ["GET"],
    rcon_api.get_chat_commands_config: ["GET"],
    rcon_api.get_chat_discord_webhooks_config: ["GET"],
    rcon_api.get_current_map_sequence: ["GET"],
    rcon_api.get_detailed_player_info: ["GET"],
    rcon_api.get_detailed_players: ["GET"],
    rcon_api.get_expired_vip_config: ["GET"],
    rcon_api.get_gamestate: ["GET"],
    rcon_api.get_historical_logs: ["GET", "POST"],
    rcon_api.get_idle_autokick_time: ["GET"],
    rcon_api.get_ingame_mods: ["GET"],
    rcon_api.get_kills_discord_webhooks_config: ["GET"],
    rcon_api.get_log_line_webhook_config: ["GET"],
    rcon_api.get_log_stream_config: ["GET"],
    rcon_api.get_logs: ["GET"],
    rcon_api.get_map_rotation: ["GET"],
    rcon_api.get_map_shuffle_enabled: ["GET"],
    rcon_api.get_votemap_whitelist: ["GET"],
    rcon_api.get_map: ["GET"],
    rcon_api.get_maps: ["GET"],
    rcon_api.get_max_ping_autokick: ["GET"],
    rcon_api.get_name_kick_config: ["GET"],
    rcon_api.get_name: ["GET"],
    rcon_api.get_next_map: ["GET"],
    rcon_api.get_online_mods: ["GET"],
    rcon_api.get_perma_bans: ["GET"],
    rcon_api.get_player_info: ["GET"],
    rcon_api.get_player_profile: ["GET"],
    rcon_api.get_playerids: ["GET"],
    rcon_api.get_player_comments: ["GET"],
    rcon_api.post_player_comment: ["POST"],
    rcon_api.get_player_messages: ["GET"],
    rcon_api.get_players_history: ["GET", "POST"],
    rcon_api.get_players: ["GET"],
    rcon_api.get_profanities: ["GET"],
    rcon_api.get_queue_length: ["GET"],
    rcon_api.get_rcon_connection_settings_config: ["GET"],
    rcon_api.get_rcon_server_settings_config: ["GET"],
    rcon_api.get_real_vip_config: ["GET"],
    rcon_api.get_recent_logs: ["GET", "POST"],
    rcon_api.get_round_time_remaining: ["GET"],
    rcon_api.get_scorebot_config: ["GET"],
    rcon_api.get_server_name_change_config: ["GET"],
    rcon_api.get_server_settings: ["GET"],
    rcon_api.get_slots: ["GET"],
    rcon_api.get_standard_broadcast_messages: ["GET"],
    rcon_api.get_standard_punishments_messages: ["GET"],
    rcon_api.get_standard_welcome_messages: ["GET"],
    rcon_api.get_status: ["GET"],
    rcon_api.get_steam_config: ["GET"],
    rcon_api.get_structured_logs: ["GET"],
    rcon_api.get_team_objective_scores: ["GET"],
    rcon_api.get_team_switch_cooldown: ["GET"],
    rcon_api.get_team_view: ["GET"],
    rcon_api.get_temp_bans: ["GET"],
    rcon_api.get_tk_ban_on_connect_config: ["GET"],
    rcon_api.get_vac_game_bans_config: ["GET"],
    rcon_api.get_vip_ids: ["GET"],
    rcon_api.get_vip_slots_num: ["GET"],
    rcon_api.get_vips_count: ["GET"],
    rcon_api.get_votekick_autotoggle_config: ["GET"],
    rcon_api.get_votekick_enabled: ["GET"],
    rcon_api.get_votekick_thresholds: ["GET"],
    rcon_api.get_votemap_config: ["GET"],
    rcon_api.get_votemap_status: ["GET"],
    rcon_api.get_watchlist_discord_webhooks_config: ["GET"],
    rcon_api.get_welcome_message: ["GET"],
    rcon_api.kick: ["POST"],
    rcon_api.message_player: ["POST"],
    rcon_api.perma_ban: ["POST"],
    rcon_api.punish: ["POST"],
    rcon_api.remove_admin: ["POST"],
    rcon_api.remove_all_vips: ["POST"],
    rcon_api.remove_map_from_rotation: ["POST"],
    rcon_api.remove_map_from_votemap_whitelist: ["POST"],
    rcon_api.remove_maps_from_rotation: ["POST"],
    rcon_api.remove_maps_from_votemap_whitelist: ["POST"],
    rcon_api.remove_perma_ban: ["POST"],
    rcon_api.remove_temp_ban: ["POST"],
    rcon_api.remove_vip: ["POST"],
    rcon_api.reset_map_votemap_whitelist: ["POST"],
    rcon_api.reset_votekick_thresholds: ["POST"],
    rcon_api.reset_votemap_state: ["POST"],
    rcon_api.set_admin_pings_discord_webhooks_config: ["POST"],
    rcon_api.set_audit_discord_webhooks_config: ["POST"],
    rcon_api.set_auto_broadcasts_config: ["POST"],
    rcon_api.set_auto_mod_level_config: ["POST"],
    rcon_api.set_auto_mod_no_leader_config: ["POST"],
    rcon_api.set_auto_mod_seeding_config: ["POST"],
    rcon_api.set_auto_mod_solo_tank_config: ["POST"],
    rcon_api.set_autobalance_enabled: ["POST"],
    rcon_api.set_autobalance_threshold: ["POST"],
    rcon_api.set_broadcast: ["POST"],
    rcon_api.set_camera_discord_webhooks_config: ["POST"],
    rcon_api.set_camera_notification_config: ["POST"],
    rcon_api.set_chat_commands_config: ["POST"],
    rcon_api.set_chat_discord_webhooks_config: ["POST"],
    rcon_api.set_expired_vip_config: ["POST"],
    rcon_api.set_idle_autokick_time: ["POST"],
    rcon_api.set_kills_discord_webhooks_config: ["POST"],
    rcon_api.set_log_line_webhook_config: ["POST"],
    rcon_api.set_log_stream_config: ["POST"],
    rcon_api.set_map_shuffle_enabled: ["POST"],
    rcon_api.set_votemap_whitelist: ["POST"],
    rcon_api.set_map: ["POST"],
    rcon_api.set_maprotation: ["POST"],
    rcon_api.set_max_ping_autokick: ["POST"],
    rcon_api.set_name_kick_config: ["POST"],
    rcon_api.set_profanities: ["POST"],
    rcon_api.set_queue_length: ["POST"],
    rcon_api.set_rcon_connection_settings_config: ["POST"],
    rcon_api.set_rcon_server_settings_config: ["POST"],
    rcon_api.set_real_vip_config: ["POST"],
    rcon_api.set_scorebot_config: ["POST"],
    rcon_api.set_server_name_change_config: ["POST"],
    rcon_api.set_server_name: ["POST"],
    rcon_api.set_standard_broadcast_messages: ["POST"],
    rcon_api.set_standard_punishments_messages: ["POST"],
    rcon_api.set_standard_welcome_messages: ["POST"],
    rcon_api.set_steam_config: ["POST"],
    rcon_api.set_team_switch_cooldown: ["POST"],
    rcon_api.set_tk_ban_on_connect_config: ["POST"],
    rcon_api.set_vac_game_bans_config: ["POST"],
    rcon_api.set_vip_slots_num: ["POST"],
    rcon_api.set_votekick_autotoggle_config: ["POST"],
    rcon_api.set_votekick_enabled: ["POST"],
    rcon_api.set_votekick_thresholds: ["POST"],
    rcon_api.set_votemap_config: ["POST"],
    rcon_api.set_watchlist_discord_webhooks_config: ["POST"],
    rcon_api.set_welcome_message: ["POST"],
    rcon_api.switch_player_now: ["POST"],
    rcon_api.switch_player_on_death: ["POST"],
    rcon_api.temp_ban: ["POST"],
    rcon_api.unban_profanities: ["POST"],
    rcon_api.unban: ["POST"],
    rcon_api.unflag_player: ["POST"],
    rcon_api.unwatch_player: ["POST"],
    rcon_api.validate_admin_pings_discord_webhooks_config: ["POST"],
    rcon_api.validate_audit_discord_webhooks_config: ["POST"],
    rcon_api.validate_auto_broadcasts_config: ["POST"],
    rcon_api.validate_auto_mod_level_config: ["POST"],
    rcon_api.validate_auto_mod_no_leader_config: ["POST"],
    rcon_api.validate_auto_mod_seeding_config: ["POST"],
    rcon_api.validate_auto_mod_solo_tank_config: ["POST"],
    rcon_api.validate_camera_discord_webhooks_config: ["POST"],
    rcon_api.validate_camera_notification_config: ["POST"],
    rcon_api.validate_chat_commands_config: ["POST"],
    rcon_api.validate_chat_discord_webhooks_config: ["POST"],
    rcon_api.validate_expired_vip_config: ["POST"],
    rcon_api.validate_kills_discord_webhooks_config: ["POST"],
    rcon_api.validate_log_line_webhook_config: ["POST"],
    rcon_api.validate_log_stream_config: ["POST"],
    rcon_api.validate_name_kick_config: ["POST"],
    rcon_api.validate_rcon_connection_settings_config: ["POST"],
    rcon_api.validate_rcon_server_settings_config: ["POST"],
    rcon_api.validate_real_vip_config: ["POST"],
    rcon_api.validate_scorebot_config: ["POST"],
    rcon_api.validate_server_name_change_config: ["POST"],
    rcon_api.validate_standard_broadcast_messages: ["POST"],
    rcon_api.validate_standard_punishments_messages: ["POST"],
    rcon_api.validate_standard_welcome_messages: ["POST"],
    rcon_api.validate_steam_config: ["POST"],
    rcon_api.validate_tk_ban_on_connect_config: ["POST"],
    rcon_api.validate_vac_game_bans_config: ["POST"],
    rcon_api.validate_votekick_autotoggle_config: ["POST"],
    rcon_api.validate_votemap_config: ["POST"],
    rcon_api.validate_watchlist_discord_webhooks_config: ["POST"],
    rcon_api.watch_player: ["POST"],
    rcon_api.get_date_scoreboard: ["GET"],
    rcon_api.get_blacklists: ["GET"],
    rcon_api.get_blacklist: ["GET"],
    rcon_api.create_blacklist: ["POST"],
    rcon_api.edit_blacklist: ["POST"],
    rcon_api.delete_blacklist: ["POST"],
    rcon_api.get_blacklist_records: ["GET"],
    rcon_api.add_blacklist_record: ["POST"],
    rcon_api.edit_blacklist_record: ["POST"],
    rcon_api.delete_blacklist_record: ["POST"],
    rcon_api.unblacklist_player: ["POST"],
}

# Check to make sure that ENDPOINT_HTTP_METHODS and ENDPOINT_PERMISSIONS have the same endpoints
MISSING_ENDPOINTS = set(
    k for k in RCON_ENDPOINT_HTTP_METHODS.keys()
).symmetric_difference(set(k for k in ENDPOINT_PERMISSIONS))

if len(MISSING_ENDPOINTS) > 0:
    logger.error(f"{MISSING_ENDPOINTS=}")
    sys.exit(1)

# Some get_ and deprecated endpoints accept POST requests
# TODO: remove deprecated endpoints
ALLOWED_METHODS_SPECIAL_CASES: dict[Callable, list[str]] = {
    rcon_api.get_players_history: ["GET", "POST"],
    rcon_api.get_historical_logs: ["GET", "POST"],
    rcon_api.get_recent_logs: ["GET", "POST"],
    rcon_api.unflag_player: ["POST"],
    rcon_api.clear_cache: ["POST"],
    rcon_api.unban: ["POST"],
}

commands = [
    ("get_version", get_version),
    ("get_connection_info", get_connection_info),
    ("get_public_info", get_public_info),
    ("run_raw_command", run_raw_command),
]

if not os.getenv("HLL_MAINTENANCE_CONTAINER"):
    logger.info("Initializing endpoints")

    try:
        # Dynamically register all the methods from ServerCtl
        # TODO: remove deprecated endpoints check once endpoints are removed
        for func in ENDPOINT_PERMISSIONS.keys():
            name = func.__name__
            commands.append(
                (
                    name,
                    expose_api_endpoint(
                        func=func,
                        command_name=name,
                        permissions=ENDPOINT_PERMISSIONS[func],
                        endpoint_allowed_http_methods=RCON_ENDPOINT_HTTP_METHODS,
                    ),
                ),
            )
        logger.info("Done Initializing endpoints")
    except:
        logger.exception(
            "Failed to initialized endpoints - Most likely bad configuration"
        )
        raise

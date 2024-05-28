from inspect import _empty, getdoc, signature, unwrap
from logging import getLogger
from typing import Callable

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import (
    audit_log,
    auth,
    auto_settings,
    multi_servers,
    scoreboards,
    services,
    user_settings,
    views,
    vips,
)
from .auth import api_response
from .decorators import ENDPOINT_HTTP_METHODS

logger = getLogger("rconweb")


def _get_empty(value):
    """Return None for inspect._empty values or the value as a string"""
    if value is _empty:
        return None
    else:
        return str(value)


@csrf_exempt
def get_api_documentation(request):
    """Auto-generate minimal API documentation through introspection"""
    from rcon.api_commands import RconAPI

    api_docs = []
    for name, func in endpoints:
        item = {}
        arguments = {}

        sig = signature(unwrap(func))
        for k, v in sig.parameters.items():
            if k == "request":
                continue
            expanded_args = {
                "default": _get_empty(v.default),
                "annotation": _get_empty(v.annotation),
            }
            arguments[k] = expanded_args

        item["endpoint"] = name
        item["arguments"] = arguments
        item["return_type"] = _get_empty(sig.return_annotation)
        item["doc_string"] = getdoc(func)
        # This is a bit of a hack but I'm not sure of a better way to do this
        # There shouldn't be any overlap between endpoints from RconAPI and any
        # manually created endpoints (there could be, if they were defined with different names)
        # but almost all of our endpoints share the name with functions, and those that don't map
        # to entirely different things like `login -> do_login` that are out of scope of RconAPI
        item["auto_settings_capable"] = name in dir(RconAPI)

        try:
            item["allowed_http_methods"] = ENDPOINT_HTTP_METHODS[func.__name__]
        except KeyError:
            raise ValueError(f"ENDPOINT_HTTP_METHODS key error {func.__name__=}")

        api_docs.append(item)

    return api_response(
        result=sorted(api_docs, key=lambda x: x["endpoint"]),
        command="get_api_documentation",
        failed=False,
    )


# Each explicitly exposed API endpoint and auto-exposed Rcon endpoints
endpoints: list[tuple[str, Callable]] = [
    ("login", auth.do_login),
    ("logout", auth.do_logout),
    ("is_logged_in", auth.is_logged_in),
    ("get_own_user_permissions", auth.get_own_user_permissions),
    ("get_services", services.get_services),
    ("do_service", services.do_service),
    ("get_server_list", multi_servers.get_server_list),
    ("upload_vips", vips.upload_vips),
    ("upload_vips_result", vips.upload_vips_result),
    ("download_vips", vips.download_vips),
    ("get_live_scoreboard", scoreboards.get_live_scoreboard),
    ("get_scoreboard_maps", scoreboards.get_scoreboard_maps),
    ("get_map_scoreboard", scoreboards.get_map_scoreboard),
    ("get_map_history", scoreboards.get_map_history),
    ("get_previous_map", scoreboards.get_previous_map),
    ("get_live_game_stats", scoreboards.get_live_game_stats),
    ("describe_votemap_config", user_settings.describe_votemap_config),
    ("get_auto_settings", auto_settings.get_auto_settings),
    ("set_auto_settings", auto_settings.set_auto_settings),
    ("get_audit_logs", audit_log.get_audit_logs),
    ("get_audit_logs_autocomplete", audit_log.get_audit_logs_autocomplete),
    ("describe_auto_broadcasts_config", user_settings.describe_auto_broadcasts_config),
    (
        "describe_votekick_autotoggle_config",
        user_settings.describe_votekick_autotoggle_config,
    ),
    ("describe_auto_mod_level_config", user_settings.describe_auto_mod_level_config),
    (
        "describe_auto_mod_no_leader_config",
        user_settings.describe_auto_mod_no_leader_config,
    ),
    (
        "describe_auto_mod_seeding_config",
        user_settings.describe_auto_mod_seeding_config,
    ),
    (
        "describe_auto_mod_solo_tank_config",
        user_settings.describe_auto_mod_solo_tank_config,
    ),
    (
        "describe_tk_ban_on_connect_config",
        user_settings.describe_tk_ban_on_connect_config,
    ),
    (
        "describe_camera_notification_config",
        user_settings.describe_camera_notification_config,
    ),
    ("describe_expired_vip_config", user_settings.describe_expired_vip_config),
    (
        "describe_server_name_change_config",
        user_settings.describe_server_name_change_config,
    ),
    (
        "describe_log_line_webhook_config",
        user_settings.describe_log_line_webhook_config,
    ),
    ("describe_name_kick_config", user_settings.describe_name_kick_config),
    (
        "describe_rcon_connection_settings_config",
        user_settings.describe_rcon_connection_settings_config,
    ),
    (
        "describe_rcon_server_settings_config",
        user_settings.describe_rcon_server_settings_config,
    ),
    ("describe_scorebot_config", user_settings.describe_scorebot_config),
    (
        "describe_standard_broadcast_messages",
        user_settings.describe_standard_broadcast_messages,
    ),
    (
        "describe_standard_punishments_messages",
        user_settings.describe_standard_punishments_messages,
    ),
    (
        "describe_standard_welcome_messages",
        user_settings.describe_standard_welcome_messages,
    ),
    ("describe_steam_config", user_settings.describe_steam_config),
    ("describe_vac_game_bans_config", user_settings.describe_vac_game_bans_config),
    (
        "describe_admin_pings_discord_webhooks_config",
        user_settings.describe_admin_pings_discord_webhooks_config,
    ),
    (
        "describe_audit_discord_webhooks_config",
        user_settings.describe_audit_discord_webhooks_config,
    ),
    (
        "describe_camera_discord_webhooks_config",
        user_settings.describe_camera_discord_webhooks_config,
    ),
    (
        "describe_chat_discord_webhooks_config",
        user_settings.describe_chat_discord_webhooks_config,
    ),
    (
        "describe_kills_discord_webhooks_config",
        user_settings.describe_kills_discord_webhooks_config,
    ),
    (
        "describe_watchlist_discord_webhooks_config",
        user_settings.describe_watchlist_discord_webhooks_config,
    ),
    (
        "describe_chat_commands_config",
        user_settings.describe_chat_commands_config,
    ),
    ("describe_real_vip_config", user_settings.describe_real_vip_config),
    ("get_all_discord_webhooks_config", user_settings.get_all_discord_webhooks_config),
    ("get_all_standard_message_config", user_settings.get_all_standard_message_config),
    ("reconnect_gameserver", views.restart_gunicorn),
] + [(name, func) for name, func in views.commands]

# Expose endpoints though Django
urlpatterns = [path(name, func, name=name) for name, func in endpoints] + [
    path("get_api_documentation", get_api_documentation, name="get_api_documentation")
]

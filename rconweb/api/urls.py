from inspect import _empty, getdoc, signature, unwrap
from typing import Callable

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import (
    audit_log,
    auth,
    auto_settings,
    history,
    logs,
    multi_servers,
    scoreboards,
    server_stats,
    services,
    user_settings,
    views,
    vips,
    votemap,
)
from .auth import api_response


def _get_empty(value):
    """Return None for inspect._empty values or the value as a string"""
    if value is _empty:
        return None
    else:
        return str(value)


@csrf_exempt
def get_api_documentation(request):
    """Auto-generate minimal API documentation through introspection"""

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
    ("get_online_mods", auth.get_online_mods),
    ("get_ingame_mods", auth.get_ingame_mods),
    ("get_own_user_permissions", auth.get_own_user_permissions),
    ("get_services", services.get_services),
    ("do_service", services.do_service),
    ("server_list", multi_servers.get_server_list),
    ("get_recent_logs", logs.get_recent_logs),
    ("get_historical_logs", logs.get_historical_logs),
    ("upload_vips", vips.upload_vips),
    ("async_upload_vips", vips.async_upload_vips),
    ("async_upload_vips_result", vips.async_upload_vips_result),
    ("download_vips", vips.download_vips),
    ("live_scoreboard", scoreboards.live_scoreboard),
    ("date_scoreboard", scoreboards.date_scoreboard),
    ("get_scoreboard_maps", scoreboards.get_scoreboard_maps),
    ("get_map_scoreboard", scoreboards.get_map_scoreboard),
    ("get_live_game_stats", scoreboards.get_live_game_stats),
    ("players_history", history.players_history),
    ("flag_player", history.flag_player),
    ("unflag_player", history.unflag_player),
    ("player", history.get_player),
    ("get_previous_map", history.get_previous_map),
    ("get_map_history", history.get_map_history),
    ("do_add_map_to_whitelist", votemap.do_add_map_to_whitelist),
    ("do_add_maps_to_whitelist", votemap.do_add_maps_to_whitelist),
    ("do_remove_map_from_whitelist", votemap.do_remove_map_from_whitelist),
    ("do_remove_maps_from_whitelist", votemap.do_remove_maps_from_whitelist),
    ("do_reset_map_whitelist", votemap.do_reset_map_whitelist),
    ("do_set_map_whitelist", votemap.do_set_map_whitelist),
    ("get_map_whitelist", votemap.get_map_whitelist),
    ("get_votemap_config", votemap.get_votemap_config),
    ("describe_votemap_config", votemap.describe_votemap_config),
    ("validate_votemap_config", votemap.validate_votemap_config),
    ("set_votemap_config", votemap.set_votemap_config),
    ("get_votemap_status", votemap.get_votemap_status),
    ("reset_votemap_state", votemap.reset_votemap_state),
    ("get_player_messages", history.get_player_messages),
    ("get_player_comment", history.get_player_comment),
    ("post_player_comment", history.post_player_comment),
    ("get_real_vip_config", vips.get_real_vip_config),
    ("describe_real_vip_config", vips.describe_real_vip_config),
    ("validate_real_vip_config", vips.validate_real_vip_config),
    ("set_real_vip_config", vips.set_real_vip_config),
    ("get_auto_settings", auto_settings.get_auto_settings),
    ("set_auto_settings", auto_settings.set_auto_settings),
    ("get_server_stats", server_stats.get_server_stats),
    ("get_audit_logs", audit_log.get_audit_logs),
    ("get_audit_logs_autocomplete", audit_log.get_audit_logs_autocomplete),
    ("get_auto_broadcasts_config", user_settings.get_auto_broadcasts_config),
    ("describe_auto_broadcasts_config", user_settings.describe_auto_broadcasts_config),
    ("validate_auto_broadcasts_config", user_settings.validate_auto_broadcasts_config),
    ("set_auto_broadcasts_config", user_settings.set_auto_broadcasts_config),
    ("get_votekick_autotoggle_config", user_settings.get_votekick_autotoggle_config),
    (
        "describe_votekick_autotoggle_config",
        user_settings.describe_votekick_autotoggle_config,
    ),
    (
        "validate_votekick_autotoggle_config",
        user_settings.validate_votekick_autotoggle_config,
    ),
    ("set_votekick_autotoggle_config", user_settings.set_votekick_autotoggle_config),
    ("get_auto_mod_level_config", user_settings.get_auto_mod_level_config),
    ("describe_auto_mod_level_config", user_settings.describe_auto_mod_level_config),
    ("validate_auto_mod_level_config", user_settings.validate_auto_mod_level_config),
    ("set_auto_mod_level_config", user_settings.set_auto_mod_level_config),
    ("get_auto_mod_no_leader_config", user_settings.get_auto_mod_no_leader_config),
    (
        "describe_auto_mod_no_leader_config",
        user_settings.describe_auto_mod_no_leader_config,
    ),
    (
        "validate_auto_mod_no_leader_config",
        user_settings.validate_auto_mod_no_leader_config,
    ),
    ("set_auto_mod_no_leader_config", user_settings.set_auto_mod_no_leader_config),
    ("get_auto_mod_seeding_config", user_settings.get_auto_mod_seeding_config),
    (
        "describe_auto_mod_seeding_config",
        user_settings.describe_auto_mod_seeding_config,
    ),
    (
        "validate_auto_mod_seeding_config",
        user_settings.validate_auto_mod_seeding_config,
    ),
    ("set_auto_mod_seeding_config", user_settings.set_auto_mod_seeding_config),
    ("get_auto_mod_solo_tank_config", user_settings.get_auto_mod_solo_tank_config),
    (
        "describe_auto_mod_solo_tank_config",
        user_settings.describe_auto_mod_solo_tank_config,
    ),
    (
        "validate_auto_mod_solo_tank_config",
        user_settings.validate_auto_mod_solo_tank_config,
    ),
    ("set_auto_mod_solo_tank_config", user_settings.set_auto_mod_solo_tank_config),
    ("get_tk_ban_on_connect_config", user_settings.get_tk_ban_on_connect_config),
    (
        "describe_tk_ban_on_connect_config",
        user_settings.describe_tk_ban_on_connect_config,
    ),
    (
        "validate_tk_ban_on_connect_config",
        user_settings.validate_tk_ban_on_connect_config,
    ),
    ("set_tk_ban_on_connect_config", user_settings.set_tk_ban_on_connect_config),
    ("get_camera_notification_config", user_settings.get_camera_notification_config),
    (
        "describe_camera_notification_config",
        user_settings.describe_camera_notification_config,
    ),
    (
        "validate_camera_notification_config",
        user_settings.validate_camera_notification_config,
    ),
    ("set_camera_notification_config", user_settings.set_camera_notification_config),
    ("get_expired_vip_config", user_settings.get_expired_vip_config),
    ("describe_expired_vip_config", user_settings.describe_expired_vip_config),
    ("validate_expired_vip_config", user_settings.validate_expired_vip_config),
    ("set_expired_vip_config", user_settings.set_expired_vip_config),
    ("get_server_name_change_config", user_settings.get_server_name_change_config),
    (
        "describe_server_name_change_config",
        user_settings.describe_server_name_change_config,
    ),
    (
        "validate_server_name_change_config",
        user_settings.validate_server_name_change_config,
    ),
    ("set_server_name_change_config", user_settings.set_server_name_change_config),
    ("get_log_line_webhook_config", user_settings.get_log_line_webhook_config),
    (
        "describe_log_line_webhook_config",
        user_settings.describe_log_line_webhook_config,
    ),
    (
        "validate_log_line_webhook_config",
        user_settings.validate_log_line_webhook_config,
    ),
    ("set_log_line_webhook_config", user_settings.set_log_line_webhook_config),
    ("get_name_kick_config", user_settings.get_name_kick_config),
    ("describe_name_kick_config", user_settings.describe_name_kick_config),
    ("validate_name_kick_config", user_settings.validate_name_kick_config),
    ("set_name_kick_config", user_settings.set_name_kick_config),
    (
        "get_rcon_connection_settings_config",
        user_settings.get_rcon_connection_settings_config,
    ),
    (
        "describe_rcon_connection_settings_config",
        user_settings.describe_rcon_connection_settings_config,
    ),
    (
        "validate_rcon_connection_settings_config",
        user_settings.validate_rcon_connection_settings_config,
    ),
    (
        "set_rcon_connection_settings_config",
        user_settings.set_rcon_connection_settings_config,
    ),
    ("get_rcon_server_settings_config", user_settings.get_rcon_server_settings_config),
    (
        "describe_rcon_server_settings_config",
        user_settings.describe_rcon_server_settings_config,
    ),
    (
        "validate_rcon_server_settings_config",
        user_settings.validate_rcon_server_settings_config,
    ),
    ("set_rcon_server_settings_config", user_settings.set_rcon_server_settings_config),
    ("get_scorebot_config", user_settings.get_scorebot_config),
    ("describe_scorebot_config", user_settings.describe_scorebot_config),
    ("validate_scorebot_config", user_settings.validate_scorebot_config),
    ("set_scorebot_config", user_settings.set_scorebot_config),
    ("get_standard_broadcast_messages", user_settings.get_standard_broadcast_messages),
    (
        "describe_standard_broadcast_messages",
        user_settings.describe_standard_broadcast_messages,
    ),
    (
        "validate_standard_broadcast_messages",
        user_settings.validate_standard_broadcast_messages,
    ),
    ("set_standard_broadcast_messages", user_settings.set_standard_broadcast_messages),
    (
        "get_standard_punishments_messages",
        user_settings.get_standard_punishments_messages,
    ),
    (
        "describe_standard_punishments_messages",
        user_settings.describe_standard_punishments_messages,
    ),
    (
        "validate_standard_punishments_messages",
        user_settings.validate_standard_punishments_messages,
    ),
    (
        "set_standard_punishments_messages",
        user_settings.set_standard_punishments_messages,
    ),
    ("get_standard_welcome_messages", user_settings.get_standard_welcome_messages),
    (
        "describe_standard_welcome_messages",
        user_settings.describe_standard_welcome_messages,
    ),
    (
        "validate_standard_welcome_messages",
        user_settings.validate_standard_welcome_messages,
    ),
    ("set_standard_welcome_messages", user_settings.set_standard_welcome_messages),
    ("get_steam_config", user_settings.get_steam_config),
    ("describe_steam_config", user_settings.describe_steam_config),
    ("validate_steam_config", user_settings.validate_steam_config),
    ("set_steam_config", user_settings.set_steam_config),
    ("get_vac_game_bans_config", user_settings.get_vac_game_bans_config),
    ("describe_vac_game_bans_config", user_settings.describe_vac_game_bans_config),
    ("validate_vac_game_bans_config", user_settings.validate_vac_game_bans_config),
    ("set_vac_game_bans_config", user_settings.set_vac_game_bans_config),
    (
        "get_admin_pings_discord_webhooks_config",
        user_settings.get_admin_pings_discord_webhooks_config,
    ),
    (
        "describe_admin_pings_discord_webhooks_config",
        user_settings.describe_admin_pings_discord_webhooks_config,
    ),
    (
        "validate_admin_pings_discord_webhooks_config",
        user_settings.validate_admin_pings_discord_webhooks_config,
    ),
    (
        "set_admin_pings_discord_webhooks_config",
        user_settings.set_admin_pings_discord_webhooks_config,
    ),
    (
        "get_audit_discord_webhooks_config",
        user_settings.get_audit_discord_webhooks_config,
    ),
    (
        "describe_audit_discord_webhooks_config",
        user_settings.describe_audit_discord_webhooks_config,
    ),
    (
        "validate_audit_discord_webhooks_config",
        user_settings.validate_audit_discord_webhooks_config,
    ),
    (
        "set_audit_discord_webhooks_config",
        user_settings.set_audit_discord_webhooks_config,
    ),
    (
        "get_camera_discord_webhooks_config",
        user_settings.get_camera_discord_webhooks_config,
    ),
    (
        "describe_camera_discord_webhooks_config",
        user_settings.describe_camera_discord_webhooks_config,
    ),
    (
        "validate_camera_discord_webhooks_config",
        user_settings.validate_camera_discord_webhooks_config,
    ),
    (
        "set_camera_discord_webhooks_config",
        user_settings.set_camera_discord_webhooks_config,
    ),
    (
        "get_chat_discord_webhooks_config",
        user_settings.get_chat_discord_webhooks_config,
    ),
    (
        "describe_chat_discord_webhooks_config",
        user_settings.describe_chat_discord_webhooks_config,
    ),
    (
        "validate_chat_discord_webhooks_config",
        user_settings.validate_chat_discord_webhooks_config,
    ),
    (
        "set_chat_discord_webhooks_config",
        user_settings.set_chat_discord_webhooks_config,
    ),
    (
        "get_kills_discord_webhooks_config",
        user_settings.get_kills_discord_webhooks_config,
    ),
    (
        "describe_kills_discord_webhooks_config",
        user_settings.describe_kills_discord_webhooks_config,
    ),
    (
        "validate_kills_discord_webhooks_config",
        user_settings.validate_kills_discord_webhooks_config,
    ),
    (
        "set_kills_discord_webhooks_config",
        user_settings.set_kills_discord_webhooks_config,
    ),
    (
        "get_watchlist_discord_webhooks_config",
        user_settings.get_watchlist_discord_webhooks_config,
    ),
    (
        "describe_watchlist_discord_webhooks_config",
        user_settings.describe_watchlist_discord_webhooks_config,
    ),
    (
        "validate_watchlist_discord_webhooks_config",
        user_settings.validate_watchlist_discord_webhooks_config,
    ),
    (
        "set_watchlist_discord_webhooks_config",
        user_settings.set_watchlist_discord_webhooks_config,
    ),
    ("get_all_discord_webhooks_config", user_settings.get_all_discord_webhooks_config),
    ("get_all_standard_message_config", user_settings.get_all_standard_message_config),
    ("do_reconnect_gameserver", views.restart_gunicorn),
] + [(name, func) for name, func in views.commands]

# Expose endpoints though Django
urlpatterns = [path(name, func, name=name) for name, func in endpoints] + [
    path("get_api_documentation", get_api_documentation, name="get_api_documentation")
]

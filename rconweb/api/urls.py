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

        item["name"] = name
        item["arguments"] = arguments
        item["return_type"] = _get_empty(sig.return_annotation)
        item["doc_string"] = getdoc(func)

        api_docs.append(item)

    return api_response(
        result=sorted(api_docs, key=lambda x: x["name"]),
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
    ("get_map_history", history.get_map_history),
    ("do_add_map_to_whitelist", votemap.do_add_map_to_whitelist),
    ("do_add_maps_to_whitelist", votemap.do_add_maps_to_whitelist),
    ("do_remove_map_from_whitelist", votemap.do_remove_map_from_whitelist),
    ("do_remove_maps_from_whitelist", votemap.do_remove_maps_from_whitelist),
    ("do_reset_map_whitelist", votemap.do_reset_map_whitelist),
    ("do_set_map_whitelist", votemap.do_set_map_whitelist),
    ("get_map_whitelist", votemap.get_map_whitelist),
    ("get_votemap_config", votemap.get_votemap_config),
    ("get_votemap_status", votemap.get_votemap_status),
    ("reset_votemap_state", votemap.reset_votemap_state),
    ("set_votemap_config", votemap.set_votemap_config),
    ("get_player_messages", history.get_player_messages),
    ("get_player_comment", history.get_player_comment),
    ("post_player_comment", history.post_player_comment),
    ("get_real_vip_config", vips.get_real_vip_config),
    ("set_real_vip_config", vips.set_real_vip_config),
    ("get_auto_settings", auto_settings.get_auto_settings),
    ("set_auto_settings", auto_settings.set_auto_settings),
    ("get_server_stats", server_stats.get_server_stats),
    ("get_audit_logs", audit_log.get_audit_logs),
    ("get_audit_logs_autocomplete", audit_log.get_audit_logs_autocomplete),
] + [(name, func) for name, func in views.commands]

# Expose endpoints though Django
urlpatterns = [path(name, func, name=name) for name, func in endpoints] + [
    path("document_api", get_api_documentation, name="get_api_documentation")
]

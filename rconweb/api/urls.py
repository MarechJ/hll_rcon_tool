from rcon import scoreboard
from django.urls import path

from . import views
from . import auth
from . import services
from . import multi_servers
from . import logs
from . import vips
from . import scoreboards
from . import history
from . import votemap


urlpatterns = [
    path(name, func, name='name')
    for name, func in views.commands
] + [
    path('login', auth.do_login),
    path('logout', auth.do_logout),
    path('is_logged_in', auth.is_logged_in),
    path('get_online_mods', auth.get_online_mods),
    path('get_ingame_mods', auth.get_ingame_mods),
    path('get_services', services.get_services),
    path('do_service', services.do_service),
    path('server_list',  multi_servers.get_server_list),
    path("get_recent_logs", logs.get_recent_logs),
    path("get_historical_logs", logs.get_historical_logs),
    path("upload_vips", vips.upload_vips),
    path("async_upload_vips", vips.async_upload_vips),
    path("async_upload_vips_result", vips.async_upload_vips_result),
    path("download_vips", vips.download_vips),
    path("live_scoreboard", scoreboards.live_scoreboard),
    path("date_scoreboard", scoreboards.date_scoreboard),
    path("get_scoreboard_maps", scoreboards.get_scoreboard_maps),
    path("get_map_scoreboard", scoreboards.get_map_scoreboard),
    path("get_live_game_stats", scoreboards.get_live_game_stats),
    path("players_history", history.players_history),
    path("flag_player", history.flag_player),
    path("unflag_player", history.unflag_player),
    path("player", history.get_player),
    path("get_map_history", history.get_map_history),
    path("get_votemap_config", votemap.get_votemap_config),
    path("set_votemap_config", votemap.set_votemap_config),
    path("get_votemap_status", votemap.get_votemap_status),
    path("reset_votemap_state", votemap.reset_votemap_state),
    path("get_player_comment", history.get_player_comment),
    path("post_player_comment", history.post_player_comment)
]

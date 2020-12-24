from django.urls import path

from . import views
from . import auth
from . import services
from . import multi_servers
from . import logs
from . import vips
from . import scoreboards
from . import history

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
    path("download_vips", vips.download_vips),
    path("scoreboard", scoreboards.text_scoreboard),
    path("tk", scoreboards.text_tk_scoreboard),
    path("players_history", history.players_history),
    path("flag_player", history.flag_player),
    path("unflag_player", history.unflag_player),
    path("player", history.get_player),
    path("get_map_history", history.get_map_history),
]

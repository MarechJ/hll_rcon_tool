import datetime
from django.views.decorators.csrf import csrf_exempt
from .auth import api_response, login_required
from .views import ctl, _get_data
from rcon.server_stats import get_db_server_stats_for_range, get_server_stats_for_range
from dateutil import parser

@csrf_exempt
@login_required
def get_server_stats(request):
    data = _get_data(request)

    try:
        with_players = int(data.get("with_players", 0))
    except ValueError:
        with_players = 0
    start = data.get("start")
    if start:
        start = parser.parse(start)
    else:
        start = (datetime.datetime.now() - datetime.timedelta(hours=24))

    end = data.get("end")
    if end:
        end = parser.parse(end)
    else:
        end = datetime.datetime.now()

    return api_response(
        result=get_db_server_stats_for_range(start=start, end=end, by_map=True, with_player_list=with_players), error=None, failed=False, command="get_server_stats"
    )


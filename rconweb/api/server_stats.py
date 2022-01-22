import datetime
from django.views.decorators.csrf import csrf_exempt
from .auth import api_response, login_required
from .views import ctl, _get_data
from rcon.server_stats import get_db_server_stats_for_range, get_server_stats_for_range
from dateutil import parser

@csrf_exempt
def get_server_stats(request):
    data = _get_data(request)

    start = data.get("start")
    if start:
        start = parser.parse(start)
    else:
        start = (datetime.datetime.now() - datetime.timedelta(hours=24))
        start = datetime.datetime(year=2022, month=1, day=9, hour=18, minute=0, second=0, microsecond=0)
    end = data.get("end")
    if end:
        end = parser.parse(end)
        
    else:
        end = datetime.datetime.now()
        end = datetime.datetime(year=2022, month=1, day=9, hour=18, minute=59, second=59, microsecond=999)
    #return api_response(
    #    result=get_db_server_stats_for_range(start=start, end=end, by_map=True), error=None, failed=False, command="get_server_stats"
    #)
    return api_response(
        result=get_server_stats_for_range(start=start, end=end, by_map=True), error=None, failed=False, command="get_server_stats"
    )


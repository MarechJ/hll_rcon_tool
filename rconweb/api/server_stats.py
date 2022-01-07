from django.views.decorators.csrf import csrf_exempt
from .auth import api_response, login_required
from .views import ctl, _get_data
from rcon.server_stats import get_server_stats_for_range

@csrf_exempt
def get_server_stats(request):
    #data = _get_data(request)

    return api_response(
        result=get_server_stats_for_range(by_map=True), error=None, failed=False, command="get_server_stats"
    )


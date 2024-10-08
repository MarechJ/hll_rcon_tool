from .auth import api_csv_response
from rcon.api_commands import get_rcon_api

from dateutil import parser
from django.views.decorators.csrf import csrf_exempt
from .decorators import require_http_methods


from .auth import api_csv_response, login_required
from .decorators import require_content_type, permission_required
from .utils import _get_data


@csrf_exempt
@login_required()
@permission_required("api.can_view_historical_logs", raise_exception=True)
@require_http_methods(["GET", "POST"])
@require_content_type()
def get_historical_logs_csv(request):
    rcon_api = get_rcon_api()
    data = _get_data(request)

    player_name = data.get("player_name")
    action = data.get("action")
    player_id = data.get("player_id")
    limit = int(data.get("limit", 1000))
    from_ = data.get("from")
    till = data.get("till")
    time_sort = data.get("time_sort", "desc")
    exact_player_match = data.get("exact_player", False)
    exact_action = data.get("exact_action", True)
    server_filter = data.get("server_filter")

    if till:
        till = parser.parse(till)
    if from_:
        from_ = parser.parse(from_)

    lines = rcon_api.get_historical_logs(
        player_name=player_name,
        player_id=player_id,
        action=action,
        limit=limit,
        from_=from_,
        till=till,
        time_sort=time_sort,
        exact_player_match=exact_player_match,
        exact_action=exact_action,
        server_filter=server_filter,
    )

    return api_csv_response(
        lines,
        "log.csv",
        [
            "id",
            "version",
            "creation_time",
            "event_time",
            "type",
            "player1_name",
            "player1_id",
            "player2_name",
            "player2_id",
            "content",
            "server",
            "weapon",
            "raw",
        ],
    )

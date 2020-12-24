
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt


from rcon.utils import MapsHistory
from rcon.recorded_commands import RecordedRcon
from rcon.commands import CommandFailedError
from rcon.steam_utils import get_steam_profile
from rcon.settings import SERVER_INFO
from .auth import login_required, api_response
from .utils import _get_data
from rcon import game_logs
from rcon.models import LogLine, PlayerSteamID, PlayerName, enter_session
from sqlalchemy import or_, and_



@csrf_exempt
@login_required
def get_historical_logs(request):
    data = _get_data(request)
    player_name = data.get("player_name")
    action = data.get("log_type")
    steam_id_64 = data.get("steam_id_64")
    limit = int(data.get("limit", 1000))
    from_ = data.get("from")
    till = data.get("till")
    time_sort = data.get("time_sort", "desc")
    exact_player_match = data.get("exact_player", False)
    exact_action = data.get("exact_action", True)

    with enter_session() as sess:
        names = []
        name_filters = []

        q = sess.query(LogLine)
        if action and not exact_action:
            q = q.filter(LogLine.type.ilike(f"%{action}%"))
        elif action and exact_action:
            q = q.filter(LogLine.type == action)

        time_filter = []
        if from_:
            from_ = parser.parse(from_)
            time_filter.append(LogLine.event_time >= from_)

        if till:
            till = parser.parse(till)
            time_filter.append(LogLine.event_time <= till)

        q = q.filter(and_(*time_filter))

        if steam_id_64:
            # Handle not found
            player = (
                sess.query(PlayerSteamID)
                .filter(PlayerSteamID.steam_id_64 == steam_id_64)
                .one_or_none()
            )
            id_ = player.id if player else 0
            q = q.filter(
                or_(LogLine.player1_steamid == id_, LogLine.player2_steamid == id_)
            )

        if player_name and not exact_player_match:
            name_filters.extend(
                [
                    LogLine.player1_name.ilike("%{}%".format(player_name)),
                    LogLine.player2_name.ilike("%{}%".format(player_name)),
                ]
            )
        elif player_name and exact_player_match:
            name_filters.extend(
                [
                    LogLine.player1_name == player_name,
                    LogLine.player2_name == player_name,
                ]
            )

        if name_filters:
            q = q.filter(or_(*name_filters))

        res = (
            q.order_by(
                LogLine.event_time.desc()
                if time_sort == "desc"
                else LogLine.event_time.asc()
            )
            .limit(limit)
            .all()
        )

        lines = []
        for r in res:
            r = r.to_dict()
            r["event_time"] = r["event_time"].timestamp()
            lines.append(r)
        return api_response(
            lines,
            command="get_historical_logs",
            arguments=dict(limit=limit, player_name=player_name, action=action),
            failed=False,
        )


@csrf_exempt
@login_required
def get_recent_logs(request):
    data = _get_data(request)
    start = int(data.get("start", 0))
    end = int(data.get("end", 10000))
    player_search = data.get("filter_player")
    action_filter = data.get("filter_action")
    exact_player_match = data.get("exact_player_match", True)
    exact_action = data.get("exact_action", False)
    

    return api_response(
        result=game_logs.get_recent_logs(
            start=start,
            end=end,
            player_search=player_search,
            action_filter=action_filter,
            exact_player_match=exact_player_match,
            exact_action=exact_action
        ),
        command="get_recent_logs",
        arguments=dict(
            start=start,
            end=end,
            filter_player=player_search,
            filter_action=action_filter,
        ),
        failed=False,
    )

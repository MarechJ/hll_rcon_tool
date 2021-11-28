from rcon.player_history import get_players_by_time
from rcon.models import enter_session, PlayerSession, PlayerName, PlayerSteamID
import datetime
import pandas as pd
from sqlalchemy import and_, or_ 
from sqlalchemy.orm import joinedload, session
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from django.views.decorators.csrf import csrf_exempt
from .auth import api_response, login_required

@csrf_exempt
def get_server_stats(request):
    return api_response(
        result=_get_server_stats(), error=None, failed=False, command="get_server_stats"
    )

def _get_server_stats(start=None, end=None):
    if start is None:
        start = datetime.datetime.now() - datetime.timedelta(hours=24)
    if end is None:
        end = datetime.datetime.now()
    
    if start > end:
        raise ValueError("Start time can't be after end time")
    
    start.replace(second=0, microsecond=0)
    end.replace(second=0, microsecond=0)

    with enter_session() as sess:
        series = pd.date_range(start=start, end=end, freq='T')
        series = series.to_list()
        
        q = sess.query(PlayerSession).filter(and_(PlayerSession.start >= start, or_(PlayerSession.end <=end, PlayerSession.end == None))).options(joinedload(PlayerSession.steamid)) 
        sessions = q.all()

        stat = []
        for minute in series:
            present_players = []
            for player_session in sessions:
                if not player_session.start:
                    # TODO handle current players
                    continue
                session_end = player_session.end or end
                if player_session.start <= minute <= session_end:
                    present_players.append(player_session.steamid.names[0].name)
            stat.append((minute, {"count": len(present_players), "players": present_players}))
    return stat

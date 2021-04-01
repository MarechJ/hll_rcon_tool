from datetime import datetime
from os import error
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.utils import MapsHistory
from rcon.recorded_commands import RecordedRcon
from rcon.commands import CommandFailedError
from rcon.steam_utils import get_steam_profile
from rcon.settings import SERVER_INFO
from rcon import game_logs
from rcon.models import LogLine, PlayerSteamID, PlayerName, enter_session
from rcon.discord import send_to_discord_audit
from rcon.scoreboard import LiveStats, TimeWindowStats

from .views import ctl
from .auth import api_response, login_required

logger = logging.getLogger('rconweb')

def make_table(scoreboard):
    return "\n".join(
        ["Rank  Name                  Ratio Kills Death"]
        + [
            f"{('#'+ str(idx+1)).ljust(6)}{obj['player'].ljust(27)}{obj['ratio'].ljust(6)}{str(obj['(real) kills']).ljust(6)}{str(obj['(real) death']).ljust(5)}"
            for idx, obj in enumerate(scoreboard)
        ]
    )


def make_tk_table(scoreboard):
    justification = [6, 27, 10, 10, 14, 14]
    headers = ["Rank", "Name", "Time(min)", "Teamkills", "Death-by-TK", "TK/Minutes"]
    keys = [
        "idx",
        "player",
        "Estimated play time (minutes)",
        "Teamkills",
        "Death by TK",
        "TK Minutes",
    ]

    return "\n".join(
        ["".join(h.ljust(justification[idx]) for idx, h in enumerate(headers))]
        + [
            "".join(
                [
                    str({"idx": f"#{idx}", **obj}[key]).ljust(justification[i])
                    for i, key in enumerate(keys)
                ]
            )
            for idx, obj in enumerate(scoreboard)
        ]
    )


@csrf_exempt
def text_scoreboard(request):
    try:
        minutes = abs(int(request.GET.get("minutes")))
    except (ValueError, KeyError, TypeError):
        minutes = 180

    name = ctl.get_name()
    try:
        scoreboard = ctl.get_scoreboard(minutes, "ratio")
        text = make_table(scoreboard)
        scoreboard = ctl.get_scoreboard(minutes, "(real) kills")
        text2 = make_table(scoreboard)
    except CommandFailedError:
        text, text2 = "No logs"

    return HttpResponse(
        f"""<div>
        <h1>{name}</h1>
        <h1>Scoreboard (last {minutes} min. 2min delay)</h1>
        <h6>Real death only (redeploy / suicides not included). Kills counted only if player is not revived</h6>
        <p>
        See for last:
        <a href="/api/scoreboard?minutes=120">120 min</a>
        <a href="/api/scoreboard?minutes=90">90 min</a>
        <a href="/api/scoreboard?minutes=60">60 min</a>
        <a href="/api/scoreboard?minutes=30">30 min</a>
        </p>
        <div style="float:left; margin-right:20px"><h3>By Ratio</h3><pre>{text}</pre></div>
        <div style="float:left; margin-left:20px"><h3>By Kills</h3><pre>{text2}</pre></div>
        </div>
        """
    )


@csrf_exempt
def text_tk_scoreboard(request):
    name = ctl.get_name()
    try:
        scoreboard = ctl.get_teamkills_boards()
        text = make_tk_table(scoreboard)
        scoreboard = ctl.get_teamkills_boards("Teamkills")
        text2 = make_tk_table(scoreboard)
    except CommandFailedError:
        text, text2 = "No logs"

    return HttpResponse(
        f"""<div>
        <h1>{name}</h1>
        <div style="float:left; margin-right:20px"><h3>By TK / Minute</h3><pre>{text}</pre></div>
        <div style="float:left; margin-left:20px"><h3>By Total TK</h3><pre>{text2}</pre></div>
        </div>
        """
    )

@csrf_exempt
def live_info(request):
    status = ctl.get_status()


@csrf_exempt
def live_scoreboard(request):
    stats = LiveStats()

    try:
        result = stats.get_cached_stats()
        result = {
            "snapshot_timestamp": result["snapshot_timestamp"],
            "stats": list(result["stats"].values())
        }
        error = None,
        failed = False
    except Exception as e:
        logger.exception("Unable to produce live stats")
        result = {}
        error = ""
        failed=True

    return api_response(
        result=result,
        error=error,
        failed=failed,
        command="live_scoreboard"
    )

@csrf_exempt
def date_scoreboard(request):

    try:
        start = datetime.fromtimestamp(int(request.GET.get("start"))).isoformat()
    except (ValueError, KeyError, TypeError):
        start = None
    try:
        end = datetime.fromtimestamp(int(request.GET.get("end"))).isoformat()
    except (ValueError, KeyError, TypeError):
        end = None

    stats = TimeWindowStats()

    try:
        result = stats.get_players_stats_at_time(start, end)
        error_ = None,
        failed = False

    except Exception as e:
        logger.exception("Unable to produce date stats")
        result = {}
        error_ = ""
        failed = True

    return api_response(
        result=result,
        error=error_,
        failed=failed,
        command="date_scoreboard"
    )
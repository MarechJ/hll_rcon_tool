import inspect
import logging
import json
from functools import wraps
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rcon.extended_commands import Rcon
from rcon.commands import CommandFailedError
from rcon.settings import SERVER_INFO
from rcon.player_history import (
    get_players_by_appearance, 
    add_player_to_blacklist, 
    remove_player_from_blacklist
)

logger = logging.getLogger('rconweb')




def _get_data(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return request.GET

@csrf_exempt
def blacklist_player(request):
    data = _get_data(request)
    res = {}
    try:
        add_player_to_blacklist(data['steam_id_64'], data['reason'])
        failed = False
    except:
        logger.exception("Unable to blacklist player")
        failed = True

    return JsonResponse({
        "result": res,
        "command": "players_history",
        "arguments": data,
        "failed": failed
    })


@csrf_exempt
def unblacklist_player(request):
    data = _get_data(request)
    res = {}
    try:
        remove_player_from_blacklist(data['steam_id_64'])
        failed = False
    except:
        logger.exception("Unable to unblacklist player")
        failed = True

    return JsonResponse({
        "result": res,
        "command": "players_history",
        "arguments": data,
        "failed": failed
    })


@csrf_exempt
def players_history(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET
    try:
        res = get_players_by_appearance(int(data.get('page', 1)), int(data.get('page_size', 200)))
        failed = False
    except:
        logger.exception("Unable to get player history")
        res = {}
        failed = True

    return JsonResponse({
        "result": res,
        "command": "players_history",
        "arguments": data,
        "failed": failed
    })


def wrap_method(func, parameters):
    @csrf_exempt
    def wrapper(request):
        logger = logging.getLogger('rconweb')
        arguments = {}
        data = {}
        failure = False

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.GET

        logger.info("%s %s", func.__name__, data)

        for pname, param in parameters.items():
            if param.default != inspect._empty:
                arguments[pname] = data.get(pname)
            else:
                try:
                    arguments[pname] = data[pname]
                except KeyError:
                    # TODO raise 400
                    raise

        try:
            logger.debug("%s %s", func.__name__, arguments)
            res = func(**arguments)
        except CommandFailedError:
            failure = True
            res = None
        #logger.debug("%s %s -> %s", func.__name__, arguments, res)
        return JsonResponse({
            "result": res,
            "command": func.__name__,
            "arguments": data,
            "failed": failure
        })
    return wrapper


ctl = Rcon(
    SERVER_INFO
)

def make_table(scoreboard):
    return '\n'.join(
        ["Rank  Name                  Ratio Kills Death"] + [
        f"{('#'+ str(idx+1)).ljust(6)}{obj['player'].ljust(22)}{obj['ratio'].ljust(6)}{str(obj['(real) kills']).ljust(6)}{str(obj['(real) death']).ljust(5)}"  
        for idx, obj in enumerate(scoreboard)]
    )

@csrf_exempt
def text_scoreboard(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET

    scoreboard = ctl.get_scoreboard(180, "ratio")
    text = make_table(scoreboard)
    scoreboard = ctl.get_scoreboard(180, "(real) kills")
    text2 = make_table(scoreboard)
    return HttpResponse(
        f'<div><h1>Scoreboard (last 180 min)</h1><h6>Real death only (redeploy / suicides not included). Kills counted only if player is not revived</h6><div style="float:left; margin-right:20px"><h3>By Ratio</h3><pre>{text}</pre></div><div style="float:left; margin-left:20px"><h3>By Kills</h3><pre>{text2}</pre></div></div>'
    )

PREFIXES_TO_EXPOSE = [
    'get_', 'set_', 'do_'
]

commands = [
    ("players_history", players_history),
    ("blacklist_player", blacklist_player),
    ("unblacklist_player", unblacklist_player),
    ("text_scoreboard", text_scoreboard)
]

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
        continue

    commands.append(
        (name, wrap_method(func, inspect.signature(func).parameters))
    )

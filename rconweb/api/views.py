import inspect
import logging
import json
import datetime
from functools import wraps

from dateutil import parser
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from rcon.recorded_commands import RecordedRcon
from rcon.commands import CommandFailedError
from rcon.settings import SERVER_INFO
from rcon.player_history import (
    get_players_by_appearance, 
    add_player_to_blacklist, 
    remove_player_from_blacklist,
    get_player_profile
)
from rcon.user_config import AutoBroadcasts, InvalidConfigurationError
from rcon.cache_utils import RedisCached, get_redis_pool

logger = logging.getLogger('rconweb')


# TODO this does not work if's there a second reverse proxy on the host of docker
# TODO Remove when user accounts are implemented
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def _get_data(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET
    return data

@csrf_exempt
def clear_cache(request):
    res = RedisCached.clear_all_caches(get_redis_pool())
    return JsonResponse({
        "result": res,
        "command": "clear_cache",
        "arguments": None,
        "failed": res is None
    })

@csrf_exempt
def get_auto_broadcasts_config(request):
    failed = False
    config = None
    
    try:
        broadcasts = AutoBroadcasts()
        config = {
            'messages': ["{} {}".format(m[0], m[1]) for m in broadcasts.get_messages()],
            'randomized': broadcasts.get_randomize(),
            'enabled': broadcasts.get_enabled()
        }
    except:
        logger.exception("Error fetch broadcasts config")
        failed = True

    return JsonResponse({
        "result": config,
        "command": "get_auto_broadcasts_config",
        "arguments": None,
        "failed": failed
    })

@csrf_exempt
def set_auto_broadcasts_config(request):
    failed = False
    res = None
    data = _get_data(request)
    broadcasts = AutoBroadcasts()
    config_keys = {
        'messages': broadcasts.set_messages, 
        'randomized': broadcasts.set_randomize, 
        'enabled': broadcasts.set_enabled,
    }
    try:
        for k, v in data.items():
            if k in config_keys:
                config_keys[k](v)
    except InvalidConfigurationError as e:
        failed = True
        res = str(e)

    return JsonResponse({
        "result": res,
        "command": "set_auto_broadcasts_config",
        "arguments": data,
        "failed": failed
    })


@csrf_exempt
def get_player(request):
    data = _get_data(request)
    res = {}
    try:
        res = get_player_profile(data['steam_id_64'], nb_sessions=data.get('nb_sessions'))
        failed = bool(res)
    except:
        logger.exception("Unable to get player %s", data)
        failed = True

    return JsonResponse({
        "result": res,
        "command": "get_player_profile",
        "arguments": data,
        "failed": failed
    })


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

    type_map = {
        "last_seen_from": parser.parse,
        "last_seen_till": parser.parse,
        "player_name": str, 
        "blacklisted": bool, 
        "steam_id_64": str,
        "page": int,
        "page_size": int
    }

    try:
        arguments = {}
        for k, v in data.items():
            if k not in type_map:
                continue
            arguments[k] = type_map[k](v)

        res = get_players_by_appearance(**arguments)
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


# This is were all the RCON commands are turned into HTTP endpoints
def wrap_method(func, parameters):
    @csrf_exempt
    @wraps(func)
    def wrapper(request):
        logger = logging.getLogger('rconweb')
        arguments = {}
        data = {}
        failure = False
        data = _get_data(request)
        logger.info("%s %s", func.__name__, data)

        for pname, param in parameters.items():
            if pname == 'by':
                # TODO: replace by account id when we have user layer
                arguments[pname] = get_client_ip(request)
            elif param.default != inspect._empty:
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


ctl = RecordedRcon(
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
        minutes = abs(int(request.GET.get('minutes')))
    except (ValueError, KeyError, TypeError):
        minutes = 180

    name = ctl.get_name()
    scoreboard = ctl.get_scoreboard(minutes, "ratio")
    text = make_table(scoreboard)
    scoreboard = ctl.get_scoreboard(minutes, "(real) kills")
    text2 = make_table(scoreboard)

    return HttpResponse(
        f'''<div>
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
        '''
    )

PREFIXES_TO_EXPOSE = [
    'get_', 'set_', 'do_'
]

commands = [
    ("player", get_player),
    ("players_history", players_history),
    ("blacklist_player", blacklist_player),
    ("unblacklist_player", unblacklist_player),
    ("scoreboard", text_scoreboard),
    ("get_auto_broadcasts_config", get_auto_broadcasts_config),
    ("set_auto_broadcasts_config", set_auto_broadcasts_config),
    ("clear_cache", clear_cache),
]

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
        continue

    commands.append(
        (name, wrap_method(func, inspect.signature(func).parameters))
    )

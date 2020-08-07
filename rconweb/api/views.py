import inspect
import logging
import json
import datetime
from functools import wraps
import os
from redis import StrictRedis

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
    get_player_profile,
    add_flag_to_player,
    remove_flag,
    banned_unblacklisted_players,
    unban_unblacklisted_players as pv_unban_unblacklisted_players
)
from rcon.user_config import AutoBroadcasts, WelcomeMessage, InvalidConfigurationError
from rcon.cache_utils import RedisCached, get_redis_pool
from .discord import send_to_discord_audit


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
def get_welcome_message_config(request):
    failed = False
    config = None

    try:
        welcome_settings = WelcomeMessage()
        config = {
            'on_map_change': welcome_settings.get_on_map_change(),
            'on_interval_switch': welcome_settings.get_on_interval_switch(),
            'on_interval_period': welcome_settings.get_on_interval_period(),
            'on_interval_unit': welcome_settings.get_on_interval_unit(),
            'welcome': welcome_settings.get_welcome()
        }
    except:
        logger.exception("Error fetching welcome message config")
        failed = True

    return JsonResponse({
        "result": config,
        "command": "get_welcome_message_config",
        "arguments": None,
        "failed": failed
    })

@csrf_exempt
def get_banned_unblacklisted_players(request):
    failed = False
    result = None

    ctl = RecordedRcon(
        SERVER_INFO
    )

    result = banned_unblacklisted_players(ctl)

    return JsonResponse({
        "result": result,
        "command": "get_banned_unblacklisted_players",
        "arguments": None,
        "failed": failed
    })

@csrf_exempt
def unban_unblacklisted_players(request):
    failed = False

    ctl = RecordedRcon(
        SERVER_INFO
    )

    result = pv_unban_unblacklisted_players(ctl)

    return JsonResponse({
        "result": result,
        "command": "unban_unblacklisted_players",
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
def set_welcome_message_config(request):
    failed = False
    res = None
    data = _get_data(request)
    welcome_settings = WelcomeMessage()
    config_keys = {
        'on_map_change': welcome_settings.set_on_map_change,
        'on_interval_switch': welcome_settings.set_on_interval_switch,
        'on_interval_period': welcome_settings.set_on_interval_period,
        'on_interval_unit': welcome_settings.set_on_interval_unit,
        'welcome': welcome_settings.set_welcome
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
        "command": "set_welcome_message_config",
        "arguments": data,
        "failed": failed
    })


@csrf_exempt
def get_player(request):
    data = _get_data(request)
    res = {}
    try:
        res = get_player_profile(data['steam_id_64'], nb_sessions=data.get('nb_sessions', 10))
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
def flag_player(request):
    data = _get_data(request)
    res = None
    try:
        player, flag = add_flag_to_player(steam_id_64=data['steam_id_64'], flag=data['flag'], comment=data.get('comment'))
        res = flag
        send_to_discord_audit(
            "Flagged '{}' '{}' with '{}' '{}'".format(
                data['steam_id_64'], 
                ' | '.join(n['name'] for n in player['names']),
                flag['flag'],
                data.get('comment', '')
            ), 
            get_client_ip(request)
        )
    except KeyError:
        logger.warning("Missing parameters")
        # TODO return 400
    except CommandFailedError:
        logger.exception("Failed to flag")
    return JsonResponse({
        "result": res,
        "command": "flag_player",
        "arguments": data,
        "failed": not res
    })
   
@csrf_exempt
def unflag_player(request):
    # Note is this really not restful
    data = _get_data(request)
    res = None
    try:
        player, flag = remove_flag(data['flag_id'])
        res = flag
        send_to_discord_audit("Remove flag '{}' from '{}'".format(
            flag['flag'], ' | '.join(n['name'] for n in player['names'])), get_client_ip(request))
    except KeyError:
        logger.warning("Missing parameters")
        # TODO return 400
    except CommandFailedError:
        logger.exception("Failed to remove flag")
    return JsonResponse({
        "result": res,
        "command": "flag_player",
        "arguments": data,
        "failed": not res
    })
   

@csrf_exempt
def blacklist_player(request):
    data = _get_data(request)
    res = {}
    try:
        ctl = RecordedRcon(
            SERVER_INFO
        )
        send_to_discord_audit("Blacklist '{}' for '{}'".format(data['steam_id_64'], data['reason']), get_client_ip(request))
        name = data['name'] if 'name' in data else None
        add_player_to_blacklist(data['steam_id_64'], data['reason'], name, ctl, True)
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
        ctl = RecordedRcon(
            SERVER_INFO
        )
        send_to_discord_audit("Unblacklist '{}' for ''".format(data['steam_id_64']), get_client_ip(request))
        remove_player_from_blacklist(data['steam_id_64'], ctl)
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


def audit(func_name, request, arguments):
    to_audit = [
        'do_',
        'set_',
        'switch'
    ]

    try:
        if any(func_name.startswith(s) for s in to_audit):
            send_to_discord_audit("{} {}".format(func_name, arguments), get_client_ip(request))
        else:
            logger.debug("%s is not set for audit", func_name)
    except:
        logger.exception("Can't send audit log")
        
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
            audit(func.__name__, request, arguments)
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
    ("get_welcome_message_config", get_welcome_message_config),
    ("set_welcome_message_config", set_welcome_message_config),
    ("clear_cache", clear_cache),
    ("flag_player", flag_player),
    ("unflag_player", unflag_player),
    ("get_banned_unblacklisted_players", get_banned_unblacklisted_players),
    ("unban_unblacklisted_players", unban_unblacklisted_players)
]

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE):
        continue

    commands.append(
        (name, wrap_method(func, inspect.signature(func).parameters))
    )

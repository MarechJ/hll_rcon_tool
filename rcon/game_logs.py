import logging

from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
import time
import sys

logger = logging.getLogger(__name__)

HOOKS = {
    'KILL': [],
    'TEAM KILL': [],
    'CONNECTED': [],
    'DISCONNECTED': [],
    'CHAT[Allies]': [],
    'CHAT[Axis]': []
}

def on_kill(func):
    HOOKS['KILL'].append(func)
    return func

def on_tk(func):
    HOOKS['TEAM KILL'].append(func)
    return func

def on_chat(func):
    HOOKS['CHAT[Allies]'].append(func)
    HOOKS['CHAT[Axis]'].append(func)
    return func

def on_chat_axis(func):
    HOOKS['CHAT[Axis]'].append(func)
    return func

def on_chat_allies(func):
    HOOKS['CHAT[Allies]'].append(func)
    return func

def on_connected(func):
    HOOKS['CONNECTED'].append(func)
    return func

def on_disconnected(func):
    HOOKS['DISCONNECTED'].append(func)
    return func

def event_loop(replay=False):
    rcon = Rcon(SERVER_INFO)
    last_run = 0
    processed = {}
    logger.info("Registered hooks: %s", HOOKS)
    replay_time = 2

    if replay:
        replay_time = 180

    while True:
        since = max(min((time.time() - last_run) / 60, replay_time), 2)
        struct_logs = rcon.get_structured_logs(int(since))
 
        for log in struct_logs['logs']:
            # Best effort to remove duplicates
            # We can't uniquely identify a log line because the HLL server only gives us a relative time
            # without giving us the server time...
            # The following algo assumes that within 1 minutes actions won't be repeated
            # This is obviously wrong as some things could be repeated, such as multiple players saying GG
            # within the same minute. Or even (more rarely) the same KILL combination
            # An alternative approach could be to use the timestamp_ms (our estimated time) with a rounding 
            # of 50ms or so, to compensate for the time lag between the server response and our time marking
            # + using redis to make sure we keep the filter accross restarts
            if f"{log['action']}{log['message']}" in processed or abs(int(log['relative_time_ms'])) >= 60000:
                #logger.debug("Skipping duplicate %s", f"{log['action']}{log['message']}")
                continue
            logger.debug("Processing %s", f"{log['action']}{log['message']}")
            try:
                hooks = HOOKS[log['action']]
            except KeyError:
                logger.error("%s is an unkown type. please update the hooks", log['action'])
            
            for hook in hooks:
                try:
                    logger.info("Triggered %s.%s on %s", hook.__module__, hook.__name__, log['raw'])
                    hook(rcon, log)
                except KeyboardInterrupt:
                    sys.exit(0)
                except Exception:
                    logger.exception("Hook '%s.%s' for '%s' returned an error",  hook.__module__, hook.__name__, log)

        processed = {
            f"{log['action']}{log['message']}": log['relative_time_ms'] 
            for log in struct_logs['logs']
            if abs(int(log['relative_time_ms'])) < 60000
        }

        last_run = time.time()
        time.sleep(10)
    
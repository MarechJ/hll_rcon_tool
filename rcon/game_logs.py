import logging

from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
import time

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

def event_loop():
    rcon = Rcon(SERVER_INFO)
    last_run = 0

    logger.info("Registered hooks: %s", HOOKS)
    while True:
        since = min(min(time.time() - last_run, 60) / 60, 180)
        struct_logs = rcon.get_structured_logs(int(since))
 
        for log in struct_logs['logs']:
            try:
                hooks = HOOKS[log['action']]
            except KeyError:
                logger.error("%s is an unkown type. please update the hooks", log['action'])
            
            for hook in hooks:
                try:
                    hook(rcon, log)
                except:
                    logger.exception("Hook '%s' for type '%s' returned an error", hook.__name__, log['action'])

        last_run = time.time()
        time.sleep(10)
    
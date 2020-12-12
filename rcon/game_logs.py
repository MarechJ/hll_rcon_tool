import logging
import time
import sys
import datetime

from rcon.map_recorder import ThreadMapRecorder
from rcon.extended_commands import Rcon
from rcon.cache_utils import get_redis_client
from rcon.utils import FixedLenList
from rcon.settings import SERVER_INFO
from rcon.commands import HLLServerError, CommandFailedError

logger = logging.getLogger(__name__)

HOOKS = {
    "KILL": [],
    "TEAM KILL": [],
    "CONNECTED": [],
    "DISCONNECTED": [],
    "CHAT[Allies]": [],
    "CHAT[Axis]": [],
    "CHAT": [],
}


def on_kill(func):
    HOOKS["KILL"].append(func)
    return func


def on_tk(func):
    HOOKS["TEAM KILL"].append(func)
    return func


def on_chat(func):
    HOOKS["CHAT"].append(func)
    return func


def on_chat_axis(func):
    HOOKS["CHAT[Axis]"].append(func)
    return func


def on_chat_allies(func):
    HOOKS["CHAT[Allies]"].append(func)
    return func


def on_connected(func):
    HOOKS["CONNECTED"].append(func)
    return func


def on_disconnected(func):
    HOOKS["DISCONNECTED"].append(func)
    return func


MAX_FAILS = 10


class ChatLoop:
    log_history_key = "log_history"

    def __init__(self):
        self.rcon = Rcon(SERVER_INFO)
        self.rcon_2 = Rcon(SERVER_INFO)
        self.red = get_redis_client()
        self.duplicate_guard_key = "unique_logs"
        self.log_history = self.get_log_history_list()
        logger.info("Registered hooks: %s", HOOKS)

    @staticmethod
    def get_log_history_list():
        return FixedLenList(key=ChatLoop.log_history_key, max_len=100000)

    def run(self, loop_frequency_secs=10, cleanup_frequency_minutes=10):
        since_min = 180
        self.cleanup()
        last_cleanup_time = datetime.datetime.now()

        while True:
            logs = self.rcon.get_structured_logs(since_min_ago=since_min)
            since_min = 10
            for log in reversed(logs["logs"]):
                l = self.record_line(log)
                if l:
                    self.process_hooks(l)
            if (
                datetime.datetime.now() - last_cleanup_time
            ).total_seconds() >= cleanup_frequency_minutes * 60:
                self.cleanup()
                last_cleanup_time = datetime.datetime.now()

            time.sleep(loop_frequency_secs)

    def record_line(self, log):
        id_ = f"{log['timestamp_ms']}|{log['line_without_time']}"
        if not self.red.sadd(self.duplicate_guard_key, id_):
            logger.debug("Skipping duplicate: %s", id_)
            return None

        logger.info("Recording: %s", id_)
        self.log_history.add(log)
        return log

    def cleanup(self):
        logger.info("Starting cleanup")
        for k in self.red.sscan_iter(self.duplicate_guard_key):
            try:
                ts, _ = k.decode().split("|", 1)
            except ValueError:
                logger.exception("Invalid key %s", k)
                continue
            t = datetime.datetime.fromtimestamp(int(ts) / 1000)
            if (datetime.datetime.now() - t).total_seconds() > 180 * 60:
                logger.debug("Older than 180min, removing: %s", k)
                self.red.srem(self.duplicate_guard_key, k)
        logger.info("Cleanup done")
            
    def process_hooks(self, log):
        logger.debug("Processing %s", f"{log['action']}{log['message']}")
        hooks = []
        for action_hook, funcs in HOOKS.items():
            if log['action'].startswith(action_hook):
                hooks += funcs
        for hook in hooks:
            try:
                logger.info("Triggered %s.%s on %s", hook.__module__, hook.__name__, log['raw'])
                hook(self.rcon_2, log)
            except KeyboardInterrupt:
                sys.exit(0)
                raise
            except Exception:
                logger.exception("Hook '%s.%s' for '%s' returned an error",  hook.__module__, hook.__name__, log)


def event_loop(replay=False):
    rcon = Rcon(SERVER_INFO)
    last_run = 0
    processed = {}
    logger.info("Registered hooks: %s", HOOKS)
    replay_time = 10  # TODO store last runtime in redis
    max_fails = MAX_FAILS

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
            if f"{log['action']}{log['message']}" in processed:
                logger.debug("Skipping duplicate %s", f"{log['action']}{log['message']}")
                continue
            logger.debug("Processing %s", f"{log['action']}{log['message']}")
            hooks = []
            for action_hook, funcs in HOOKS.items():
                if log['action'].startswith(action_hook):
                    hooks += funcs
            
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
        time.sleep(15)
    
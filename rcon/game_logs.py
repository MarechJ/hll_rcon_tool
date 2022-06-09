import datetime
import logging
import os
import sys
import time
import unicodedata
from logging import config

from sqlalchemy import and_, desc, or_
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.sql.expression import false, true

from rcon.cache_utils import get_redis_client
from rcon.commands import CommandFailedError, HLLServerError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.extended_commands import LOG_ACTIONS, Rcon
from rcon.models import LogLine, PlayerName, PlayerSteamID, enter_session
from rcon.player_history import (add_player_to_blacklist, get_player_profile,
                                 player_has_flag)
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.utils import FixedLenList

logger = logging.getLogger(__name__)

HOOKS = {
    "TEAM KILL": [],
    "CONNECTED": [],
    "DISCONNECTED": [],
    "CHAT[Allies]": [],
    "CHAT[Axis]": [],
    "CHAT": [],
    "KILL": [],
    "CAMERA": [],
    "TK": [],
    "MATCH": [],
    "MATCH START": [],
    "MATCH ENDED": []
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

def on_camera(func):
    HOOKS["CAMERA"].append(func)
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


class LogLoop:
    log_history_key = "log_history"

    def __init__(self):
        self.rcon = Rcon(SERVER_INFO)
        self.rcon_2 = RecordedRcon(SERVER_INFO)
        self.red = get_redis_client()
        self.duplicate_guard_key = "unique_logs"
        self.log_history = self.get_log_history_list()
        logger.info("Registered hooks: %s", HOOKS)

    @staticmethod
    def get_log_history_list():
        return FixedLenList(key=LogLoop.log_history_key, max_len=100000)

    def run(self, loop_frequency_secs=2, cleanup_frequency_minutes=10):
        since_min = 180
        self.cleanup()
        last_cleanup_time = datetime.datetime.now()

        while True:
            logs = self.rcon.get_structured_logs(since_min_ago=since_min)
            since_min = 5
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
            # logger.debug("Skipping duplicate: %s", id_)
            return None

        logger.info("Caching line: %s", id_)
        try:
            last_line = self.log_history[0]
        except IndexError:
            last_line = None
        if not isinstance(last_line, dict):
            logger.error("Can't check against last_line, invalid_format %s", last_line)
        elif last_line and last_line["timestamp_ms"] > log["timestamp_ms"]:
            logger.error("Received old log record, ignoring")
            return None

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
            if (datetime.datetime.now() - t).total_seconds() > 280 * 60:
                logger.debug("Older than 180min, removing: %s", k)
                self.red.srem(self.duplicate_guard_key, k)
        logger.info("Cleanup done")

    def process_hooks(self, log):
        logger.debug("Processing %s", f"{log['action']}{log['message']}")
        hooks = []
        for action_hook, funcs in HOOKS.items():
            if log["action"].startswith(action_hook):
                hooks += funcs
        for hook in hooks:
            try:
                logger.info(
                    "Triggered %s.%s on %s", hook.__module__, hook.__name__, log["raw"]
                )
                hook(self.rcon_2, log)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception:
                logger.exception(
                    "Hook '%s.%s' for '%s' returned an error",
                    hook.__module__,
                    hook.__name__,
                    log,
                )


class LogRecorder:
    def __init__(self, dump_frequency_min=5, run_immediately=False):
        self.dump_frequency_min = dump_frequency_min
        self.run_immediately = run_immediately
        self.server_id = os.getenv("SERVER_NUMBER")
        if not self.server_id:
            raise ValueError("SERVER_NUMBER is not set, can't record logs")

    def _get_new_logs(self, sess):
        to_store = []
        last_log = (
            sess.query(LogLine)
            .filter(LogLine.server == self.server_id)
            .order_by(desc(LogLine.event_time))
            .limit(1)
            .one_or_none()
        )
        logger.info("Getting new logs from %s", last_log.event_time if last_log else 0)
        for log in LogLoop.get_log_history_list():
            if not isinstance(log, dict):
                logger.warning("Log is invalid, not a dict: %s", log)
                continue
            if (
                not last_log
                or int(log["timestamp_ms"]) / 1000 > last_log.event_time.timestamp()
            ):
                to_store.append(log)
            if (
                last_log
                and not int(log["timestamp_ms"]) / 1000
                == last_log.event_time.timestamp()
                and last_log.raw == log["raw"]
            ):
                logger.info("New logs collection at: %s", log)
                return to_store
        return to_store

    def _get_steamid_record(self, sess, steam_id_64):
        if not steam_id_64:
            return None
        return (
            sess.query(PlayerSteamID)
            .filter(PlayerSteamID.steam_id_64 == steam_id_64)
            .one_or_none()
        )

    def _save_logs(self, sess, to_store):
        for log in to_store:
            steamid_1 = self._get_steamid_record(sess, log["steam_id_64_1"])
            steamid_2 = self._get_steamid_record(sess, log["steam_id_64_2"])
            try:
                sess.add(
                    LogLine(
                        event_time=datetime.datetime.fromtimestamp(
                            log["timestamp_ms"] // 1000
                        ),
                        type=log["action"],
                        player1_name=log["player"],
                        player2_name=log["player2"],
                        steamid1=steamid_1,
                        steamid2=steamid_2,
                        raw=log["raw"],
                        content=log["message"],
                        server=os.getenv("SERVER_NUMBER"),
                    )
                )
                sess.commit()
            except IntegrityError:
                sess.rollback()
                logger.exception("Unable to recorder %s", log)

    def run(self):
        last_run = datetime.datetime.now()
        if self.run_immediately:
            last_run = last_run - datetime.timedelta(minutes=self.dump_frequency_min)

        while True:
            now = datetime.datetime.now()
            if not (now - last_run).total_seconds() > self.dump_frequency_min * 60:
                logger.debug("Not due for recording yet")
                time.sleep(30)
                continue
            with enter_session() as sess:
                to_store = self._get_new_logs(sess)
                logger.info("%s log lines to record", len(to_store))

                self._save_logs(sess, to_store)

                last_run = datetime.datetime.now()


def is_player(search_str, player, exact_match=False):
    if exact_match:
        return search_str == player

    if not player or not search_str:
        return None

    if search_str.lower() in player.lower():
        return True

    normalize_search = (
        unicodedata.normalize("NFD", search_str)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )
    normalize_player = (
        unicodedata.normalize("NFD", player).encode("ascii", "ignore").decode("utf-8")
    )

    if normalize_search in normalize_player:
        return True

    return False


def is_action(action_filter, action, exact_match=False):
    if not action_filter or not action:
        return None
    if not isinstance(action_filter, list):
        action_filter = [action_filter]

    for filter_ in action_filter:
        if not exact_match:
            if action.lower().startswith(filter_.lower()):
                return True
        elif filter_ == action:
            return True

    return False


def get_recent_logs(
    start=0,
    end=100000,
    player_search=None,
    action_filter=None,
    min_timestamp=None,
    exact_player_match=False,
    exact_action=False,
):
    log_list = LogLoop.get_log_history_list()
    all_logs = log_list
    if start != 0:
        all_logs = log_list[start : min(end, len(log_list))]
    logs = []
    all_players = set()
    actions = set(
        LOG_ACTIONS
    )
    if player_search and not isinstance(player_search, list):
        player_search = [player_search]
    # flatten that shit
    for idx, l in enumerate(all_logs):
        if idx >= end - start:
            break
        if not isinstance(l, dict):
            continue
        if min_timestamp and l["timestamp_ms"] / 1000 < min_timestamp:
            logger.debug("Stopping log read due to old timestamp at index %s", idx)
            break
        if player_search:
            for player_name_search in player_search:
                if is_player(player_name_search, l["player"], exact_player_match) or is_player(
                    player_name_search, l["player2"], exact_player_match
                ):
                    
                    if action_filter and not is_action(action_filter, l["action"], exact_action):
                        continue
                    logs.append(l)
                    break
        elif action_filter and is_action(action_filter, l["action"], exact_action):
            logs.append(l)
        elif not player_search and not action_filter:
            logs.append(l)
        if p1 := l["player"]:
            all_players.add(p1)
        if p2 := l["player2"]:
            all_players.add(p2)
        actions.add(l["action"])

    return {
        "actions": list(actions),
        "players": list(all_players),
        "logs": logs,
    }


def is_player_death(player, log):
    return log["action"] == "KILL" and player == log["player2"]


def is_player_kill(player, log):
    return log["action"] == "KILL" and player == log["player"]


@on_tk
def auto_ban_if_tks_right_after_connection(rcon: RecordedRcon, log):
    config = get_config()
    config = config.get("BAN_TK_ON_CONNECT")
    if not config or not config.get("enabled"):
        return

    player_name = log["player"]
    player_steam_id = log["steam_id_64_1"]
    player_profile = None
    vips = {}
    try:
        player_profile = get_player_profile(player_steam_id, 0)
    except:
        logger.exception("Unable to get player profile")
    try:
        vips = set(v["steam_id_64"] for v in rcon.get_vip_ids())
    except:
        logger.exception("Unable to get VIPS")

    last_logs = get_recent_logs(
        end=500, player_search=player_name, exact_player_match=True
    )
    logger.debug("Checking TK from %s", player_name)
    author = config.get("author_name", "Automation")
    reason = config.get("message", "No reasons provided")
    discord_msg = config.get("discord_webhook_message", "No message provided")
    webhook = config.get("discord_webhook_url")
    max_time_minute = config.get("max_time_after_connect_minutes", 5)
    excluded_weapons = [w.lower() for w in config.get("exclude_weapons", [])]
    ignore_after_kill = config.get("ignore_tk_after_n_kills", 1)
    ignore_after_death = config.get("ignore_tk_after_n_death", 1)
    whitelist_players = config.get("whitelist_players", {})
    tk_tolerance_count = config.get("teamkill_tolerance_count", 1)

    if player_profile:
        if whitelist_players.get("is_vip") and player_steam_id in vips:
            logger.debug("Not checking player because he's VIP")
            return

        if whitelist_players.get("has_at_least_n_sessions") and player_profile[
            "sessions_count"
        ] >= whitelist_players.get("has_at_least_n_sessions"):
            logger.debug(
                "Not checking player because he has %s sessions",
                player_profile["sessions_count"],
            )
            return

        flags = whitelist_players.get("has_flag", [])
        if not isinstance(flags, list):
            flags = [flags]

        for f in flags:
            if player_has_flag(player_profile, f):
                logger.debug("Not checking player because he has flag %s", f)
                return

    last_action_is_connect = False
    last_connect_time = None
    kill_counter = 0
    death_counter = 0
    tk_counter = 0
    for log in reversed(last_logs["logs"]):
        logger.debug(log)

        if log["action"] == "CONNECTED":
            last_action_is_connect = log
            last_connect_time = log["timestamp_ms"]
            kill_counter = 0
            death_counter = 0
            continue
        if (
            log["action"] == "TEAM KILL"
            and log["player"] == player_name
            and last_action_is_connect
        ):
            if excluded_weapons and log["weapon"].lower() in excluded_weapons:
                logger.debug("Not counting TK as offense due to weapon exclusion")
                continue
            if log["timestamp_ms"] - last_connect_time > max_time_minute * 60 * 1000:
                logger.debug(
                    "Not counting TK as offense due to elapsed time exclusion, last connection time %s, tk time %s",
                    datetime.datetime.fromtimestamp(last_connect_time / 1000),
                    datetime.datetime.fromtimestamp(log["timestamp_ms"]),
                )
                continue
            
            tk_counter += 1
            if tk_counter > tk_tolerance_count:
                logger.info("Banning player %s for TEAMKILL after connect %s", player_name, log)
                try:
                    rcon.do_perma_ban(
                        player=player_name,
                        reason=reason,
                        by=author,
                    )
                except:
                    logger.exception("Can't perma, trying blacklist")
                    add_player_to_blacklist(player_steam_id, reason, by=author)
                logger.info("Banned player %s for TEAMKILL after connect %s", player_name, log)
                send_to_discord_audit(discord_msg.format(player=player_name), by=author, webhookurl=webhook)
        elif is_player_death(player_name, log):
            death_counter += 1
            if death_counter >= ignore_after_death:
                last_action_is_connect = False
        elif is_player_kill(player_name, log):
            kill_counter += 1
            if kill_counter >= ignore_after_kill:
                last_action_is_connect = False


def get_historical_logs_records(
    sess,
    player_name=None,
    action=None,
    steam_id_64=None,
    limit=1000,
    from_=None,
    till=None,
    time_sort="desc",
    exact_player_match=False,
    exact_action=True,
    server_filter=None,
):
    names = []
    name_filters = []

    q = sess.query(LogLine)
    if action and not exact_action:
        q = q.filter(LogLine.type.ilike(f"%{action}%"))
    elif action and exact_action:
        q = q.filter(LogLine.type == action)

    time_filter = []
    if from_:
        time_filter.append(LogLine.event_time >= from_)

    if till:
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

    if server_filter:
        q = q.filter(LogLine.server == server_filter)

    if time_sort:
        q = q.order_by(
            LogLine.event_time.desc()
            if time_sort == "desc"
            else LogLine.event_time.asc()
        ).limit(limit)

    return q.all()


def get_historical_logs(
    player_name=None,
    action=None,
    steam_id_64=None,
    limit=1000,
    from_=None,
    till=None,
    time_sort="desc",
    exact_player_match=False,
    exact_action=True,
    server_filter=None,
    output=None
):
    with enter_session() as sess:
        res = get_historical_logs_records(
            sess,
            player_name,
            action,
            steam_id_64,
            limit,
            from_,
            till,
            time_sort,
            exact_player_match,
            exact_action,
            server_filter,
        )
        lines = []
        for r in res:
            r = r.to_dict()
            if output != "CSV" and output != "csv":
                r["event_time"] = r["event_time"].timestamp()
            else:
                del r["id"]
                del r["version"]
                del r["creation_time"]
                del r["raw"]
            lines.append(r)
        return lines

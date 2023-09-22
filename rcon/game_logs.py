import datetime
import logging
import os
import re
import sys
import time
import unicodedata
from collections import defaultdict
from functools import partial
from typing import Callable, DefaultDict, Dict, Iterable, List

import discord
from sqlalchemy import and_, desc, or_
from sqlalchemy.exc import IntegrityError

from rcon.cache_utils import get_redis_client, ttl_cache
from rcon.models import LogLine, PlayerSteamID, enter_session
from rcon.player_history import (
    add_player_to_blacklist,
    get_player_profile,
    player_has_flag,
)
from rcon.rcon_ import LOG_ACTIONS, Rcon
from rcon.rcon_discord import make_hook, send_to_discord_audit
from rcon.settings import SERVER_INFO
from rcon.typedefs import (
    GetDetailedPlayer,
    ParsedLogsType,
    PlayerStat,
    StructuredLogLineWithMetaData,
)
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.log_line_webhooks import (
    DiscordMentionWebhook,
    LogLineWebhookUserConfig,
)
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.utils import FixedLenList, MapsHistory

logger = logging.getLogger(__name__)

HOOKS: Dict[str, set[Callable]] = {
    "TEAM KILL": set(),
    "CONNECTED": set(),
    "DISCONNECTED": set(),
    "TK": set(),
    "TK AUTO": set(),
    "TK AUTO BANNED": set(),
    "TK AUTO KICKED": set(),
    "ADMIN BANNED": set(),
    "ADMIN KICKED": set(),
    "CAMERA": set(),
    "CHAT": set(),
    "CHAT[Allies]": set(),
    "CHAT[Allies][Team]": set(),
    "CHAT[Allies][Unit]": set(),
    "CHAT[Axis]": set(),
    "CHAT[Axis][Team]": set(),
    "CHAT[Axis][Unit]": set(),
    "KILL": set(),
    "MATCH START": set(),
    "MATCH ENDED": set(),
    "MATCH": set(),
    "TEAMSWITCH": set(),
    "VOTE": set(),
    "VOTE STARTED": set(),
    "VOTE COMPLETED": set(),
}


def on_kill(func):
    HOOKS["KILL"].add(func)
    return func


def on_tk(func):
    HOOKS["TEAM KILL"].add(func)
    return func


def on_chat(func):
    HOOKS["CHAT"].add(func)
    return func


def on_camera(func):
    HOOKS["CAMERA"].add(func)
    return func


def on_chat_axis(func):
    HOOKS["CHAT[Axis]"].add(func)
    return func


def on_chat_allies(func):
    HOOKS["CHAT[Allies]"].add(func)
    return func


def on_connected(func):
    HOOKS["CONNECTED"].add(func)
    return func


def on_disconnected(func):
    HOOKS["DISCONNECTED"].add(func)
    return func


def on_match_start(func):
    HOOKS["MATCH START"].add(func)
    return func


def on_match_end(func):
    HOOKS["MATCH ENDED"].add(func)
    return func


def on_generic(key, func) -> Callable:
    """Dynamically register hooks from config.yml LOG_LINE_WEBHOOKS"""
    HOOKS[key].add(func)
    return func


def make_allowed_mentions(mentions: Iterable[str]) -> discord.AllowedMentions:
    """Convert the provided sequence of users and roles to a discord.AllowedMentions

    Similar to discord_chat.make_allowed_mentions but doesn't strip @everyone/@here
    """
    allowed_mentions: DefaultDict[str, List[discord.Object]] = defaultdict(list)

    for role_or_user in mentions:
        if match := re.match(r"<@(\d+)>", role_or_user):
            allowed_mentions["users"].append(discord.Object(int(match.group(1))))
        if match := re.match(r"<@&(\d+)>", role_or_user):
            allowed_mentions["roles"].append(discord.Object(int(match.group(1))))

    return discord.AllowedMentions(
        users=allowed_mentions["users"], roles=allowed_mentions["roles"]
    )


def send_log_line_webhook_message(
    webhooks: list[DiscordMentionWebhook],
    _,
    log_line: Dict[str, str | int | float | None],
) -> None:
    """Send a time stammped embed of the log_line and mentions to the provided Discord Webhook"""

    config = RconServerSettingsUserConfig.load_from_db()

    for hook in webhooks:
        mentions = hook.user_mentions + hook.role_mentions
        webhook = make_hook(hook.url)
        allowed_mentions = make_allowed_mentions(mentions)

        content = " ".join(mentions)
        description = log_line["line_without_time"]
        embed = discord.Embed(
            description=description,
            timestamp=datetime.datetime.utcfromtimestamp(
                log_line["timestamp_ms"] / 1000
            ),
        )
        embed.set_footer(text=config.short_name)
        webhook.send(content=content, embed=embed, allowed_mentions=allowed_mentions)


@ttl_cache(ttl=60 * 5)
def load_generic_hooks():
    """Load and validate all the subscribed log line webhooks from config.yml"""
    try:
        config = LogLineWebhookUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        logger.error("Error when loading settings")
        return

    for conf in config.log_types:
        # mentions = [h.user_mentions + h.role_mentions for h in conf.webhooks]
        func = partial(send_log_line_webhook_message, conf.webhooks)

        # Have to set these attributes as the're used in LogLoop.process_hooks()
        func.__name__ = send_log_line_webhook_message.__name__
        func.__module__ = __name__

        on_generic(conf.log_type.value, func)


MAX_FAILS = 10


class LogLoop:
    log_history_key = "log_history"

    def __init__(self):
        self.rcon = Rcon(SERVER_INFO)
        self.red = get_redis_client()
        self.duplicate_guard_key = "unique_logs"
        self.log_history = self.get_log_history_list()

        logger.info("Registered hooks: %s", HOOKS)

    @staticmethod
    def get_log_history_list() -> FixedLenList:
        return FixedLenList(key=LogLoop.log_history_key, max_len=100000)

    def run(self, loop_frequency_secs=2, cleanup_frequency_minutes=10):
        since_min = 180
        self.cleanup()
        last_cleanup_time = datetime.datetime.now()

        while True:
            load_generic_hooks()
            logs: ParsedLogsType = self.rcon.get_structured_logs(
                since_min_ago=since_min
            )
            since_min = 5
            for log in reversed(logs["logs"]):
                line = self.record_line(log)
                if line:
                    self.process_hooks(line)
            if (
                datetime.datetime.now() - last_cleanup_time
            ).total_seconds() >= cleanup_frequency_minutes * 60:
                self.cleanup()
                last_cleanup_time = datetime.datetime.now()

            dp = self.rcon.get_detailed_players()
            if dp["fail_count"] > 0:
                logger.warning(
                    "Could not fetch all player stats. "
                    + str(dp["fail_count"])
                    + " players failed."
                )
            self.record_player_stats(dp["players"])

            time.sleep(loop_frequency_secs)

    def record_player_stats(self, players: dict[str, GetDetailedPlayer]):
        maps = MapsHistory()
        if len(maps) == 0:
            logger.info("No map seems to be running, skipping saving stats")
            return
        m = maps[0]
        # give us and the gameserver some time after map switch to zero out scores.
        # No clue, why this is actually needed, tbh, but without it, it seems that score values
        # from the previous map may leak into the current one
        if m["start"] > datetime.datetime.now().timestamp() - 30:
            return
        for steam_id in players:
            player = players.get(steam_id)
            map_players = m.setdefault("player_stats", dict())
            p = map_players.get(
                steam_id,
                PlayerStat(
                    combat=player["combat"],
                    offense=player["offense"],
                    defense=player["defense"],
                    support=player["support"],
                ),
            )
            for stat in ["combat", "offense", "defense", "support"]:
                if player[stat] > p[stat]:
                    p[stat] = player[stat]
            map_players[steam_id] = p
        maps.update(0, m)

    def record_line(self, log: StructuredLogLineWithMetaData):
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

    def process_hooks(self, log: StructuredLogLineWithMetaData):
        logger.debug("Processing %s", f"{log['action']}{log['message']}")
        hooks = []
        started_total = time.time()
        for action_hook, funcs in HOOKS.items():
            if log["action"].startswith(action_hook):
                hooks += funcs

        for hook in hooks:
            try:
                logger.info(
                    "Triggered %s.%s on %s", hook.__module__, hook.__name__, log["raw"]
                )
                started = time.time()
                hook(self.rcon, log)
                logger.debug(
                    "Ran in %.4f seconds %s.%s on %s",
                    time.time() - started,
                    hook.__module__,
                    hook.__name__,
                    log["raw"],
                )
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                logger.exception(
                    f"Hook '{hook.__module__}.{hook.__name__}' for '{log}' returned an error: {e}"
                )
        logger.debug(
            "Processed %s hooks in %.4f for: %s",
            len(hooks),
            time.time() - started_total,
            f"{log['action']}{log['message']}",
        )


class LogRecorder:
    def __init__(self, dump_frequency_min=5, run_immediately=False):
        self.dump_frequency_min = dump_frequency_min
        self.run_immediately = run_immediately
        self.server_id = os.getenv("SERVER_NUMBER")
        if not self.server_id:
            raise ValueError("SERVER_NUMBER is not set, can't record logs")

    def _get_new_logs(self, sess):
        to_store: list[StructuredLogLineWithMetaData] = []
        last_log = (
            sess.query(LogLine)
            .filter(LogLine.server == self.server_id)
            .order_by(desc(LogLine.event_time))
            .limit(1)
            .one_or_none()
        )
        logger.info("Getting new logs from %s", last_log.event_time if last_log else 0)
        log: StructuredLogLineWithMetaData
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

    def _save_logs(self, sess, to_store: list[StructuredLogLineWithMetaData]):
        for log in to_store:
            steamid_1 = self._get_steamid_record(sess, log["steam_id_64_1"])
            steamid_2 = self._get_steamid_record(sess, log["steam_id_64_2"])
            try:
                sess.add(
                    LogLine(
                        version=log["version"],
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
                        weapon=log["weapon"],
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
    """Test whether the passed in log line `action` is in `action_filter`."""
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
    inclusive_filter=True,
) -> ParsedLogsType:
    # The default behavior is to only show log lines with actions in `actions_filter`
    # inclusive_filter=True retains this default behavior
    # inclusive_filter=False will do the opposite, show all lines except what is passed in
    # `actions_filter`
    log_list = LogLoop.get_log_history_list()
    all_logs = log_list
    if start != 0:
        all_logs = log_list[start : min(end, len(log_list))]
    logs: list[StructuredLogLineWithMetaData] = []
    all_players = set()
    actions = set(LOG_ACTIONS)
    if player_search and not isinstance(player_search, list):
        player_search = [player_search]
    # flatten that shit
    line: StructuredLogLineWithMetaData
    for idx, line in enumerate(all_logs):
        if idx >= end - start:
            break
        if not isinstance(line, dict):
            continue
        if min_timestamp and line["timestamp_ms"] / 1000 < min_timestamp:
            logger.debug("Stopping log read due to old timestamp at index %s", idx)
            break
        if player_search:
            for player_name_search in player_search:
                if is_player(
                    player_name_search, line["player"], exact_player_match
                ) or is_player(player_name_search, line["player2"], exact_player_match):
                    # Filter out anything that isn't in action_filter
                    if (
                        action_filter
                        and inclusive_filter
                        and is_action(action_filter, line["action"], exact_action)
                    ):
                        logs.append(line)
                        break
                    # Filter out any action in action_filter
                    elif (
                        action_filter
                        and not inclusive_filter
                        and not is_action(action_filter, line["action"], exact_action)
                    ):
                        logs.append(line)
                        break
                    # Handle action_filter being empty
                    elif not action_filter:
                        logs.append(line)
                        break
        elif action_filter:
            # Filter out anything that isn't in action_filter
            if inclusive_filter and is_action(
                action_filter, line["action"], exact_action
            ):
                logs.append(line)
            # Filter out any action in action_filter
            elif not inclusive_filter and not is_action(
                action_filter, line["action"], exact_action
            ):
                logs.append(line)
        elif not player_search and not action_filter:
            logs.append(line)

        if p1 := line["player"]:
            all_players.add(p1)
        if p2 := line["player2"]:
            all_players.add(p2)
        actions.add(line["action"])

    return {
        "actions": sorted(list(actions)),
        "players": list(all_players),
        "logs": logs,
    }


def is_player_death(player, log):
    return log["action"] == "KILL" and player == log["player2"]


def is_player_kill(player, log):
    return log["action"] == "KILL" and player == log["player"]


@on_tk
def auto_ban_if_tks_right_after_connection(
    rcon: Rcon,
    log: StructuredLogLineWithMetaData,
    config: BanTeamKillOnConnectUserConfig | None = None,
):
    if config is None:
        config = BanTeamKillOnConnectUserConfig.load_from_db()
    if not config or not config.enabled:
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
    author = config.author_name
    reason = config.message
    discord_msg = config.discord_webhook_message
    webhook = config.discord_webhook_url
    max_time_minute = config.max_time_after_connect_minutes
    excluded_weapons = [w.lower() for w in config.excluded_weapons]
    ignore_after_kill = config.ignore_tk_after_n_kills
    ignore_after_death = config.ignore_tk_after_n_deaths
    whitelist_players = config.whitelist_players
    tk_tolerance_count = config.teamkill_tolerance_count

    if player_profile:
        if whitelist_players.is_vip and player_steam_id in vips:
            logger.debug("Not checking player because he's VIP")
            return

        if (
            player_profile["sessions_count"]
            >= whitelist_players.has_at_least_n_sessions
        ):
            logger.debug(
                "Not checking player because he has %s sessions",
                player_profile["sessions_count"],
            )
            return

        for f in whitelist_players.has_flag:
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
                    datetime.datetime.fromtimestamp(log["timestamp_ms"] / 1000),
                )
                continue

            tk_counter += 1
            if tk_counter > tk_tolerance_count:
                logger.info(
                    "Banning player %s for TEAMKILL after connect %s", player_name, log
                )
                try:
                    rcon.do_perma_ban(
                        steam_id_64=player_steam_id,
                        reason=reason,
                        by=author,
                    )
                except:
                    logger.exception("Can't perma, trying blacklist")
                    add_player_to_blacklist(player_steam_id, reason, by=author)
                logger.info(
                    "Banned player %s for TEAMKILL after connect %s", player_name, log
                )
                send_to_discord_audit(
                    discord_msg.format(player=player_name),
                    by=author,
                    webhookurls=[webhook],
                )
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
    output=None,
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

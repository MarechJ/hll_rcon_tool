import datetime
import logging
import re
import sys
import time
from collections import defaultdict
from functools import partial
from typing import Callable, Dict, Iterable, DefaultDict

import discord_webhook
from discord.utils import escape_markdown

from rcon.cache_utils import get_redis_client, ttl_cache
from rcon.discord import make_hook
from rcon.rcon import get_rcon
from rcon.types import AllLogTypes, ParsedLogsType, GetDetailedPlayer, StructuredLogLineWithMetaData, PlayerStat
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import DiscordMentionWebhook
from rcon.utils import FixedLenList, MapsHistory

logger = logging.getLogger(__name__)

HOOKS: Dict[str, list[Callable]] = {
    AllLogTypes.admin.value: [],
    AllLogTypes.admin_anti_cheat.value: [],
    AllLogTypes.admin_banned.value: [],
    AllLogTypes.admin_idle.value: [],
    AllLogTypes.admin_kicked.value: [],
    AllLogTypes.admin_misc.value: [],
    AllLogTypes.admin_perma_banned.value: [],
    AllLogTypes.allies_chat.value: [],
    AllLogTypes.allies_team_chat.value: [],
    AllLogTypes.allies_unit_chat.value: [],
    AllLogTypes.axis_chat.value: [],
    AllLogTypes.axis_team_chat.value: [],
    AllLogTypes.axis_unit_chat.value: [],
    AllLogTypes.camera.value: [],
    AllLogTypes.chat.value: [],
    AllLogTypes.connected.value: [],
    AllLogTypes.disconnected.value: [],
    AllLogTypes.kill.value: [],
    AllLogTypes.match.value: [],
    AllLogTypes.match_end.value: [],
    AllLogTypes.match_start.value: [],
    AllLogTypes.team_kill.value: [],
    AllLogTypes.team_switch.value: [],
    AllLogTypes.tk.value: [],
    AllLogTypes.tk_auto.value: [],
    AllLogTypes.tk_auto_banned.value: [],
    AllLogTypes.tk_auto_kicked.value: [],
    AllLogTypes.vote.value: [],
    AllLogTypes.vote_completed.value: [],
    AllLogTypes.vote_expired.value: [],
    AllLogTypes.vote_passed.value: [],
    AllLogTypes.vote_started.value: [],
}


def on_kill(func):
    HOOKS[AllLogTypes.kill.value].append(func)
    return func


def on_tk(func):
    HOOKS[AllLogTypes.team_kill.value].append(func)
    return func


def on_chat(func):
    HOOKS[AllLogTypes.chat.value].append(func)
    HOOKS[AllLogTypes.axis_chat.value].append(func)
    HOOKS[AllLogTypes.axis_team_chat.value].append(func)
    HOOKS[AllLogTypes.axis_unit_chat.value].append(func)
    HOOKS[AllLogTypes.allies_chat.value].append(func)
    HOOKS[AllLogTypes.allies_team_chat.value].append(func)
    HOOKS[AllLogTypes.allies_unit_chat.value].append(func)
    return func


def on_camera(func):
    HOOKS[AllLogTypes.camera.value].append(func)
    return func


def on_chat_axis(func):
    HOOKS[AllLogTypes.axis_chat.value].append(func)
    HOOKS[AllLogTypes.axis_team_chat.value].append(func)
    HOOKS[AllLogTypes.axis_unit_chat.value].append(func)
    return func


def on_chat_allies(func):
    HOOKS[AllLogTypes.allies_chat.value].append(func)
    HOOKS[AllLogTypes.allies_team_chat.value].append(func)
    HOOKS[AllLogTypes.allies_unit_chat.value].append(func)
    return func


def on_connected(insert_at: int | None = None):
    """Insert the given hook at `insert_at` position, or the end"""

    def wrapper(func):
        if isinstance(insert_at, int):
            HOOKS[AllLogTypes.connected.value].insert(insert_at, func)
        else:
            HOOKS[AllLogTypes.connected.value].append(func)

        return func

    return wrapper


def on_disconnected(func):
    HOOKS[AllLogTypes.disconnected.value].append(func)
    return func


def on_match_start(func):
    HOOKS[AllLogTypes.match_start.value].append(func)
    return func


def on_match_end(func):
    HOOKS[AllLogTypes.match_end.value].append(func)
    return func


def on_generic(key, func) -> Callable:
    """Dynamically register hooks from config.yml LOG_LINE_WEBHOOKS"""

    # equality comparison for partial functions does not work since each newly created object has a different id
    # we have to directly compare the function and arguments to avoid duplicates
    for f in HOOKS[key]:
        if (
                isinstance(f, partial)
                and f.func == func.func
                and f.args == func.args
                and f.keywords == func.keywords
        ):
            logger.info("Skipping %s %s already added", key, func)
            return func

    HOOKS[key].append(func)
    return func


def make_allowed_mentions(mentions: Iterable[str]) -> defaultdict[str, list[str]]:
    """Convert the provided sequence of users and roles to a discord.AllowedMentions

    Similar to discord_chat.make_allowed_mentions but doesn't strip @everyone/@here
    """
    allowed_mentions: DefaultDict[str, list[str]] = defaultdict(list)

    for role_or_user in mentions:
        if match := re.match(r"<@(\d+)>", role_or_user):
            allowed_mentions["users"].append((match.group(1)))
        elif match := re.match(r"<@&(\d+)>", role_or_user):
            allowed_mentions["roles"].append((match.group(1)))

    return allowed_mentions


def send_log_line_webhook_message(
        webhook: DiscordMentionWebhook,
        _,
        log_line: Dict[str, str | int | float | None],
) -> None:
    """Send a time stammped embed of the log_line and mentions to the provided Discord Webhook"""

    config = RconServerSettingsUserConfig.load_from_db()

    mentions = webhook.user_mentions + webhook.role_mentions

    wh = make_hook(webhook.url)
    if not wh:
        logger.error("Error creating discord webhook for: %s", webhook.url)
        return

    allowed_mentions = make_allowed_mentions(mentions)

    content = " ".join(mentions)
    description: str = escape_markdown(log_line["line_without_time"])
    embed = discord_webhook.DiscordEmbed(
        description=description,
        timestamp=datetime.datetime.utcfromtimestamp(log_line["timestamp_ms"] / 1000),
    )

    embed.set_footer(text=config.short_name)

    wh.content = content
    wh.add_embed(embed)
    wh.allowed_mentions = allowed_mentions
    wh.execute()


# I don't think there is a good way to cache invalidate this without
# circular imports when setting it through LogLineWebhookUserConfig
# but it is invalidated on service startup
@ttl_cache(ttl=60 * 5)
def load_generic_hooks():
    """Load and validate all the subscribed log line webhooks from config.yml"""
    logger.info("Loading generic hooks")
    config = LogLineWebhookUserConfig.load_from_db()
    for hook in config.webhooks:
        # mentions = [h.user_mentions + h.role_mentions for h in conf.webhooks]
        func = partial(send_log_line_webhook_message, hook.webhook)

        # Have to set these attributes as the're used in LogLoop.process_hooks()
        func.__name__ = send_log_line_webhook_message.__name__
        func.__module__ = __name__

        for log_type in hook.log_types:
            logger.info("Adding log type %s, %s", func, log_type.value)
            on_generic(log_type.value, func)


class LogLoop:
    log_history_key = "log_history"

    def __init__(self):
        self.rcon = get_rcon()
        self.red = get_redis_client()
        self.duplicate_guard_key = "unique_logs"
        self.log_history = self.get_log_history_list()
        self.running = True  # Used for graceful shutdown

        logger.info("Registered hooks: %s", HOOKS)

    @staticmethod
    def get_log_history_list() -> FixedLenList[StructuredLogLineWithMetaData]:
        return FixedLenList(key=LogLoop.log_history_key, max_len=100_000)

    def run(self, loop_frequency_secs=2, cleanup_frequency_minutes=10, batch_size=120):
        # Initialize by getting logs from a longer time period, then use shorter intervals
        self._run_initial_collection()

        self.cleanup()
        last_cleanup_time = datetime.datetime.now()

        while self.running:
            try:
                # Use long connection for batch collection
                self._run_batch_collection(batch_size, loop_frequency_secs)

                # Check if cleanup is needed
                if (
                        datetime.datetime.now() - last_cleanup_time
                ).total_seconds() >= cleanup_frequency_minutes * 60:
                    self.cleanup()
                    last_cleanup_time = datetime.datetime.now()

                # Get player stats (keep existing logic)
                dp = self.rcon.get_detailed_players()
                if dp["fail_count"] > 0:
                    logger.warning(
                        "Could not fetch all player stats. "
                        + str(dp["fail_count"])
                        + " players failed."
                    )
                self.record_player_stats(dp["players"])

                # Batch interval
                time.sleep(1)

            except KeyboardInterrupt:
                logger.info("Received stop signal, shutting down gracefully")
                self.running = False
                break
            except Exception as e:
                logger.exception("Log loop encountered an exception, will retry in 1 second: %s", e)
                time.sleep(1)

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
        for player_id in players:
            player = players.get(player_id)
            map_players = m.setdefault("player_stats", dict())
            p = map_players.get(
                player_id,
                PlayerStat(
                    combat=player["combat"],
                    p_combat=0,
                    offense=player["offense"],
                    p_offense=0,
                    defense=player["defense"],
                    p_defense=0,
                    support=player["support"],
                    p_support=0,
                ),
            )
            for stat in ["combat", "offense", "defense", "support"]:
                if player[stat] < p[stat]:
                    p["p_" + stat] = p["p_" + stat] + p[stat]

                p[stat] = player[stat]
            map_players[player_id] = p
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
            logger.warning("Received old log record, ignoring")
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
            # Increase deduplication record retention time to 24 hours (1440 minutes) to fix kill statistics accuracy issue
            if (datetime.datetime.now() - t).total_seconds() > 1440 * 60:
                logger.debug("Older than 24 hours, removing: %s", k)
                self.red.srem(self.duplicate_guard_key, k)
        logger.info("Cleanup done")

    def process_hooks(self, log: StructuredLogLineWithMetaData):
        logger.debug("Processing %s", f"{log['action']} | {log['message']}")
        hooks = []
        started_total = time.time()
        for action_hook, funcs in HOOKS.items():
            if log["action"] == action_hook:
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

    def _run_initial_collection(self):
        """Get logs from a longer time period on initial startup"""
        try:
            load_generic_hooks()
            since_min = 10
            logs: ParsedLogsType = self.rcon.get_structured_logs(
                since_min_ago=since_min
            )
            logger.info("Initial collection retrieved %d logs", len(logs["logs"]))
            for log in reversed(logs["logs"]):
                line = self.record_line(log)
                if line:
                    self.process_hooks(line)
        except Exception as e:
            logger.exception("Initial log collection failed: %s", e)

    def _run_batch_collection(self, batch_size: int, interval_secs: int):
        """Use long connection for batch log collection"""
        logger.debug("Starting batch collection, batch size: %d, interval: %d seconds", batch_size, interval_secs)

        try:
            with self.rcon.with_connection() as conn:
                last_iteration_start = None

                for i in range(batch_size):
                    if not self.running:
                        logger.info("Received stop signal, exiting batch collection")
                        break

                    try:
                        # Load dynamic hooks
                        if i == 0:  # Only load once at the beginning of the batch
                            load_generic_hooks()

                        # Calculate the time window for log retrieval
                        current_time = time.time()
                        if last_iteration_start is not None:
                            elapsed_seconds = int(current_time - last_iteration_start)
                            # If less than 10 seconds, get 10 seconds of logs
                            # If more than 10 seconds, get elapsed + 10 seconds of logs
                            if elapsed_seconds < 10:
                                log_window_seconds = 10
                            else:
                                log_window_seconds = elapsed_seconds + 10
                            logger.debug("Elapsed time: %d seconds, fetching logs for %d seconds", elapsed_seconds, log_window_seconds)
                        else:
                            # First iteration, use default window
                            log_window_seconds = 10

                        last_iteration_start = current_time

                        # Get logs from the calculated time window
                        logs: ParsedLogsType = self.rcon.get_structured_logs_with_seconds_conn(
                            since_sec_ago=log_window_seconds,
                            conn=conn
                        )

                        # Process logs (existing logic)
                        for log in reversed(logs["logs"]):
                            line = self.record_line(log)
                            if line:
                                self.process_hooks(line)

                        if i < batch_size - 1:  # No need to sleep on the last iteration
                            time.sleep(interval_secs)

                    except Exception as e:
                        logger.warning("Batch collection iteration %d failed: %s", i + 1, e)
                        # Single failure does not interrupt the entire batch, continue to next
                        continue

        except Exception as e:
            logger.exception("Batch collection connection failed: %s", e)
            # Wait briefly before outer retry on connection failure
            time.sleep(2)

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
from hllrcon.data import Role, Team

from rcon.cache_utils import get_redis_client, ttl_cache
from rcon.discord import make_hook
from rcon.rcon import get_rcon
from rcon.types import AllLogTypes, GameStateType, GetDetailedPlayers, MapInfo, MapScore, UnitHistoryEntry, StructuredLogLineWithMetaData, PlayerStat, WorldPositionType
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
        self.ACTIVE_MAP_INDEX = 0
        self.RECORD_STATS_DELAY = 30
        self.GET_LOGS_SINCE_MIN = 180
        logger.info("Registered hooks: %s", HOOKS)

    @staticmethod
    def get_log_history_list() -> FixedLenList[StructuredLogLineWithMetaData]:
        return FixedLenList(key=LogLoop.log_history_key, max_len=100_000)

    def run(self, loop_frequency_secs=2, cleanup_frequency_minutes=10):
        self.GET_LOGS_SINCE_MIN = 180
        last_cleanup_time = datetime.datetime.now()
        prev_map_time_elapsed = 0

        while True:
            load_generic_hooks()
            self.process_logs()
            prev_map_time_elapsed = self.update_maps_history(prev_map_time_elapsed)
            last_cleanup_time = self.cleanup(last_cleanup_time, cleanup_frequency_minutes)
            time.sleep(loop_frequency_secs)

    def update_maps_history(self, prev_map_time_elapsed: int) -> int:
        dp = self.get_detailed_players()
        gs = self.rcon.get_gamestate()
        maps_history = MapsHistory()

        if len(maps_history) == 0:
            logger.info("No map seems to be running, skipping saving stats")
            return prev_map_time_elapsed

        current_map = maps_history[self.ACTIVE_MAP_INDEX]
        now = int(datetime.datetime.now().timestamp())

        # HLL SERVER BUG
        # Player's stats are leaking into the next match before the player
        # properly connects to the server / before the player's map loads
        if current_map["start"] + self.RECORD_STATS_DELAY >= now:
            logger.info("Waiting 30s from map start, skipping saving stats")
            return prev_map_time_elapsed

        # Once the game ends time_remaining changes to 100 (after the match score screen)
        curr_map_time_elapsed = gs["match_time"] - gs["time_remaining"].seconds
        if gs["time_remaining"].seconds < 101 and now - current_map["start"] > curr_map_time_elapsed:
            curr_map_time_elapsed = now - current_map["start"]

        if gs["current_map"]["id"] != current_map["name"]:
            logger.info("Map has changed but has not started yet(based on map id diff), skipping saving stats\ncurrent_map: %s\ncached_map:%s", gs["current_map"]["id"], current_map["name"])
            return gs["time_remaining"].seconds
        
        if gs["time_remaining"].seconds == 0:
            logger.info("Map has changed but has not started yet(based on time remaining diff), skipping saving stats\ntime_remaining:%d\ncurrently_recorded_time_elapsed:%d\npreviously_recorded_time_elapsed:%d", gs["time_remaining"].seconds, curr_map_time_elapsed, prev_map_time_elapsed)
            return gs["time_remaining"].seconds

        if gs["allied_score"] == 2 and gs["axis_score"] == 2 and len(current_map["cap_flips"]) > 1:
            logger.info("New score is 2:2 but there are some cap flips records already")
            return gs["time_remaining"].seconds

        self.record_player_stats(current_map, curr_map_time_elapsed, dp)
        self.record_cap_flips(current_map, curr_map_time_elapsed, gs)
        maps_history.update(self.ACTIVE_MAP_INDEX, current_map)
        return curr_map_time_elapsed

    def process_logs(self):
        logs = self.rcon.get_structured_logs(since_min_ago=self.GET_LOGS_SINCE_MIN)
        self.GET_LOGS_SINCE_MIN = 5
        for log in reversed(logs["logs"]):
            line = self.record_line(log)
            if line:
                self.process_hooks(line)

    def get_detailed_players(self) -> GetDetailedPlayers:
        dp = self.rcon.get_detailed_players()
        if dp["fail_count"] > 0:
            logger.warning(
                "Could not fetch all player stats. "
                + str(dp["fail_count"])
                + " players failed."
            )
        return dp

    def record_cap_flips(self, current_map: MapInfo, sec_from_start: int, gs: GameStateType):
        cap_flips = current_map.setdefault("cap_flips", [])

        if len(cap_flips) == 0 or cap_flips[-1]["allied_score"] != gs["allied_score"] or cap_flips[-1]["axis_score"] != gs["axis_score"]:
            cap_flips.append(MapScore(allied_score=gs["allied_score"], axis_score=gs["axis_score"], ts=sec_from_start))
        
    def record_player_stats(self, current_map: MapInfo, sec_from_start: int, dp: GetDetailedPlayers):
        UNASSIGNED = -111
        all_roles = {r.name.lower(): r.id for r in Role.all()}
        all_teams = {t.name.lower(): t.id for t in Team.all()}

        map_cached_stats = current_map.setdefault("player_stats", dict())

        # Compare cached player stats with live player stats
        # if player not online, append UNASSIGNED role
        # that will be eventually used to calc accurate times each role was played 
        offline_unit = UnitHistoryEntry(ts=sec_from_start, t=UNASSIGNED, s=UNASSIGNED, r=UNASSIGNED)
        for player_id, player_stats in map_cached_stats.items():
            # When player joins both role and squad are set to 0 vals but only team is not assigned
            if player_id not in dp["players"] and player_stats["p_unit"]["s"] != UNASSIGNED and player_stats["p_unit"]["r"] != UNASSIGNED:
                player_stats["p_unit"] = offline_unit
                player_stats["units"].append(offline_unit)

        for player_id in dp["players"]:
            current = dp["players"].get(player_id)
            cached = map_cached_stats.get(player_id)

            # first occurance this match
            if not cached:
                map_cached_stats[player_id] = PlayerStat(
                    combat=0,
                    p_combat=0,
                    offense=0,
                    p_offense=0,
                    defense=0,
                    p_defense=0,
                    support=0,
                    p_support=0,
                    vehicle_kills=0,
                    p_vehicle_kills=0,
                    vehicles_destroyed=0,
                    p_vehicles_destroyed=0,
                    kills_and_assists=0,
                    p_kills_and_assists=0,
                    deaths_and_redeploys=0,
                    p_deaths_and_redeploys=0,
                    p_unit=UnitHistoryEntry(ts=sec_from_start, t=UNASSIGNED, s=UNASSIGNED, r=UNASSIGNED),
                    units=[],
                    level=current["level"],
                    p_coord=current["world_position"],
                    has_spawned=False,
                )
                continue
            
            # first coordinates change
            # NOTE when crcon starts mid game and player's coordinates don't change
            if cached and not cached["has_spawned"] and ((cached["p_coord"]["x"] != current["world_position"]["x"] or cached["p_coord"]["y"] != current["world_position"]["y"] or cached["p_coord"]["z"] != current["world_position"]["z"]) or (current["role"] != 0 or current["unit_id"] != 0)):
                cached.update(
                    combat=current["combat"],
                    offense=current["offense"],
                    defense=current["defense"],
                    support=current["support"],
                    vehicle_kills=current["vehicle_kills"],
                    vehicles_destroyed=current["vehicles_destroyed"],
                    kills_and_assists=current["kills"],
                    deaths_and_redeploys=current["deaths"],
                    has_spawned=True,
                )            

            # recalc values only available during the match
            # when the current values are lower, the player reconnected
            # the previously recorded values are moved to "p" values
            # the values are eventually summed up and stored in the db
            # note: some values are persisted across sessions so 
            for v in ["combat", "offense", "defense", "support", "vehicle_kills", "vehicles_destroyed"]:
                if current[v] < cached[v]:
                    cached["p_" + v] = cached["p_" + v] + cached[v]
                cached[v] = current[v]
            
            if current["kills"] < cached["kills_and_assists"]:
                cached["p_kills_and_assists"] = cached["p_kills_and_assists"] + cached["kills_and_assists"]
            cached["kills_and_assists"] = current["kills"]

            if current["deaths"] < cached["deaths_and_redeploys"]:
                cached["p_deaths_and_redeploys"] = cached["p_deaths_and_redeploys"] + cached["deaths_and_redeploys"]
            cached["deaths_and_redeploys"] = current["deaths"]
            
            current_role = all_roles.get(current["role"], UNASSIGNED)
            current_team = all_teams.get(current["team"], UNASSIGNED)
            current_squad = current["unit_id"]

            cached_unit = cached["p_unit"]

            if current_role != cached_unit["r"] or current_squad != cached_unit["s"] or current_team != cached_unit["t"]:
                switched_unit = UnitHistoryEntry(ts=sec_from_start, t=current_team, s=current_squad, r=current_role)
                cached["p_unit"] = switched_unit
                cached["units"].append(switched_unit)

            cached["level"] = current["level"]
            cached["p_coord"] = current["world_position"]
            # update
            map_cached_stats[player_id] = cached

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

    def cleanup(self, last_cleanup_time: datetime.datetime, cleanup_frequency_minutes: int) -> datetime.datetime:
        now = datetime.datetime.now()
        if (now - last_cleanup_time).total_seconds() < cleanup_frequency_minutes * 60:
            return last_cleanup_time

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
        return now

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

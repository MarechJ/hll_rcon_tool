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
from rcon.connection import HLLServerError
from rcon.discord import make_hook
from rcon.maps import GameMode, get_theoretical_match_time, parse_layer
from rcon.rcon import get_rcon
from rcon.types import AllLogTypes, GameStateType, GetDetailedPlayers, MapInfo, MapScore, UnitHistoryEntry, StructuredLogLineWithMetaData, PlayerStat, WorldPositionType
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import DiscordMentionWebhook
from rcon.utils import LogsHistory, MapsHistory

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
    started = time.perf_counter()
    try:
        wh.execute()
    finally:
        logger.debug(
            "Discord log webhook completed in %.3fs",
            time.perf_counter() - started,
        )


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
    def __init__(self):
        self.rcon = get_rcon()
        self.red = get_redis_client()
        self.duplicate_guard_key = "unique_logs"
        self.log_history = self.get_log_history_list()
        self.ACTIVE_MAP_INDEX = 0
        self.RECORD_STATS = 30 # 0.5 minute
        self.RECORD_PLAYER_STATS_DELAY = 120 # 2 minutes
        self.GET_LOGS_SINCE_MIN = 180 # 3 hours
        self.CLEANUP_MIN = 180 # 3 hours
        self.now = 0
        logger.info("Registered hooks: %s", HOOKS)

    @staticmethod
    def get_log_history_list():
        return LogsHistory()

    def run(self, loop_frequency_secs=2, cleanup_frequency_minutes=10):
        self.GET_LOGS_SINCE_MIN = 180
        last_cleanup_time = datetime.datetime.now()
        prev_map_time_elapsed = 0

        while True:
            load_generic_hooks()
            try:
                self.process_logs()
                self.now = int(datetime.datetime.now(tz=datetime.UTC).timestamp())
                prev_map_time_elapsed = self.update_maps_history(prev_map_time_elapsed)
            except (HLLServerError, ConnectionError) as e:
                # The server becomes unresponsive when the map is changing 
                # which in turn restarts this service
                # Let's log it and prevent restarting the service
                logger.warning("Connection error: %s", str(e))
            last_cleanup_time = self.cleanup(last_cleanup_time, cleanup_frequency_minutes)
            time.sleep(loop_frequency_secs)

    # GENERAL
    # - Once the game ends time_remaining changes to 100 (after the match score screen) and so 100s map restart countdown begins
    # - When the map is restarted but no players are in the server time_remaining stays at 0
    # OFFENSIVE
    ## General
    # - Match time is shown as a duration for capturing a single objective not the sum of 5*(cap time per objective)
    # - Remaining match time is therefore the remaining time to capture a single objective
    ## Overtime
    # - Remaining match time is 0 during overtime
    # - If attacking's team manpower is depleted before capturing the point it's game over

    def update_maps_history(self, prev_map_time_elapsed: int) -> int:
        started = time.perf_counter()
        gs = self.rcon.get_gamestate()
        maps_history = MapsHistory()
        current_map = maps_history.get_current_map()

        if not current_map:
            logger.info("[MATCH UNKNOWN] No map seems to be running: %s", current_map)
            return prev_map_time_elapsed
        
        map_start = current_map["start"]
        if map_start is None:
            logger.info("[MATCH START MISSING] Probably a very old map record: %s", current_map)
            return prev_map_time_elapsed

        curr_map_time_elapsed = self.now - map_start

        if current_map["end"] is not None:
            logger.info("[MATCH ENDED]")
            return current_map["end"] - map_start

        if gs["current_map"]["id"] != current_map["name"]:
            logger.info(
                "[MATCH IDLE] - Live and cached map IDs differ, skipping stats "
                "- current_map: %s - cached_map: %s",
                gs["current_map"]["id"],
                current_map["name"],
            )
            return 0

        cached_game_mode = parse_layer(current_map["name"]).game_mode
        if cached_game_mode != gs["game_mode"]:
            logger.info(
                "[MATCH IDLE] - Live and cached game modes differ, skipping stats "
                "- current_mode: %s - cached_mode: %s",
                gs["game_mode"],
                cached_game_mode,
            )
            return 0

        # time remaining is 0 during match overtime so that value alone is not sufficient enough
        if gs["time_remaining"].seconds == 0 and prev_map_time_elapsed == 0:
            logger.info("[MATCH IDLE] - Map has changed but has not started yet(based on time remaining diff), skipping saving stats - time_remaining: %d - currently_recorded_time_elapsed: %d - previously_recorded_time_elapsed: %d", gs["time_remaining"].seconds, curr_map_time_elapsed, prev_map_time_elapsed)
            return 0

        if current_map["match_time"] == 0:
            if cached_game_mode == GameMode.OFFENSIVE:
                remaining = int(gs["time_remaining"].total_seconds())
                if curr_map_time_elapsed <= 60 and remaining > 100:
                    # The session's matchTime can still contain Warfare's
                    # 90-minute value at the match boundary. remainingMatchTime
                    # is the live Offensive objective timer; round it back up to
                    # its configured whole-minute value after polling delay.
                    objective_time = ((remaining + 59) // 60) * 60
                    current_map["match_time"] = get_theoretical_match_time(
                        cached_game_mode, objective_time
                    )
                    logger.info(
                        "Recorded Offensive match time %ds from %ds objective timer",
                        current_map["match_time"],
                        objective_time,
                    )
            else:
                current_map["match_time"] = get_theoretical_match_time(
                    cached_game_mode, gs["match_time"]
                )

        dp = self.get_detailed_players()
        logger.info(
            "RCON map/player polling completed in %.3fs",
            time.perf_counter() - started,
        )
        self.record_cap_flips(current_map, curr_map_time_elapsed, gs)

        # logger.debug("\n[MATCH RUNNING] - Recording stats")
        # logger.debug("\n[MATCH RUNNING]\nMatch Start: %d\nMatch Time: %d\nRemaining Match Time: %d\nTime elapsed: %d\nTime elapsed(now-start): %d\n", current_map["start"], gs["match_time"], gs["time_remaining"].seconds, prev_map_time_elapsed, now - current_map["start"])
        self.record_player_stats(current_map, curr_map_time_elapsed, dp)
        maps_history.update(self.ACTIVE_MAP_INDEX, current_map)
        return curr_map_time_elapsed

    def process_logs(self):
        started = time.perf_counter()
        logs = self.rcon.get_structured_logs(since_min_ago=self.GET_LOGS_SINCE_MIN)
        logger.info(
            "RCON log fetch completed in %.3fs (%d logs)",
            time.perf_counter() - started,
            len(logs["logs"]),
        )
        self.GET_LOGS_SINCE_MIN = 5
        current_map = MapsHistory().get_current_map()
        name_to_id = self._get_name_to_id(current_map) if current_map else {} 
        for log in reversed(logs["logs"]):
            line = self.record_line(log, name_to_id)
            if line:
                self.process_hooks(line)

    def get_detailed_players(self) -> GetDetailedPlayers:
        started = time.perf_counter()
        dp = self.rcon.get_detailed_players()
        logger.info("RCON detailed-player fetch completed in %.3fs", time.perf_counter() - started)
        if dp["fail_count"] > 0:
            logger.warning(
                "Could not fetch all player stats. "
                + str(dp["fail_count"])
                + " players failed."
            )
        return dp

    def record_cap_flips(self, current_map: MapInfo, sec_from_start: int, gs: GameStateType):
        cap_flips = current_map.setdefault("cap_flips", [])

        if gs["allied_score"] == 2 and gs["axis_score"] == 2 and len(cap_flips) > 0:
            # Most likely leak from the current map
            return

        if len(cap_flips) == 0 or cap_flips[-1]["allied_score"] != gs["allied_score"] or cap_flips[-1]["axis_score"] != gs["axis_score"]:
            logger.debug("[MATCH SCORE] - New cap flip recorded as the score has changed")
            cap_flips.append(MapScore(allied_score=gs["allied_score"], axis_score=gs["axis_score"], ts=sec_from_start))

    def record_player_stats(self, current_map: MapInfo, sec_from_start: int, dp: GetDetailedPlayers):
        # skip_caching_stats = current_map["start"] + self.RECORD_STATS >= self.now
        if current_map["start"] is None:
            return
        skip_caching_player_stats = current_map["start"] + self.RECORD_PLAYER_STATS_DELAY >= self.now

        # if skip_caching_stats:
        #     logger.debug("\n[MATCH START] - Waiting %ds from map start, skipping caching", self.RECORD_PLAYER_STATS_DELAY)

        UNASSIGNED = -111
        all_roles = {r.name.lower(): r.id for r in Role.all()}
        all_teams = {t.name.lower(): t.id for t in Team.all()}

        map_cached_stats = current_map.setdefault("player_stats", dict())

        # Compare cached player stats with live player stats
        # if player not online, append UNASSIGNED role
        # that will be eventually used to calc accurate times each role was played 
        offline_unit = UnitHistoryEntry(
            ts=sec_from_start,
            team=UNASSIGNED,
            squad=UNASSIGNED,
            role=UNASSIGNED,
        )
        for player_id, player_stats in map_cached_stats.items():
            # When player joins both role and squad are set to 0 vals but only team is not assigned
            if player_id not in dp["players"] and player_stats["status"] != "offline":
                logger.debug("Player %s has disconnected", player_stats["names"][-1])
                player_stats["status"] = "offline"
                player_stats["p_unit"] = offline_unit
                player_stats["units"] = (player_stats.get("units") or []) + [offline_unit]

        for player_id in dp["players"]:
            current = dp["players"][player_id]
            cached = map_cached_stats.get(player_id)

            # first occurance this match
            if not cached:
                logger.debug("Player %s has connected/been cached", current["name"])
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
                    p_unit=UnitHistoryEntry(
                        ts=sec_from_start,
                        team=UNASSIGNED,
                        squad=UNASSIGNED,
                        role=UNASSIGNED,
                    ),
                    units=[],
                    level=current["level"],
                    p_coord=WorldPositionType(x=current["world_position"]["x"], y=current["world_position"]["y"], z=current["world_position"]["z"]),
                    has_spawned=False,
                    names=[current["name"]],
                    status="online"
                )
                continue

            # BUG: HLL SERVER 
            # Some player's stats are leaking into the next match before the player
            # properly connects to the server / before the player's map loads
            if skip_caching_player_stats:
                logger.debug("[MATCH START] - Waiting %ds from map start, skipping caching player stats", self.RECORD_PLAYER_STATS_DELAY)
                # continue so some other players can be cached for the first time as well
                # or marked as 'offline'
                continue
            
            # first coordinates change
            # Is this still needed? Perhaps for some future use
            # NOTE: if timestamp provided we could track 'idle' players
            # When player connects, disconnects and connects again it's coord can differ
            # NOTE: when crcon starts mid game and player's coordinates don't change
            # there might be needed another check
            if cached and not cached["has_spawned"] and cached["status"] != "offline" and \
                ((cached["p_coord"]["x"] != current["world_position"]["x"] \
                    or cached["p_coord"]["y"] != current["world_position"]["y"] \
                    or cached["p_coord"]["z"] != current["world_position"]["z"])):
                logger.debug("Player %s has spawned for the first time", current["name"])
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

            if cached["status"] == "offline":
                logger.debug("Player %s has reconnected", current["name"])
                cached["status"] = "online"

            # recalc values only available during the match
            # when the current values are lower, the player reconnected
            # the previously recorded values are moved to "p" values
            # the values are eventually summed up and stored in the db
            # NOTE: some values are persisted across sessions
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
            
            current_role = all_roles.get(current["role"] or "", UNASSIGNED)
            current_team = all_teams.get(current["team"] or "", UNASSIGNED)
            current_squad = current["unit_id"] or UNASSIGNED

            cached_unit = cached["p_unit"]

            if (
                current_role != cached_unit["role"]
                or current_squad != cached_unit["squad"]
                or current_team != cached_unit["team"]
            ):
                switched_unit = UnitHistoryEntry(
                    ts=sec_from_start,
                    team=current_team,
                    squad=current_squad,
                    role=current_role,
                )
                cached["p_unit"] = switched_unit
                cached["units"] = (cached.get("units") or []) + [switched_unit]

            if current["name"] not in cached["names"]:
                cached["names"].append(current["name"])

            cached["level"] = current["level"]
            cached["p_coord"] = WorldPositionType(x=current["world_position"]["x"], y=current["world_position"]["y"], z=current["world_position"]["z"])
            # update
            map_cached_stats[player_id] = cached
            # logger.debug("Updated cached stats for player %s", current["name"])

    def _is_log_player_related(self, log: StructuredLogLineWithMetaData) -> bool:
        return bool(log["player_id_1"] or log["player_id_2"] or log["player_name_1"] or log["player_name_2"])

    def _is_log_from_map(self, log: StructuredLogLineWithMetaData | None, map: MapInfo | None) -> bool:
        if not log or not map or not map["start"]:
            return False
        log_time = log.get("event_time")
        map_start = datetime.datetime.fromtimestamp(map["start"])
        if map["end"] is None:
            return log_time >= map_start
        map_end = datetime.datetime.fromtimestamp(map["end"])
        return map_start <= log_time and log_time <= map_end
        
    def _get_name_to_id(self, map: MapInfo) -> dict[str, str]:
        # if one player with name 'foo' disconnects and another player with
        # the same name connects the online player takes preference
        # when name collision happens
        name_to_id: dict[str, str] = {}
        for id, player in map["player_stats"].items():
            for name in player["names"]:
                existing_id = name_to_id.get(name)
                if not existing_id:
                    name_to_id[name] = id
                    continue
                # if there is another id linking to the same name
                # and the player is online, override it
                if existing_id != id and player["status"] == "online":
                    name_to_id[name] = id
        return name_to_id

    def record_line(self, log: StructuredLogLineWithMetaData, name_to_id: dict[str, str] = {}):
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
            logger.error("Can't check against last_line, invalid_format\nLast line: %s\nCurrent log: %s", last_line, log)
        elif last_line and last_line["timestamp_ms"] > log["timestamp_ms"]:
            logger.warning("Received old log record, ignoring\nLast line: %s\nCurrent log: %s", last_line, log)
            return None

        if self._is_log_player_related(log):
            current_map = MapsHistory().get_current_map()
            if current_map and self._is_log_from_map(log, current_map):
                for slot in (1, 2):
                    player_name: str | None = log.get(f"player_name_{slot}", None)
                    player_id: str | None = log.get(f"player_id_{slot}", None)

                    if not player_id and not player_name:
                        continue
                    
                    if not player_id and player_name:
                        # Let's try to backtrack the player_id from cached player stats(redis)
                        player_id = name_to_id.get(player_name)
                        if player_id:
                            logger.debug("Updated player_id: %s by player_name: %s - %s", player_id, player_name, log["raw"])

                    if not player_id:
                        logger.info("Unable to link player %s to any player_id - %s", player_name, log)
                        continue

                    if player_name and player_id:
                        prev_key = name_to_id.setdefault(player_name, player_id)
                        if prev_key != player_id:
                            logger.warning("This log potentialy belonging to 1 or more players\nName: %s, ID: %s, Log: %s", player_name, prev_key, log["raw"])
                    log[f"player_id_{slot}"] = player_id
                    
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
            if (datetime.datetime.now() - t).total_seconds() > self.CLEANUP_MIN * 60:
                logger.debug("Older than %d min, removing: %s", self.CLEANUP_MIN, k)
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
                duration = time.time() - started
                if duration >= 5:
                    logger.warning(
                        "Slow hook %.3fs %s.%s on %s",
                        duration,
                        hook.__module__,
                        hook.__name__,
                        log["raw"],
                    )
                logger.debug(
                    "Ran in %.4f seconds %s.%s on %s",
                    duration,
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

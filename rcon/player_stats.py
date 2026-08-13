import datetime
import logging
import os
import pickle
import re
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, TypeAlias, TypedDict

from hllrcon import HLLTeam

from rcon.cache_utils import get_redis_client
from rcon.game.registry import game_switch
from rcon.game_logs import get_historical_logs_records, get_recent_logs
from rcon.maps import parse_layer
from rcon.models import enter_session
from rcon.player_history import _get_profiles, get_player_profile_by_player_ids
from rcon.rcon import get_rcon
from rcon.types import (
    STAT_DISPLAY_LOOKUP,
    AllLogTypes,
    CachedLiveGameStats,
    GameEnum,
    GetPlayersType,
    MapInfo,
    PlayerProfileType,
    PlayerStat,
    PlayerStatsEnum,
    PlayerStatsType,
    StructuredLogLineWithMetaData,
)
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.utils import MapsHistory, get_default_player_stats

logger = logging.getLogger(__name__)

PLAYER_ID = "player_id"
NAME_KEY_PREFIX = "name:"

class PlayerSessions(TypedDict):
    start: list[datetime.datetime]
    end: list[datetime.datetime]
    total: int

def update_player_name_map(
    id_to_name: dict[str, str],
    player_id: str | None,
    player_name: str | None,
) -> None:
    if player_id and player_name:
        id_to_name[player_id] = player_name


def is_same_log_player(
    player: GetPlayersType,
    log: StructuredLogLineWithMetaData,
    slot: int,
) -> bool:
    log_id = log.get(f"player_id_{slot}")
    log_name = log.get(f"player_name_{slot}")
    player_id = player.get(PLAYER_ID)
    if player_id and log_id:
        return player_id == log_id
    return player["name"] == log_name


@dataclass
class Streaks:
    kill: int = 0
    death: int = 0
    teamkills: int = 0
    deaths_by_tk: int = 0

StatsUpdateHandler: TypeAlias = Callable[
    [PlayerStatsType, GetPlayersType, StructuredLogLineWithMetaData], None
]

class BaseStats:
    _stat_handlers: dict[str, StatsUpdateHandler] = {}

    def __init__(self):
        self.rcon = get_rcon()
        self.voted_yes_regex = re.compile(".*PV_Favour.*")
        self.voted_no_regex = re.compile(".*PV_Against.*")
        self.voted_ignore_regex = re.compile(".*PV_Ignored.*")
        self.team_switch_regex = re.compile(r"\((Axis|Allies|None) > (Axis|Allies|None)\)")
        self.red = get_redis_client()
        self._stat_handlers = {
            AllLogTypes.kill: self._add_kill_handler,
            AllLogTypes.team_kill: self._add_tk_handler,
            AllLogTypes.vote_started: self._add_vote_started_handler,
            AllLogTypes.vote: self._add_vote_handler,
        }

    # The main function
    def get_stats_by_player(
        self,
        indexed_logs: dict[str, list[StructuredLogLineWithMetaData]],
        players: list[GetPlayersType],
        profiles_by_id: dict[str, PlayerProfileType],
    ) -> dict[str, PlayerStatsType]:
        stats_by_player: dict[str, PlayerStatsType] = {}

        # Deduplicate players by player_id so a single canonical record is computed per id.
        unique_players_by_id: dict[str, GetPlayersType] = {}
        # If there are players without player_id, we keep them keyed by name (legacy)
        legacy_name_only_players: list[GetPlayersType] = []

        for p in players:
            pid = p.get(PLAYER_ID)
            if pid:
                # later items overwrite earlier ones: prefer the last-seen record for that id
                unique_players_by_id[pid] = p
            else:
                legacy_name_only_players.append(p)

        # iterate canonical players (by id) followed by any name-only players
        for player in list(unique_players_by_id.values()) + legacy_name_only_players:
            logger.debug("Crunching stats for %s", player)

            profile = profiles_by_id.get(player.get(PLAYER_ID))
            soldier = profile.soldier if profile else None

            # Initialise stats and populate them with values based on player's profile and session
            player_stats = PlayerStatsType(get_default_player_stats())
            player_stats.update(
                player=player["name"],
                player_id=player["player_id"],
                platform=player.get("platform") or (soldier.platform if soldier else None),
                steaminfo=profile.steaminfo.to_dict() if profile and profile.steaminfo else None,
                last_spawn=self._get_player_first_appearance(player),
                time_seconds=int(self._get_player_session_time(player)),
            )

            # Update stats based on game logs
            player_logs = indexed_logs.get(player["player_id"], [])
            streaks = Streaks()
            for log in player_logs:
                self._process_log(player_stats, player, log)                
                self._calc_streaks(player_stats, player, log, streaks)
                self._calc_computed_stats(player_stats)

            # Use player_id as the mapping key so a name change does not create duplicates
            pid_key = player.get("player_id") or player.get("name")
            stats_by_player[pid_key] = player_stats

        return stats_by_player

    # STATS PROCESSORS
    def _process_log(
        self,
        stats: PlayerStatsType,
        player: GetPlayersType,
        log: StructuredLogLineWithMetaData,
    ) -> None:
        log_type = log.get("action") or log.get("type")
        handler = self._stat_handlers.get(log_type)
        if handler is not None:
            handler(stats, player, log)

    def _calc_computed_stats(self, stats: PlayerStatsType) -> None:
        stats.update(
            kills_per_minute=round(stats["kills"] / max(stats["time_seconds"] / 60, 1), 2),
            deaths_per_minute=round(stats["deaths"] / max(stats["time_seconds"] / 60, 1), 2),
            kill_death_ratio=round(stats["kills"] / max(stats["deaths"], 1), 2)
        )

    def _calc_streaks(
        self,
        stats: PlayerStatsType,
        player: GetPlayersType,
        log: StructuredLogLineWithMetaData,
        streaks: Streaks,
        ) -> None:
        action = log["action"]

        log_time = datetime.datetime.fromtimestamp(log["timestamp_ms"] / 1000)
        if action == AllLogTypes.kill:
            if self._is_player_kill(player, log):
                streaks.kill += 1
                streaks.death = 0
                streaks.teamkills = 0
            elif self._is_player_death(player, log):
                streaks.kill = 0
                streaks.deaths_by_tk = 0
                streaks.death += 1
                self._process_death_time(log_time, stats)
        if action == AllLogTypes.team_kill:
            if self._is_player_kill(player, log):
                streaks.teamkills += 1
            if self._is_player_death(player, log):
                streaks.deaths_by_tk += 1
                self._process_death_time(log_time, stats)
        if action == AllLogTypes.connected:
            stats["last_spawn"] = log_time
        if action == AllLogTypes.disconnected:
            self._process_death_time(log_time, stats, save_spawn=False)

        stats["kills_streak"] = max(streaks.kill, stats["kills_streak"])
        stats["deaths_without_kill_streak"] = max(
            streaks.death, stats["deaths_without_kill_streak"]
        )
        stats["teamkills_streak"] = max(streaks.teamkills, stats["teamkills_streak"])
        stats["deaths_by_tk_streak"] = max(
            streaks.deaths_by_tk, stats["deaths_by_tk_streak"]
        )

    # LOG HANDLERS
    def _add_kill_handler(self, stats: PlayerStatsType, player: GetPlayersType, log: StructuredLogLineWithMetaData):
        self._add_kd("kills", "deaths", stats, player, log)
        if self._is_player_kill(player, log):
            stats["weapons"][log["weapon"]] = stats["weapons"].get(log["weapon"], 0) + 1
            stats["most_killed"][log["player_id_2"]] = (
                stats["most_killed"].get(log["player_id_2"], 0) + 1
            )
        if self._is_player_death(player, log):
            stats["death_by_weapons"][log["weapon"]] = (
                stats["death_by_weapons"].get(log["weapon"], 0) + 1
            )
            stats["death_by"][log["player_id_1"]] = (
                stats["death_by"].get(log["player_id_1"], 0) + 1
            )

    def _add_tk_handler(self, stats: PlayerStatsType, player: GetPlayersType, log: StructuredLogLineWithMetaData):
        self._add_kd("teamkills", "deaths_by_tk", stats, player, log)

    def _add_vote_handler(self, stats: PlayerStatsType, player: GetPlayersType, log: StructuredLogLineWithMetaData):
        if self.voted_no_regex.match(log["raw"]):
            stats["nb_voted_no"] += 1
        elif self.voted_yes_regex.match(log["raw"]):
            stats["nb_voted_yes"] += 1
        elif self.voted_ignore_regex.match(log["raw"]):
            # TODO
            pass
        else:
            logger.warning(
                "VOTE log line does not match either vote yes,no or ignore regex: %s",
                log["raw"],
            )

    def _add_vote_started_handler(self, stats: PlayerStatsType, player: GetPlayersType, log: StructuredLogLineWithMetaData):
        stats["nb_vote_started"] += 1

    # HELPERS
    def _is_player_death(self, player: GetPlayersType, log: StructuredLogLineWithMetaData):
        return is_same_log_player(player, log, 2)

    def _is_player_kill(self, player: GetPlayersType, log: StructuredLogLineWithMetaData):
        return is_same_log_player(player, log, 1)

    def _process_death_time(self, log_time: datetime.datetime, stats: PlayerStatsType, save_spawn=True):
        if not stats.get("last_spawn"):
            stats["last_spawn"] = log_time
            return

        time_since_last_spawn = int((log_time.replace(tzinfo=datetime.UTC) - stats["last_spawn"].replace(tzinfo=datetime.UTC)).total_seconds())
        stats["longest_life_secs"] = max(
            time_since_last_spawn,
            stats["longest_life_secs"],
        )
        stats["shortest_life_secs"] = min(
            time_since_last_spawn,
            stats["shortest_life_secs"],
        )
        if save_spawn:
            stats["last_spawn"] = log_time

    def _add_kd(self, attacker_key, victim_key, stats, player, log: StructuredLogLineWithMetaData):
        if self._is_player_kill(player, log):
            stats[attacker_key] += 1
        elif self._is_player_death(player, log):
            stats[victim_key] += 1
        else:
            logger.warning(
                "Log line does not belong to player '%s' line: '%s'",
                player["name"],
                log["raw"],
            )

    # ABSTRACT METHODS
    def _get_player_session_time(self, player: GetPlayersType) -> int:
        raise NotImplementedError("_get_player_session_time")

    def _get_player_first_appearance(self, player: GetPlayersType) -> datetime.datetime | None:
        raise NotImplementedError("_get_player_first_appearance")


class LiveStats(BaseStats):
    def _get_player_session_time(self, player: GetPlayersType) -> int:
        if not player or not player.get("profile"):
            logger.warning("Can't use player profile")
            return 0

        player_time_sec = player.get("profile", {}).get("current_playtime_seconds", 0)

        return player_time_sec

    def _get_player_first_appearance(self, player: GetPlayersType) -> datetime.datetime | None:
        if not player or not player.get("profile"):
            logger.warning("Can't use player profile")
            return None

        player_profile = player.get("profile", {})
        player_sessions = player_profile.get("sessions")
        if not player_sessions:
            logger.warning("No sessions in player profile %s", player_profile)
            return None

        session_start = player_sessions[0].get("start")
        if not session_start:
            return None

        return session_start.replace(tzinfo=datetime.UTC)

    def _is_log_from_current_session(self, now, player, log: StructuredLogLineWithMetaData):
        return (
            log["timestamp_ms"]
            >= (now.timestamp() - self._get_player_session_time(player)) * 1000
        )

    def _get_indexed_logs_by_player_for_session(
        self, now, indexed_players_by_id, indexed_players_by_name, logs: list[StructuredLogLineWithMetaData]
    ) -> tuple[dict[str, list[StructuredLogLineWithMetaData]], dict[str, str]]:
        logs_indexed: dict[str, list[StructuredLogLineWithMetaData]] = {}
        id_to_name: dict[str, str] = {}
        for l in logs:
            update_player_name_map(id_to_name, l.get("player_id_1"), l.get("player_name_1"))
            update_player_name_map(id_to_name, l.get("player_id_2"), l.get("player_name_2"))

            player = indexed_players_by_id.get(l.get("player_id_1")) or indexed_players_by_name.get(
                l.get("player_name_1")
            )
            player2 = indexed_players_by_id.get(l.get("player_id_2")) or indexed_players_by_name.get(
                l.get("player_name_2")
            )

            try:
                # Only consider stats for a player from his last connection (so a disconnect reconnect should reset stats) otherwise multiple sessions could be blended into one, even if they are far apart
                if player and self._is_log_from_current_session(now, player, l):
                    key = l["player_id_1"]
                    if key:
                        logs_indexed.setdefault(key, []).append(l)
                if player2 and self._is_log_from_current_session(now, player2, l):
                    key = l["player_id_2"]
                    if key:
                        logs_indexed.setdefault(key, []).append(l)
            except KeyError:
                logger.exception("Invalid log line %s", l)

        return logs_indexed, id_to_name

    def get_current_players_stats(self):
        players: list[GetPlayersType]  = self.rcon.get_players()
        if not players:
            logger.debug("No players")
            return {}

        players = [p for p in players if p.get(PLAYER_ID)]
        detailed_players = self.rcon.get_detailed_players()["players"]
        for player in players:
            details = detailed_players.get(player[PLAYER_ID])
            if details:
                player["platform"] = details.get("platform")

        with enter_session() as sess:
            id_to_PlayerID = {
                profile.player_id: profile
                for profile in _get_profiles(
                    sess, [p[PLAYER_ID] for p in players], nb_sessions=1
                )
            }
            logger.info(
                "%s players, %s profiles loaded", len(players), len(id_to_PlayerID)
            )
            oldest_session_seconds = self._get_player_session_time(
                max(players, key=self._get_player_session_time)
            )
            logger.debug("Oldest session: %s", oldest_session_seconds)
            now = datetime.datetime.now()
            min_timestamp = (
                now - datetime.timedelta(seconds=oldest_session_seconds)
            ).timestamp()
            logger.debug("Min timestamp: %s", min_timestamp)
            logs = get_recent_logs(min_timestamp=min_timestamp)

            logger.info("%s log lines to process", len(logs["logs"]))

            id_to_player = {
                p[PLAYER_ID]: p for p in players if p.get(PLAYER_ID)
            }
            name_to_player = {p["name"]: p for p in players}
            indexed_logs, id_to_name = self._get_indexed_logs_by_player_for_session(
                now, id_to_player, name_to_player, list(reversed(logs["logs"]))
            )

            for p in players:
                update_player_name_map(id_to_name, p.get(PLAYER_ID), p.get("name"))

            stats = self.get_stats_by_player(
                indexed_logs, players, id_to_PlayerID
            )

            # Enrich the log-derived stats with the richer per-unit stats stored on the current map.
            # This mirrors the behavior of `current_game_stats()`.
            try:
                current_map = MapsHistory()[0]
            except IndexError:
                logger.error("No maps information available")
                return stats

            _apply_current_map_player_stats(
                stats=stats, current_map=current_map
            )
            return stats

    def set_live_stats(self):
        snapshot_ts = datetime.datetime.now().timestamp()
        stats = self.get_current_players_stats()
        self.red.set(
            "LIVE_STATS",
            pickle.dumps(
                dict(snapshot_timestamp=snapshot_ts, stats=list(stats.values()))
            ),
        )

    def get_cached_stats(self):
        stats = self.red.get("LIVE_STATS")
        if stats:
            stats = pickle.loads(stats)
        return stats


class TimeWindowStats(BaseStats):
    def __init__(self):
        super().__init__()
        self.match_end_result_regex = re.compile(
            r"MATCH ENDED `.+` ALLIED \((\d) - (\d)\) AXIS"
        )

    def _set_start_end_times(
        self, player: str, players_times: dict[str, PlayerSessions], log: StructuredLogLineWithMetaData, from_: datetime.datetime, offset_warmup_time_seconds=180
    ):
        if not player:
            return
        event_time = log.get("event_time").replace(tzinfo=datetime.UTC)
        # A CONNECT means the begining of a session for the player
        if log["action"] == AllLogTypes.connected:
            return players_times.setdefault(player, PlayerSessions(start=[], end=[], total=0))["start"].append(event_time)
        # if the player is not already in the times record we add the start of the stats window as his session start time
        # we didn't see a CONNECTED before, so it means that the player was here before the current window.
        # For those we add the game warmup time to have a more accurate kill / min
        if player not in players_times and log["action"] != AllLogTypes.disconnected:
            return players_times.setdefault(player, PlayerSessions(start=[], end=[], total=0))["start"].append(
                from_ + datetime.timedelta(seconds=offset_warmup_time_seconds)
            )
        # if the player was already in the time record and we see a disconnect we log it as the end of his session
        if player in players_times and log["action"] == AllLogTypes.disconnected:
            return players_times.setdefault(player, PlayerSessions(start=[], end=[], total=0))["end"].append(event_time)
        # if we had a player that disconnected but was not in the time record it means he did have any kill / death or other actions like chat, vote
        # This player won't have a session time (most likely and AFK one)
        # NOTE: if there is no session it is throwing errors so if the player's single log
        # for the match is DISCONNECT let's record it as 0 second session time
        if player not in players_times and log["action"] == AllLogTypes.disconnected:
            return players_times.setdefault(player, PlayerSessions(start=[event_time], end=[event_time], total=0))

    def _get_player_session_time(self, player: GetPlayersType) -> int:
        player_key = player["player_id"]
        if not player_key or not self.times:
            return 0
        if not self.times.get(player_key):
            logger.warning("Unable to get session time for %s", player)
            return 0
        return self.times[player_key].get("total", 0)

    def _get_player_first_appearance(self, player: GetPlayersType) -> datetime.datetime | None:
        player_key = player["player_id"]
        if not player_key or not self.times:
            return None
        if not self.times.get(player_key) or not self.times[player_key].get("start"):
            logger.warning("Unable to get first appearance time for %s", player)
            return None
        return self.times[player_key]["start"][0]

    def _get_players_stats_from_logs(
        self,
        logs: Iterable[StructuredLogLineWithMetaData],
        from_: datetime.datetime,
        until: datetime.datetime,
        offset_warmup_time_seconds=120,
        offset_cooldown_time_seconds=100,
        cached_players: dict[str, PlayerStat] = {}
    ):
        indexed_logs: dict[str, list[StructuredLogLineWithMetaData]] = {}
        unique_players = set[tuple[str, str]]()
        players_times: dict[str, PlayerSessions] = {}
        name_to_id = {name: id for id, player in cached_players.items() for name in player["names"]} 
        for log in logs:
            for slot in (1, 2):
                player_name: str | None = log.get(f"player_name_{slot}")
                player_id: str | None = log.get(f"player_id_{slot}")
                player_key = None
                if player_id:
                    player_key = player_id
                elif player_name:
                    # This log does not contain player_id but does contain player_name detail
                    # Let's try to backtrack the player_id from previous logs or cached player stats(redis)
                    logger.debug("This log contains player_name without player_id detail\n%s", log)
                    player_key = name_to_id.get(player_name)
                else:
                    # Not a player related log
                    continue

                if not player_key:
                    logger.info("Unable to determine who this log belongs to\n%s", log)
                    continue

                if player_name and player_key:
                    unique_players.add((player_name, player_key))
                    prev_key = name_to_id.setdefault(player_name, player_key)
                    if prev_key != player_key:
                        logger.warning("A log with the same player_name belonging to 1 or more players\nName: %s, ID: %s\n, Log: %s", player_name, prev_key, log)

                self._set_start_end_times(player_key, players_times, log, from_)
                indexed_logs.setdefault(player_key, []).append(log)

        # Convert the unique set of players into a list of dict for compatibility with parent class
        players = [
            dict(name=player_name, player_id=player_id)
            for player_name, player_id in unique_players
        ]
        # Here we massage the session times for a player. 1 session should be a pair of times a start and an end
        for player, times in players_times.items():
            starts = times["start"]
            ends = times["end"]
            times["total"] = 0
            # This is an error check, it should never happend to not have a start time
            # If the player connected prior to the time window we're computing the start for, then the start time should be the start of that window
            if len(starts) == 0:
                logger.error("No start time for  %s - %s", player, times)
            # If there's 1 start more that there are ends, it means that the player did not leave the game, and therefore we add the end of the session as the end of the window we're computing the stats for
            # We discount the cooldown time at the end of the game to get a more accurate kill / min
            elif len(starts) == len(ends) + 1:
                logger.debug("Adding end time to end of range for %s", player)
                ends.append(
                    until - datetime.timedelta(seconds=offset_cooldown_time_seconds)
                )
            # If starts and ends don't match something's probably wrong the the code
            if len(starts) != len(ends):
                logger.error("Sessions time don't match for %s - %s", player, times)
                continue

            # We loop over the pairs of start and ends (chronologically in the order we encountered them)
            # and we compute the total play time of the player for the window we're looking at
            for pair in zip(starts, ends):
                start, end = pair
                # logger.debug("\nstart: %s - %s\nend: %s - %s", start, type(start), end, type(end))
                sess_time = end - start
                times["total"] += int(sess_time.total_seconds())

        self.times = players_times

        logger.debug("Indexing profiles by id")
        # we create and hashmap where the key is the player ID (steam/windows) of a player and the value his DB profile.
        # The DB rows are eagerly loaded (at least the ones we need later on) if you need more rows make sure to eager load them as well otherwise it will add significan slowness
        # The profiles are attached to the current DB session
        with enter_session() as sess:
            profiles_by_id = {
                profile.player_id: profile
                for profile in get_player_profile_by_player_ids(
                    sess, [p[PLAYER_ID] for p in players]
                )
            }

            logger.debug("Computing stats")
            # we delegate the stats computation to the parent class
            return self.get_stats_by_player(
                indexed_logs=indexed_logs,
                players=players,
                profiles_by_id=profiles_by_id,
            )

    def get_players_stats_at_time(self, from_, until, server_number=None, cached_players: dict[str, PlayerStat] = {}):
        server_number = server_number or os.getenv("SERVER_NUMBER")
        with enter_session() as sess:
            # Get the logs from the database for the given time range
            rows = get_historical_logs_records(
                sess,
                from_=from_,
                till=until,
                time_sort="asc",
                server_filter=server_number,
                limit=99999999,
            )

            return self._get_players_stats_from_logs(
                [row.compatible_dict() for row in rows], from_, until, cached_players=cached_players
            )

    def map_result(self, from_, until, server_number=None) -> dict[str, int]:
        server_number = server_number or os.getenv("SERVER_NUMBER")
        with enter_session() as sess:
            rows = get_historical_logs_records(
                sess,
                action="MATCH ENDED",
                from_=from_,
                till=until,
                time_sort="asc",
                server_filter=server_number,
                limit=1,
            )
            if len(rows) == 0:
                return {"Allied": 2, "Axis": 2}
            (allied, axis) = self.match_end_result_regex.match(
                rows[0].compatible_dict().get("message")
            ).groups()
            return {"Allied": int(allied), "Axis": int(axis)}

    def get_players_stats_from_time(self, from_timestamp: float, cached_players: dict[str, PlayerStat] = {}):
        logs = get_recent_logs(min_timestamp=from_timestamp)
        return self._get_players_stats_from_logs(
            reversed(logs.get("logs", [])),
            datetime.datetime.fromtimestamp(from_timestamp, datetime.UTC),
            datetime.datetime.now(datetime.UTC),
            offset_cooldown_time_seconds=0,
            cached_players=cached_players
        )


def live_stats_loop():
    live = LiveStats()
    config = RconServerSettingsUserConfig.load_from_db()
    last_loop_session = datetime.datetime(year=2020, month=1, day=1)
    last_loop_game = datetime.datetime(year=2020, month=1, day=1)
    live_session_sleep_seconds = config.live_stats_refresh_seconds
    live_game_sleep_seconds = config.live_stats_refresh_seconds
    logger.debug("live_session_sleep_seconds: {}".format(live_session_sleep_seconds))
    logger.debug("live_game_sleep_seconds: {}".format(live_game_sleep_seconds))
    red = get_redis_client()

    while True:
        # Keep track of session and game timers seperately
        last_loop_session_seconds = (
            datetime.datetime.now() - last_loop_session
        ).total_seconds()
        last_loop_game_seconds = (
            datetime.datetime.now() - last_loop_game
        ).total_seconds()

        if last_loop_session_seconds >= live_session_sleep_seconds:
            last_loop_session = datetime.datetime.now()
            try:
                live.set_live_stats()
                logger.debug("Refreshed set_live_stats")
            except Exception:
                logger.exception("Error while producing stats")

        if last_loop_game_seconds >= live_game_sleep_seconds:
            last_loop_game = datetime.datetime.now()
            try:
                snapshot_ts = datetime.datetime.now().timestamp()
                stats = current_game_stats()
                logger.debug("Refreshed current_game_stats")
                red.set(
                    "LIVE_GAME_STATS",
                    pickle.dumps(
                        dict(
                            snapshot_timestamp=snapshot_ts,
                            stats=list[PlayerStatsType](stats.values()),
                            refresh_interval_sec=live_game_sleep_seconds,
                        )
                    ),
                )
            except Exception:
                logger.exception("Failed to compute live game stats")

        time.sleep(0.1)


def current_game_stats():
    current_map = MapsHistory().get_current_map()
    if not current_map:
        logger.error("Unable to get current game stats [no map information available]")
        return {}
    if current_map["start"] is None:
        logger.error("Unable to get current game stats [missing map start information]")
        return {}

    stats = TimeWindowStats().get_players_stats_from_time(current_map["start"], current_map["player_stats"])
    _apply_current_map_player_stats(
        stats=stats, current_map=current_map
    )
    return stats


def _apply_current_map_player_stats(
    stats: Mapping[str, PlayerStatsType],
    current_map: MapInfo,
) -> None:
    """Override/augment stats using the richer per-unit values stored on map history.

    `player_stats` is `MapsHistory()[0]["player_stats"]` and keys are player IDs.
    """
    player_stats = current_map.get("player_stats", dict())
    map_layer = parse_layer(current_map["name"])

    for stat in stats.values():
        player_id = stat.get(PLAYER_ID)
        if not player_id:
            logger.debug("Missing player_id for player %s", stat.get("player"))
            continue

        map_stat = player_stats.get(player_id, None)
        if map_stat is None:
            logger.info("No stats for: %s", player_id)
            continue

        team_name = None
        faction_name = None
        unit = map_stat.get("p_unit", None)
        if unit:
            try:
                # TODO: This relies on the assumption that HLLTeam and HLLVTeam are equal enough
                team = HLLTeam.by_id(unit["team"])
                team_name = team.name.lower()
                if team == HLLTeam.ALLIES:
                    faction_name = map_layer.map.allies.name.lower()
                elif team == HLLTeam.AXIS:
                    faction_name = map_layer.map.axis.name.lower()
            except ValueError:
                pass

        # Combat stats
        stat["combat"] = map_stat.get("combat", 0) + map_stat.get("p_combat", 0)
        stat["offense"] = map_stat.get("offense", 0) + map_stat.get("p_offense", 0)
        stat["defense"] = map_stat.get("defense", 0) + map_stat.get("p_defense", 0)
        stat["support"] = map_stat.get("support", 0) + map_stat.get("p_support", 0)

        # Vehicles
        stat["vehicle_kills"] = (
            map_stat.get("vehicle_kills", 0) + map_stat.get("p_vehicle_kills", 0)
        )
        stat["vehicles_destroyed"] = (
            map_stat.get("vehicles_destroyed", 0)
            + map_stat.get("p_vehicles_destroyed", 0)
        )

        # Misc
        stat["kills_and_assists"] = map_stat.get("kills_and_assists", 0) + map_stat.get("p_kills_and_assists", 0)
        stat["deaths_and_redeploys"] = map_stat.get("deaths_and_redeploys", 0) + map_stat.get("p_deaths_and_redeploys", 0)
        stat["level"] = map_stat.get("level", 0)
        stat["team"] = team_name
        stat["faction"] = faction_name
        stat["status"] = map_stat.get("status")

        # Del unused attributes
        del stat["id"]
        del stat["map_id"]
        del stat["units"]


def get_cached_live_game_stats() -> CachedLiveGameStats:
    red = get_redis_client()
    stats = red.get("LIVE_GAME_STATS")
    if stats:
        stats = pickle.loads(stats)
    return stats


def get_stat_post_processor(key: PlayerStatsEnum):
    if key in (
        PlayerStatsEnum.TIME_SECONDS,
        PlayerStatsEnum.LONGEST_LIFE_SECS,
    ):
        return lambda v: round(v / 60, 2)
    else:
        return lambda v: v


def get_stat(
    stats: list[PlayerStatsType],
    key: PlayerStatsEnum,
    limit: int,
    post_process: Callable | None = None,
    reverse: bool | None = None,
) -> list[PlayerStatsType]:
    if key in (PlayerStatsEnum.SHORTEST_LIFE_SECS,):
        reverse = False
    else:
        reverse = True

    if post_process is None:
        post_process = get_stat_post_processor(key=key)

    assert post_process is not None

    stats = sorted(
        stats, key=lambda stat: stat[STAT_DISPLAY_LOOKUP[key]], reverse=reverse
    )[:limit]
    return stats


if __name__ == "__main__":
    from pprint import pprint

    # pprint(LiveStats().get_current_players_stats())
    pprint(
        TimeWindowStats().get_players_stats_from_time(
            datetime.datetime(2021, 7, 16, 23, 30, 44, 793000).timestamp()
        )
    )

    # LiveStats().get_current_players_stats()

import datetime
import logging
import os
import pickle
import re
import time
from dataclasses import dataclass
from typing import Callable

from rcon.cache_utils import get_redis_client
from rcon.game_logs import get_historical_logs_records, get_recent_logs
from rcon.models import enter_session
from rcon.player_history import _get_profiles, get_player_profile_by_steam_ids
from rcon.rcon import get_rcon
from rcon.types import (
    CachedLiveGameStats,
    PlayerStatsType,
    StatTypes,
    StructuredLogLineWithMetaData,
)
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.utils import MapsHistory

logger = logging.getLogger(__name__)

STAT_DISPLAY_LOOKUP = {
    StatTypes.top_killers: "kills",
    StatTypes.top_ratio: "kill_death_ratio",
    StatTypes.top_performance: "kills_per_minute",
    StatTypes.try_harders: "deaths_per_minute",
    StatTypes.top_stamina: "deaths",
    StatTypes.top_kill_streak: "kills_streak",
    StatTypes.i_never_give_up: "deaths_without_kill_streak",
    StatTypes.most_patient: "deaths_by_tk",
    StatTypes.im_clumsy: "teamkills",
    StatTypes.i_need_glasses: "teamkills_streak",
    StatTypes.i_love_voting: "nb_vote_started",
    StatTypes.what_is_a_break: "time_seconds",
    StatTypes.survivors: "longest_life_secs",
    StatTypes.u_r_still_a_man: "shortest_life_secs",
}


@dataclass
class Streaks:
    kill: int = 0
    death: int = 0
    teamkills: int = 0
    deaths_by_tk: int = 0


class BaseStats:
    def __init__(self):
        self.rcon = get_rcon()
        self.voted_yes_regex = re.compile(".*PV_Favour.*")
        self.voted_no_regex = re.compile(".*PV_Against.*")
        self.red = get_redis_client()

    def _is_player_death(self, player, log):
        return player["name"] == log["player2"]

    def _is_player_kill(self, player, log):
        return player["name"] == log["player"]

    def _add_kd(self, attacker_key, victim_key, stats, player, log):
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

    def _add_kill(self, stats, player, log):
        self._add_kd("kills", "deaths", stats, player, log)
        if self._is_player_kill(player, log):
            stats["weapons"][log["weapon"]] = stats["weapons"].get(log["weapon"], 0) + 1
            stats["most_killed"][log["player2"]] = (
                stats["most_killed"].get(log["player2"], 0) + 1
            )
        if self._is_player_death(player, log):
            stats["death_by_weapons"][log["weapon"]] = (
                stats["death_by_weapons"].get(log["weapon"], 0) + 1
            )
            stats["death_by"][log["player"]] = (
                stats["death_by"].get(log["player"], 0) + 1
            )

    def _add_tk(self, stats, player, log):
        self._add_kd("teamkills", "deaths_by_tk", stats, player, log)

    def _add_vote(self, stats, player, log):
        if self.voted_no_regex.match(log["raw"]):
            stats["nb_voted_no"] += 1
        elif self.voted_yes_regex.match(log["raw"]):
            stats["nb_voted_yes"] += 1
        else:
            logger.warning(
                "VOTE log line does not match either vote yes or no regex: %s",
                log["raw"],
            )

    def _add_vote_started(self, stats, player, log):
        stats["nb_vote_started"] += 1

    def _process_death_time(self, log_time, stats, save_spawn=True):
        if not isinstance(stats["last_spawn"], datetime.datetime):
            logger.warning("Unknown last spawn")
            stats["last_spawn"] = log_time
            return

        time_since_last_spawn = (log_time - stats["last_spawn"]).total_seconds()
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

    def _streaks_accumulator(self, player, log, stats, streaks):
        action = log["action"]

        log_time = datetime.datetime.fromtimestamp(log["timestamp_ms"] / 1000)
        if action == "KILL":
            if self._is_player_kill(player, log):
                streaks.kill += 1
                streaks.death = 0
                streaks.teamkills = 0
            elif self._is_player_death(player, log):
                streaks.kill = 0
                streaks.deaths_by_tk = 0
                streaks.death += 1
                self._process_death_time(log_time, stats)
        if action == "TEAM KILL":
            if self._is_player_kill(player, log):
                streaks.teamkills += 1
            if self._is_player_death(player, log):
                streaks.deaths_by_tk += 1
                self._process_death_time(log_time, stats)
        if action == "CONNECTED":
            stats["last_spawn"] = log_time
        if action == "DISCONNECTED":
            self._process_death_time(log_time, stats, save_spawn=False)

        stats["kills_streak"] = max(streaks.kill, stats["kills_streak"])
        stats["deaths_without_kill_streak"] = max(
            streaks.death, stats["deaths_without_kill_streak"]
        )
        stats["teamkills_streak"] = max(streaks.teamkills, stats["teamkills_streak"])
        stats["deaths_by_tk_streak"] = max(
            streaks.deaths_by_tk, stats["deaths_by_tk_streak"]
        )

    def _get_player_session_time(self, player):
        raise NotImplementedError("_get_player_session_time")

    def _get_player_first_appearance(self, player):
        raise NotImplementedError("_get_player_first_appearance")

    def get_stats_by_player(
        self,
        indexed_logs: dict[str, list[StructuredLogLineWithMetaData]],
        players,
        profiles_by_id,
    ):
        """
        players is expected to be a list of dict, such as:
        [{"steam_id_64": ..., "name": ...}, ...]
        """
        stats_by_player = {}

        actions_processors = {
            "KILL": self._add_kill,
            "TEAM KILL": self._add_tk,
            "VOTE STARTED": self._add_vote_started,
            "VOTE": self._add_vote,
        }
        for p in players:
            logger.debug("Crunching stats for %s", p)
            player_logs: list[StructuredLogLineWithMetaData] = indexed_logs.get(
                p["name"], []
            )
            profile = profiles_by_id.get(p.get("steam_id_64"))
            stats = {
                "player": p["name"],
                "steam_id_64": p.get("steam_id_64"),
                "steaminfo": profile.steaminfo.to_dict()
                if profile and profile.steaminfo
                else None,
                "kills": 0,
                "kills_streak": 0,
                "deaths": 0,
                "death_by_weapons": {},
                "deaths_without_kill_streak": 0,
                "teamkills": 0,
                "teamkills_streak": 0,
                "deaths_by_tk": 0,
                "deaths_by_tk_streak": 0,
                "nb_vote_started": 0,
                "nb_voted_yes": 0,
                "nb_voted_no": 0,
                "longest_life_secs": 0,
                "shortest_life_secs": 9999,
                "last_spawn": self._get_player_first_appearance(p),
                "time_seconds": self._get_player_session_time(p),
                "weapons": {},
                "death_by": {},
                "most_killed": {},
                "combat": 0,
                "offense": 0,
                "defense": 0,
                "support": 0,
            }

            streaks = Streaks()
            # player_p = p
            # import ipdb; ipdb.set_trace()
            for l in player_logs:
                action = l["action"]
                processor = actions_processors.get(action, lambda **kargs: None)
                processor(stats=stats, player=p, log=l)
                self._streaks_accumulator(p, l, stats, streaks)

            stats_by_player[p["name"]] = self._compute_stats(stats)

        return stats_by_player

    def _compute_stats(self, stats):
        new_stats = dict(**stats)
        new_stats["kills_per_minute"] = round(
            stats["kills"] / max(stats["time_seconds"] / 60, 1), 2
        )
        new_stats["deaths_per_minute"] = round(
            stats["deaths"] / max(stats["time_seconds"] / 60, 1), 2
        )
        new_stats["kill_death_ratio"] = round(
            stats["kills"] / max(stats["deaths"], 1), 2
        )
        return new_stats


class LiveStats(BaseStats):
    def _get_player_session_time(self, player):
        if not player or not player.get("profile"):
            logger.warning("Can't use player profile")
            return -1

        player_time_sec = player.get("profile", {}).get("current_playtime_seconds", 0)

        return player_time_sec

    def _get_player_first_appearance(self, player):
        if not player or not player.get("profile"):
            logger.warning("Can't use player profile")
            return -1

        player_sessions = player.get("profile", {}).get("sessions")
        if not player_sessions:
            logger.warning("No sessions in player profile")
            return -1

        return player_sessions[0].get("start")

    def _is_log_from_current_session(self, now, player, log):
        if player["name"] == "Dr.WeeD":
            logger.debug(
                "%s %s %s %s",
                log["timestamp_ms"],
                (now.timestamp() - self._get_player_session_time(player)) * 1000,
                log["timestamp_ms"]
                >= (now.timestamp() - self._get_player_session_time(player)) * 1000,
                log["raw"],
            )
        return (
            log["timestamp_ms"]
            >= (now.timestamp() - self._get_player_session_time(player)) * 1000
        )

    def _get_indexed_logs_by_player_for_session(
        self, now, indexed_players, logs: list[StructuredLogLineWithMetaData]
    ) -> dict[str, list[StructuredLogLineWithMetaData]]:
        logs_indexed = {}
        for l in logs:
            player = indexed_players.get(l["player"])
            player2 = indexed_players.get(l["player2"])

            try:
                # Only consider stats for a player from his last connection (so a disconnect reconnect should reset stats) otherwise multiple sessions could be blended into one, even if they are far apart
                if player and self._is_log_from_current_session(now, player, l):
                    logs_indexed.setdefault(l["player"], []).append(l)
                if player2 and self._is_log_from_current_session(now, player2, l):
                    logs_indexed.setdefault(l["player2"], []).append(l)
            except KeyError:
                logger.exception("Invalid log line %s", l)

        return logs_indexed

    def get_current_players_stats(self):
        players = self.rcon.get_players()
        if not players:
            logger.debug("No players")
            return {}

        players = [p for p in players if p.get("steam_id_64")]

        with enter_session() as sess:
            profiles_by_id = {
                profile.steam_id_64: profile
                for profile in _get_profiles(
                    sess, [p["steam_id_64"] for p in players], nb_sessions=1
                )
            }
            logger.info(
                "%s players, %s profiles loaded", len(players), len(profiles_by_id)
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

            indexed_players = {p["name"]: p for p in players}
            indexed_logs = self._get_indexed_logs_by_player_for_session(
                now, indexed_players, list(reversed(logs["logs"]))
            )

            return self.get_stats_by_player(indexed_logs, players, profiles_by_id)

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
    def _set_start_end_times(
        self, player, players_times, log, from_, offset_warmup_time_seconds=180
    ):
        if not player:
            return
        # A CONNECT means the begining of a session for the player
        if log["action"] == "CONNECTED":
            players_times.setdefault(player, {"start": [], "end": []})["start"].append(
                # Event time is a key only avaible in the dict coming from the DB and is already a datetime
                log.get(
                    "event_time",
                    datetime.datetime.utcfromtimestamp(log["timestamp_ms"] // 1000),
                )
            )
        # if the player is not already in the times record we add the start of the stats window as his session start time
        # we didn't see a CONNECTED before, so it means that the player was here before the current window.
        # For those we add the game warmup time to have a more accurate kill / min
        elif player not in players_times and log["action"] != "DISCONNECTED":
            players_times.setdefault(player, {"start": [], "end": []})["start"].append(
                from_ + datetime.timedelta(seconds=offset_warmup_time_seconds)
            )
        # if the player was already in the time record and we see a disconnect we log it as the end of his session
        if player in players_times and log["action"] == "DISCONNECTED":
            players_times.setdefault(player, {"start": [], "end": []})["end"].append(
                log.get(
                    "event_time",
                    datetime.datetime.utcfromtimestamp(log["timestamp_ms"] // 1000),
                )
            )
        # if we had a player that disconnected but was not in the time record it means he did have any kill / death or other actions like chat, vote
        # This player won't have a session time (most likely and AFK one)

    def _get_player_session_time(self, player):
        # TODO: Make safe
        try:
            return self.times[player["name"]]["total"]
        except KeyError:
            logger.warning("Unable to get session time for %s", player.get("name"))
            return 0

    def _get_player_first_appearance(self, player):
        try:
            return self.times[player["name"]]["start"][0]
        except KeyError:
            logger.warning(
                "Unable to get first appearance time for %s", player.get("name")
            )
            return 0

    def _get_players_stats_for_logs(
        self,
        logs,
        from_,
        until,
        offset_warmup_time_seconds=120,
        offset_cooldown_time_seconds=100,
    ):
        indexed_logs = {}
        players = set()
        players_times = {}

        for log in logs:
            # player is the player name
            if player := log.get("player"):
                # Check if this log line in a disconnect / connect and stores it it is
                self._set_start_end_times(player, players_times, log, from_)
                # index logs by player names, so that you can fetch all logs for a given player easily
                indexed_logs.setdefault(player, []).append(log)

                # Create a list of dict for players, for backward compatibility with the parent class that holds the computation logic
                if steamid := log.get("steam_id_64_1"):
                    players.add((player, steamid))

            if player2 := log.get("player2"):
                self._set_start_end_times(player2, players_times, log, from_)
                indexed_logs.setdefault(player2, []).append(log)

                if steamid2 := log.get("steam_id_64_2"):
                    players.add((player2, steamid2))

        # Convert the unique set of players into a list of dict for compatibility with parent class
        players = [
            dict(name=player_name, steam_id_64=player_steamid)
            for player_name, player_steamid in players
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
                time = end - start
                times["total"] += time.total_seconds()

        self.times = players_times

        logger.debug("Indexing profiles by id")
        # we create and hashmap where the key is the steam ID of a player and the value his DB profile.
        # The DB rows are eagerly loaded (at least the ones we need later on) if you need more rows make sure to eager load them as well otherwise it will add significan slowness
        # The profiles are attached to the current DB session
        with enter_session() as sess:
            profiles_by_id = {
                profile.steam_id_64: profile
                for profile in get_player_profile_by_steam_ids(
                    sess, [p["steam_id_64"] for p in players]
                )
            }

            logger.debug("Computing stats")
            # we delegate the stats computation to the parent class
            return self.get_stats_by_player(
                indexed_logs=indexed_logs,
                players=players,
                profiles_by_id=profiles_by_id,
            )

    def get_players_stats_at_time(self, from_, until, server_number=None):
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

            return self._get_players_stats_for_logs(
                [row.compatible_dict() for row in rows], from_, until
            )

    def get_players_stats_from_time(self, from_timestamp):
        logs = get_recent_logs(min_timestamp=from_timestamp)
        return self._get_players_stats_for_logs(
            reversed(logs.get("logs", [])),
            datetime.datetime.utcfromtimestamp(from_timestamp),
            datetime.datetime.utcnow(),
            offset_cooldown_time_seconds=0,
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
                            stats=list(stats.values()),
                            refresh_interval_sec=live_game_sleep_seconds,
                        )
                    ),
                )
            except Exception:
                logger.exception("Failed to compute live game stats")

        time.sleep(0.1)


def current_game_stats():
    try:
        current_map = MapsHistory()[0]
    except IndexError:
        logger.error("No maps information available")
        return {}

    stats = TimeWindowStats().get_players_stats_from_time(current_map["start"])
    for name in stats:
        stat = stats.setdefault(name)
        map_stat = current_map.get("player_stats", dict()).get(
            stat["steam_id_64"], None
        )
        if map_stat is None:
            logger.info("No stats for: " + stat["steam_id_64"])
            continue
        stat["combat"] = map_stat["combat"] + map_stat['p_combat']
        stat["offense"] = map_stat["offense"] + map_stat['p_offense']
        stat["defense"] = map_stat["defense"] + map_stat['p_defense']
        stat["support"] = map_stat["support"] + map_stat['p_support']
    return stats


def get_cached_live_game_stats() -> CachedLiveGameStats:
    red = get_redis_client()
    stats = red.get("LIVE_GAME_STATS")
    if stats:
        stats = pickle.loads(stats)
    return stats


def get_stat_post_processor(key: StatTypes):
    if key in (
        StatTypes.what_is_a_break,
        StatTypes.survivors,
    ):
        return lambda v: round(v / 60, 2)
    else:
        return lambda v: v


def get_stat(
    stats: list[PlayerStatsType],
    key: StatTypes,
    limit: int,
    post_process: Callable | None = None,
    reverse: bool | None = None,
) -> list[PlayerStatsType]:
    if key in (StatTypes.u_r_still_a_man,):
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

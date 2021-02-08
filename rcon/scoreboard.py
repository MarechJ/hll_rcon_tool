import datetime
import re
import logging
from dataclasses import dataclass

from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.game_logs import get_recent_logs
from rcon.cache_utils import ttl_cache

logger = logging.getLogger(__name__)

@dataclass
class Streaks:
    kill: int = 0
    death: int = 0
    teamkills: int = 0
    deaths_by_tk: int = 0


class LiveStats:
    def __init__(self):
        self.rcon = RecordedRcon(SERVER_INFO)
        self.voted_yes_regex = re.compile('.*PV_Favour.*')
        self.voted_no_regex = re.compile('.*PV_Against.*')

    def _get_player_session_time(self, player):
        if not player or not player.get('profile'):
            return -1
        return player.get("profile", {}).get("current_playtime_seconds", 0)

    def _is_log_from_current_session(self, now, player, log):
        return log['timestamp_ms'] >= (now.timestamp() - self._get_player_session_time(player)) * 1000

    def _get_indexed_logs_by_player_for_session(self, now, indexed_players, logs):
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
            logger.warning("Log line does not belong to player '%s' line: '%s'", player["name"], log['raw'])

    def _add_kill(self, stats, player, log):
        self._add_kd('kills', 'deaths', stats, player, log)

    def _add_tk(self, stats, player, log):
        self._add_kd('teamkills', 'deaths_by_tk', stats, player, log)

    def _add_vote(self, stats, player, log):
        if self.voted_no_regex.match(log['raw']):
            stats['nb_voted_no'] += 1
        elif self.voted_yes_regex.match(log['raw']):
            stats['nb_voted_yes'] += 1
        else:
            logger.warning("VOTE log line does not match either vote yes or no regex: %s", log['raw'])
        
    def _add_vote_started(self, stats, player, log):
        stats['nb_vote_started'] += 1

    def _streaks_accumulator(self, player, log, stats, streaks):
        action = log['action']

        if action == 'KILL':
            if self._is_player_kill(player, log):
                stats['deaths_without_kill_streak'] = max(streaks.death, stats['deaths_without_kill_streak'])
                stats['teamkills_streak'] = max(streaks.teamkills, stats['teamkills_streak'])
                streaks.kill += 1
                streaks.death = 0
                streaks.teamkills = 0
            elif self._is_player_death(player, log):
                stats['kills_streak'] = max(streaks.kill, stats['kills_streak'])
                stats['deaths_by_tk_streak'] = max(streaks.deaths_by_tk, stats['deaths_by_tk_streak'])
                streaks.kill = 0
                streaks.deaths_by_tk = 0
                streaks.death += 1
        if action == 'TEAM KILL':
            if self._is_player_kill(player, log):
                streaks.teamkills += 1                    
            if self._is_player_death(player, log):
                streaks.deaths_by_tk += 1

    @ttl_cache(30)
    def get_current_players_stats(self):
        players = self.rcon.get_players()
        if not players:
            return {}

        oldest_session_seconds = self._get_player_session_time(max(players, key=self._get_player_session_time))
        now = datetime.datetime.now()
        min_timestamp = (now - datetime.timedelta(seconds=oldest_session_seconds)).timestamp()
        logs = get_recent_logs(min_timestamp=min_timestamp)

        indexed_players = {p["name"]: p for p in players}
        indexed_logs = self._get_indexed_logs_by_player_for_session(now, indexed_players, logs['logs'])      
        stats_by_player = {}

        actions_processors = {
            'KILL': self._add_kill,
            'TEAM KILL': self._add_tk,
            'VOTE STARTED': self._add_vote_started,
            'VOTE': self._add_vote,
        }
        for p in players:
            player_logs = indexed_logs.get(p["name"], [])
            stats = {
                "player": p["name"],
                "steam_id_64": p["steam_id_64"],
                "steaminfo": p.get("steaminfo"),
                'kills': 0,
                'kills_streak': 0,
                'deaths': 0,
                'deaths_without_kill_streak': 0,
                'teamkills': 0,
                'teamkills_streak': 0,
                'deaths_by_tk': 0,
                'deaths_by_tk_streak': 0,
                'nb_vote_started': 0,
                'nb_voted_yes': 0,
                'nb_voted_no': 0,
                'time_seconds': self._get_player_session_time(p)
            }

            streaks = Streaks()

            for l in player_logs:
                action = l['action']
                processor = actions_processors.get(action, lambda **kargs: None)
                processor(stats=stats, player=p, log=l)
                self._streaks_accumulator(p, l, stats, streaks)

            #stats = self._compute_stats(stats)
            stats_by_player[p["name"]] = self._compute_stats(stats)

        return stats_by_player

    def _compute_stats(self, stats):
        new_stats = dict(**stats)
        new_stats['kills_per_minute'] = round(stats['kills'] / max(stats['time_seconds'] / 60, 1), 2)
        new_stats['deaths_per_minute'] = round(stats['deaths'] / max(stats['time_seconds'] / 60, 1), 2)
        new_stats["kill_death_ratio"] = round(stats['kills'] / max(stats['deaths'], 1), 2)
        return new_stats

if __name__ == '__main__':
    from pprint import pprint

    pprint(LiveStats().get_current_players_stats())


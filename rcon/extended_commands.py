import random
from contextlib import contextmanager
from datetime import datetime, timedelta
import logging
import socket
from rcon.cache_utils import ttl_cache
from rcon.commands import ServerCtl, CommandFailedError


STEAMID = "steam_id_64"
NAME = "name"
ROLE = "role"


logger = logging.getLogger(__name__)


@contextmanager
def invalidates(*cached_funcs):
    yield None
    for f in cached_funcs:
        f.cache_clear()


class Rcon(ServerCtl):
    settings = (
        ('team_switch_cooldown', int),
        ('autobalance_threshold', int),
        ('idle_autokick_time', int), ('max_ping_autokick', int),
        ('queue_length', int), ('vip_slots_num', int)
    )

    @ttl_cache(ttl=60 * 60 * 24, cache_falsy=False)
    def get_player_info(self, player):
        try:
            raw = super().get_player_info(player)
            name, steam_id_64 = raw.split('\n')
            if not steam_id_64:
                return {}
        except CommandFailedError:
            logger.exception("Can't get player info for %s", player)
            return {}
        return {
            NAME: name.split(": ", 1)[-1],
            STEAMID: steam_id_64.split(": ", 1)[-1],
        }

    @ttl_cache(ttl=60 * 60 * 24)
    def get_admin_ids(self):
        res = super().get_admin_ids()
        admins = []
        for item in res:
            steam_id_64, role, name = item.split(" ", 2)
            admins.append(
                {
                    STEAMID: steam_id_64,
                    NAME: name[1:-1],
                    ROLE: role
                }
            )
        return admins
        
    def do_add_admin(self, steam_id_64, role, name):
        with invalidates(self.get_admin_ids):
            return super().do_add_admin(steam_id_64, role, name)

    def do_remove_admin(self, steam_id_64):
        with invalidates(self.get_admin_ids):
            return super().do_remove_admin(steam_id_64)

    @ttl_cache(ttl=5)
    def get_players(self):
        # We need a centralized cache or a
        # mutliprocess safe one to be able to invalidate the cache on
        # kick/ban actions
        names = super().get_players()
        return [
            {NAME: n, STEAMID: self.get_player_info(n).get(STEAMID)}
            for n in names
        ]

    @ttl_cache(ttl=60 * 60)
    def get_perma_bans(self):
        return super().get_perma_bans()

    @ttl_cache(ttl=60 * 60)
    def get_temp_bans(self):
        return super().get_temp_bans()

    def _struct_ban(self, ban, type_):
        name, time = ban.split(', banned on ')
        return {
            'type': type_,
            'name': name,
            # TODO check which timezone the server is using. Assuming UTC here.
            'timestamp': datetime.strptime(time, "%Y.%m.%d-%H.%M.%S").timestamp(),
            'raw': ban
        }

    def get_bans(self):
        temp_bans = [
            self._struct_ban(b, 'temp')
            for b in self.get_temp_bans()
        ]
        bans = [
            self._struct_ban(b, 'perma')
            for b in self.get_perma_bans()
        ]
        # Most recent first
        bans.reverse()
        return temp_bans + bans

    @ttl_cache(ttl=60 * 60)
    def get_vip_ids(self):
        res = super().get_vip_ids()
        l = []

        for item in res:
            try:
                steam_id_64, name = item.split(" ", 1)
                name = name.replace('"', "")
                name = name.replace("\n", "")
                name = name.strip()
            except ValueError:
                self._reconnect()
                raise
            l.append(dict(zip((STEAMID, NAME), (steam_id_64, name))))

        return l

    def do_remove_vip(self, steam_id_64):
        with invalidates(self.get_vip_ids):
            return super().do_remove_vip(steam_id_64)

    def do_add_vip(self, name, steam_id_64):
        with invalidates(self.get_vip_ids):
            return super().do_add_vip(steam_id_64, name)

    @ttl_cache(ttl=60)
    def get_next_map(self):
        current = self.get_map()
        rotation = self.get_map_rotation()
        next_id = rotation.index(current)
        next_id += 1
        if next_id == len(rotation):
            next_id = 0

        return rotation[next_id]

    def set_map(self, map_name):
        with invalidates(self.get_map):
            res = super().set_map(map_name)
            if res != 'SUCCESS':
                raise CommandFailedError(res)

    @ttl_cache(ttl=60 * 5)
    def get_map(self):
        return super().get_map()

    @ttl_cache(ttl=60 * 60)
    def get_name(self):
        return super().get_name()

    @ttl_cache(ttl=60 * 60)
    def get_team_switch_cooldown(self):
        return int(super().get_team_switch_cooldown())

    def set_team_switch_cooldown(self, minutes):
        with invalidates(self.get_team_switch_cooldown):
            return super().set_team_switch_cooldown(minutes)
    
    @ttl_cache(ttl=60 * 60)
    def get_autobalance_threshold(self):
        return int(super().get_autobalance_threshold())

    def set_autobalance_threshold(self, max_diff):
        with invalidates(self.get_autobalance_threshold):
            return super().set_autobalance_threshold(max_diff)
    
    @ttl_cache(ttl=60 * 60)
    def get_idle_autokick_time(self):
        return int(super().get_idle_autokick_time())

    def set_idle_autokick_time(self, minutes):
        with invalidates(self.get_idle_autokick_time):
            return super().set_idle_autokick_time(minutes)
    
    @ttl_cache(ttl=60 * 60)
    def get_max_ping_autokick(self):
        return int(super().get_max_ping_autokick())

    def set_max_ping_autokick(self, max_ms):
        with invalidates(self.get_max_ping_autokick):
            return super().set_max_ping_autokick(max_ms)

    @ttl_cache(ttl=60 * 60)
    def get_queue_length(self):
        return int(super().get_queue_length())

    def set_queue_length(self, num):
        with invalidates(self.get_queue_length):
            return super().set_queue_length(num)

    @ttl_cache(ttl=60 * 60)
    def get_vip_slots_num(self):
        return super().get_vip_slots_num()

    def set_vip_slots_num(self, num):
        with invalidates(self.get_vip_slots_num):
            return int(super().set_vip_slots_num(num))

    @ttl_cache(ttl=20)
    def get_slots(self):
        return super().get_slots()

    @ttl_cache(ttl=5, cache_falsy=False)
    def get_status(self):
        return {
            'name': self.get_name(),
            'map': self.get_map(),
            'nb_players': self.get_slots()
        }

    @ttl_cache(ttl=60 * 60 * 24)
    def get_maps(self):
        return super().get_maps()

    @ttl_cache(ttl=60 * 10, cache_falsy=False)
    def get_server_settings(self):
        settings = {}
        for name, type_ in self.settings:
            try:
                settings[name] = type_(getattr(self, f'get_{name}')())
            except: 
                logger.exception("Failed to retrieve settings %s", name)
                raise
        return settings


    def do_save_setting(self, name, value):
        if not name in dict(self.settings):
            raise ValueError(f"'{name}' can't be save with this method")

        with invalidates(self.get_server_settings):
            return getattr(self, f'set_{name}')(value)

    def _convert_relative_time(self, from_, time_str):
        time, unit = time_str.split(' ')
        if unit == 'ms':
            return from_ - timedelta(milliseconds=int(time))
        if unit == 'sec':
            return from_ - timedelta(seconds=float(time))
        if unit == 'min':
            minutes, seconds = time.split(':')
            return from_ - timedelta(minutes=float(minutes), seconds=float(seconds))
        if unit == 'hours':
            hours, minutes, seconds = time.split(':')
            return from_ - timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds)
            )

    @ttl_cache(ttl=10)
    def get_structured_logs(self, since_min_ago, filter_action=None, filter_player=None):
        try:
            raw = super().get_logs(since_min_ago)
        except socket.timeout:
            # The hll server just hangs when there are no logs for the requested time
            raw = ''

        now = datetime.now()
        res = []
        actions = set()
        players = set()
        for line in raw.split('\n'):
            if not line:
                continue
            try:
                time, rest = line.split('] ', 1)
                try:
                    # Bug: '[1:34:22 hours] DISCONNECTED ᚱ A V И E Ν : .',
                    action, content = rest.split(': ', 1)
                except ValueError:
                    action, content = rest.split(' ', 1)
                player, player2 = None, None
                if action in {'CONNECTED', 'DISCONNECTED'}:
                    player = content
                if action in {'KILL', 'TEAM KILL'}:
                    player, player2 = content.split(' -> ', 1)
                time = self._convert_relative_time(now, time[1:])
                players.add(player)
                players.add(player2)
                actions.add(action)
            except ValueError:
                logger.exception("Invalid line: '%s'", line)
                raise
            if filter_action and action != filter_action:
                continue
            if filter_player and filter_player not in line:
                continue

            res.append({
                'timestamp_ms': int(time.timestamp() * 1000),
                'relative_time_ms':  (time - now).total_seconds() * 1000,
                'raw': line,
                'action': action,
                'player': player,
                'player2': player2,
                'message': content
            })

        res.reverse()
        return {
            'actions': list(actions),
            'players': list(players),
            'logs': res
        }

    def do_kick(self, player, reason):
        with invalidates(self.get_players):
            return super().do_kick(player, reason)

    def do_temp_ban(self, player, reason):
        with invalidates(self.get_players, self.get_temp_bans):
            return super().do_temp_ban(player, reason)

    def do_remove_temp_ban(self, ban_log):
        with invalidates(self.get_temp_bans):
            return super().do_remove_temp_ban(ban_log)

    def do_remove_perma_ban(self, ban_log):
        with invalidates(self.get_perma_bans):
            return super().do_remove_perma_ban(ban_log)

    def do_perma_ban(self, player, reason):
        with invalidates(self.get_players, self.get_perma_bans):
            return super().do_perma_ban(player, reason)


    @ttl_cache(5)  # TODO cache longer
    def get_map_rotation(self):
        return super().get_map_rotation()

    def do_add_map_to_rotation(self, map_name):
        return self.do_add_maps_to_rotation([map_name])

    def do_remove_map_from_rotation(self, map_name):
        return self.do_remove_maps_from_rotation([map_name])

    def do_remove_maps_from_rotation(self, maps):
        with invalidates(self.get_map_rotation):
            for map_name in maps:
                super().do_remove_map_from_rotation(map_name)
            return 'SUCCESS'

    def do_add_maps_to_rotation(self, maps):
        with invalidates(self.get_map_rotation):
            for map_name in maps:
                super().do_add_map_to_rotation(map_name)
            return 'SUCCESS'

    def do_randomize_map_rotation(self, maps=None):
        maps = maps or self.get_maps()
        current = self.get_map_rotation()

        random.shuffle(maps)

        for m in maps:
            if m in current:
                self.do_remove_map_from_rotation(m)
            self.do_add_map_to_rotation(m)

        return maps

    @ttl_cache(ttl=60 * 2)
    def get_scoreboard(self, minutes=180, sort='ratio'):
        logs = self.get_structured_logs(minutes, 'KILL')
        scoreboard = []
        for player in logs['players']:
            if not player:
                continue
            kills = 0
            death = 0
            for log in logs['logs']:
                if log['player'] == player:
                    kills += 1
                elif log['player2'] == player:
                    death += 1
            if kills == 0 and death == 0:
                continue
            scoreboard.append({ 
                'player': player,
                '(real) kills': kills,
                '(real) death': death,
                'ratio': kills / max(death, 1)
            })

        scoreboard = sorted(
            scoreboard, key=lambda o: o[sort], reverse=True
        )
        for o in scoreboard:
            o["ratio"] = "%.2f" % o["ratio"]

        return scoreboard

if __name__ == '__main__':
    from rcon.settings import SERVER_INFO
    r = Rcon(SERVER_INFO)
    print(r.get_map_rotation())
    print(r.do_randomize_map_rotation())
    print(r.get_map_rotation())

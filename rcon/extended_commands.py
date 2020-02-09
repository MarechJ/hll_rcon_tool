import random
from contextlib import contextmanager
from datetime import datetime, timedelta
from cachetools.func import ttl_cache
import logging

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
    @ttl_cache(ttl=60 * 60)
    def get_player_info(self, player):
        raw = super().get_player_info(player)
        try:
            name, steam_id_64 = raw.split('\n')
        except ValueError:
            self._reconnect()
            return {
                NAME: player,
                STEAMID: None
            }
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

    @ttl_cache(ttl=5)
    def get_players(self):
        # We need a centralized cache or a
        # mutliprocess safe one to be able to invalidate the cache on
        # kick/ban actions
        names = super().get_players()
        return [
            self.get_player_info(n)
            for n in names
        ]

    @ttl_cache(ttl=60 * 5)
    def get_perma_bans(self):
        return super().get_perma_bans()

    @ttl_cache(ttl=60)
    def get_temp_bans(self):
        return super().get_temp_bans()

    def _struct_ban(self, ban, type_):
        name, time =  ban.split(', banned on ')
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
            except ValueError:
                self._reconnect()
                raise
            l.append(dict(zip((STEAMID, NAME), (steam_id_64, name))))

        return l

    @ttl_cache(ttl=60)
    def get_status(self):
        return {
            'map': self.get_map(),
            'nb_players': self.get_slots().split('/')[0]
        }

    @ttl_cache(ttl=60 * 10)
    def get_server_settings(self):
        settings = [
            'name', 'team_switch_cooldown',
            'autobalance_threshold', 'map_rotation',
            'idle_autokick_time', 'max_ping_autokick',
            'queue_length', 'vip_slots_num'
        ]
        return {
            s: getattr(self, f'get_{s}')()
            for s in settings
        }

    def _convert_relative_time(self, from_, time_str):
        time, unit  = time_str.split(' ')
        if unit == 'ms':
            return from_ - timedelta(milliseconds=int(time))
        if unit == 'sec':
            return from_ - timedelta(seconds=float(time))
        if unit == 'hours':
            hours, minutes, seconds = time.split(':')
            return from_ - timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds)
            )

    def get_structured_logs(self, since_min_ago, filter_action=None, filter_player=None):
        raw = super().get_logs(since_min_ago)
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

            res.append({
                'time': time,
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

    def do_perma_ban(self, player, reason):
        with invalidates(self.get_players, self.get_perma_bans):
            return super().do_perma_ban(player, reason)

    def do_randomize_map_rotation(self, maps=None):
        maps = maps or self.get_maps()
        current = self.get_map_rotation()

        random.shuffle(maps)

        for m in maps:
            if m in current:
                print(self.do_remove_map_from_rotation(m))
            print(self.do_add_map_to_rotation(m))

        return maps


if __name__ == '__main__':
    from rcon.settings import SERVER_INFO
    r = Rcon(SERVER_INFO)
    print(r.get_map_rotation())
    print(r.do_randomize_map_rotation())
    print(r.get_map_rotation())

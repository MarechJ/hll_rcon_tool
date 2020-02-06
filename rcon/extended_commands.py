import random

from cachetools.func import ttl_cache

from rcon.commands import ServerCtl, CommandFailedError


STEAMID = "steam_id_64"
NAME = "name"
ROLE = "role"


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

    def get_players(self):
        names = super().get_players()
        return [
            self.get_player_info(n)
            for n in names
        ]

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

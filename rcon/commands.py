import logging
import socket
from functools import wraps
import time

from dataclasses import dataclass
from functools import wraps

from rcon.connection import HLLConnection

logger = logging.getLogger(__name__)

def escape_string(s):
    """ Logic taken from the official rcon client.
    There's probably plenty of nicer and more bulletproof ones
    """
    st = ""
    for index in range(len(s)):
        st = (st + s[index] if s[index] != '\\' else st + "\\\\") if s[index] != '"' else st + "\\\""
    return st


def _escape_params(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(
            args[0],
            *[escape_string(a) for a in args[1:]],
            **{k: escape_string(v) for k, v in kwargs.items()}
        )
    return wrapper


class CommandFailedError(Exception):
    pass


class HLLServerError(Exception):
    pass


def _auto_retry(method):
    @wraps(method)
    def wrap(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except HLLServerError:
            if not self.auto_retry:
                raise
            logger.exception(
                "Auto retrying %s %s %s", method.__name__, args, kwargs
            )
            self._reconnect()
            return method(self, *args, **kwargs)
            # TODO loop and counter implement counter

    return wrap


class ServerCtl:
    """TODO: Use string format instead of interpolation as it could be a
    security risk

    set password not implemented on purpose
    """
    def __init__(self, config, auto_retry=1):
        self.config = config
        self._connect()
        self.auto_retry = auto_retry

    def _connect(self):
        self.conn = HLLConnection()
        self.conn.connect(
            self.config['host'],
            self.config['port'],
            self.config['password']
        )

    def _reconnect(self):
        logger.warning("reconnecting")
        self.conn.close()
        time.sleep(1)
        self._connect()

    @_auto_retry
    def _request(self, command: str, can_fail=True):
        logger.debug(command)
        try:
            self.conn.send(command.encode())
            result = self.conn.receive().decode()
        except (RuntimeError, BrokenPipeError, socket.timeout, ConnectionResetError):
            logger.exception("Failed request")
            raise HLLServerError(command)

        if result == 'FAIL':
            if can_fail:
                raise CommandFailedError(command)
            else:
                raise HLLServerError(f"Got FAIL for {command}")

        return result

    def _read_list(self, raw):
        res = raw.split('\t')

        try:
            expected_len = int(res[0])
        except ValueError:
            raise HLLServerError(
                "Unexpected response from server."
                "Unable to get list length"
            )

        # Max 30 tries
        for i in range(30):
            if expected_len <= len(res) - 1:
                break
            raw += self.conn.receive().decode()
            res = raw.split('\t')

        if res[-1] == '':
            # There's a trailin \t
            res = res[:-1]
        if expected_len < len(res) - 1:
            raise HLLServerError(
                "Server returned incomplete list,"
                f" expected {expected_len} got {len(res) - 1}"
            )

        return res[1:]

    @_auto_retry
    def _get(self, item, is_list=False, can_fail=True):
        res = self._request(f"get {item}", can_fail)

        if not is_list:
            return res

        return self._read_list(res)

    def get_name(self):
        return self._get("name", can_fail=False)

    def get_map(self):
        # server adds a _RESTART suffix after the name when the map is
        # loading
        return self._get("map", can_fail=False)

    def get_maps(self):
        return self._get("mapsforrotation", True, can_fail=False)

    def get_players(self):
        return self._get("players", True, can_fail=False)

    def get_player_info(self, player):
        return self._request(f'playerinfo {player}')

    def get_admin_ids(self):
        return self._get("adminids", True, can_fail=False)

    def get_temp_bans(self):
        return self._get("tempbans", True, can_fail=False)

    def get_perma_bans(self):
        return self._get("permabans", True, can_fail=False)

    def get_team_switch_cooldown(self):
        return self._get("teamswitchcooldown", can_fail=False)

    def get_autobalance_threshold(self):
        return self._get("autobalancethreshold", can_fail=False)

    def get_map_rotation(self):
        return self._request('rotlist', can_fail=False).split('\n')[:-1]

    def get_slots(self):
        return self._get("slots", can_fail=False)

    def get_vip_ids(self):
        return self._get("vipids", True, can_fail=False)

    def get_admin_groups(self):
        return self._get("admingroups", True, can_fail=False)

    @_auto_retry
    def get_logs(self, since_min_ago, filter_=''):
        res = self._request(f'showlog {since_min_ago}')
        for i in range(30):
            if res[-1] == '\n':
                break
            res += self.conn.receive().decode()
        return res

    def get_idle_autokick_time(self):
        return self._get("idletime", can_fail=False)

    def get_max_ping_autokick(self):
        return self._get('highping', can_fail=False)

    def get_queue_length(self):
        return self._get("maxqueuedplayers", can_fail=False)

    def get_vip_slots_num(self):
        return self._get("numvipslots", can_fail=False)

    def set_autobalance(self, bool_str):
        """
        String bool is on / off
        """
        return self._request(f'setautobalanceenabled {bool_str}')

    def set_welcome_message(self, msg):
        return self._request(f"say {msg}")

    def set_map(self, map_name):
        return self._request(f"map {map_name}")

    def set_idle_autokick_time(self, minutes):
        return self._request(f"setkickidletime {minutes}")

    def set_max_ping_autokick(self, max_ms):
        return self._request(f"sethighping {max_ms}")

    def set_autobalance_threshold(self, max_diff: int):
        return self._request(f"setautobalancethreshold {max_diff}")

    def set_team_switch_cooldown(self, minutes):
        return self._request(f"setteamswitchcooldown {minutes}")

    def set_queue_length(self, num):
        return self._request(f"setmaxqueuedplayers {num}")

    def set_vip_slots_num(self, num):
        return self._request(f"setnumvipslots {num}")

    @_escape_params
    def set_broadcast(self, msg):
        return self._request(f'broadcast "{msg}"')

    def do_switch_player_on_death(self, player):
        return self._request(f'switchteamondeath {player}')

    def do_switch_player_now(self, player):
        return self._request(f'switchteamnow {player}')

    def do_add_map_to_rotation(self, map_name):
        return self._request(f"rotadd {map_name}")

    def do_remove_map_from_rotation(self, map_name):
        return self._request(f"rotdel {map_name}")

    @_escape_params
    def do_punish(self, player, reason):
        return self._request(f'punish "{player}" "{reason}"')

    @_escape_params
    def do_kick(self, player, reason):
        return self._request(f'kick "{player}" "{reason}"')

    @_escape_params
    def do_temp_ban(self, player, reason):
        return self._request(f'tempban "{player}" "{reason}"')

    @_escape_params
    def do_perma_ban(self, player, reason):
        return self._request(f'permaban "{player}" "{reason}"')

    def do_remove_temp_ban(self, ban_log):
        return self._request(f"pardontempban {ban_log}")

    def do_remove_perma_ban(self, ban_log):
        return self._request(f"pardonpermaban {ban_log}")

    @_escape_params
    def do_add_admin(self, steam_id_64, role, name):
        return self._request(f'adminadd "{steam_id_64}" "{role}" "{name}"')

    def do_remove_admin(self, steam_id_64):
        return self._request(f'admindel {steam_id_64}')

    @_escape_params
    def do_add_vip(self, steam_id_64, name):
        return self._request(f'vipadd {steam_id_64} "{name}"')

    def do_remove_vip(self, steam_id_64):
        return self._request(f'vipdel {steam_id_64}')


if __name__ == '__main__':
    import os
    from rcon.settings import SERVER_INFO

    ctl = ServerCtl(
        SERVER_INFO
    )

    player = '[CFr] Dr.WeeD "blah"'
    print(ctl.do_kick(player, "test"))

import logging
import socket
import time
from functools import wraps
from typing import List

from rcon.connection import HLLConnection

logger = logging.getLogger(__name__)


def escape_string(s):
    """Logic taken from the official rcon client.
    There's probably plenty of nicer and more bulletproof ones
    """
    if not isinstance(s, str):
        return s
    st = ""
    for index in range(len(s)):
        st = (
            (st + s[index] if s[index] != "\\" else st + "\\\\")
            if s[index] != '"'
            else st + '\\"'
        )
    return st


def _escape_params(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(
            args[0],
            *[escape_string(a) for a in args[1:]],
            **{k: escape_string(v) for k, v in kwargs.items()},
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
        except (HLLServerError, UnicodeDecodeError):
            if not self.auto_retry:
                raise
            time.sleep(5)
            logger.exception("Auto retrying %s %s %s", method.__name__, args, kwargs)

            try:
                return method(self, *args, **kwargs)
            except (HLLServerError, UnicodeDecodeError):
                self._reconnect()
                raise
            # TODO loop and counter implement counter

    return wrap


class ServerCtl:
    """TODO: Use string format instead of interpolation as it could be a
    security risk

    set password not implemented on purpose
    """

    def __init__(self, config, auto_retry=1):
        # .env fed config from rcon.SERVER_INFO
        self.config = config
        self.conn = None
        # self._connect()
        self.auto_retry = auto_retry

    def _connect(self):
        self.conn = HLLConnection()
        try:
            self.conn.connect(
                self.config["host"], int(self.config["port"]), self.config["password"]
            )
        except (TypeError, ValueError) as e:
            logger.critical("Invalid connection information")
            raise

    def _reconnect(self):
        logger.warning("reconnecting")

        self.conn.close()
        time.sleep(2)
        self._connect()

    @_auto_retry
    def _request(self, command: str, can_fail=True, log_info=False, decode=True):
        if not self.conn:
            self._connect()
        if log_info:
            logger.info(command)
        else:
            logger.debug(command)
        try:
            self.conn.send(command.encode())
            if decode:
                result = self.conn.receive().decode()
            else:
                result = self.conn.receive()
        except (
            RuntimeError,
            BrokenPipeError,
            socket.timeout,
            ConnectionResetError,
            UnicodeDecodeError,
        ) as e:
            logger.exception("Failed request")
            raise HLLServerError(command) from e

        if (decode and result == "FAIL") or (not decode and result == b"FAIL"):
            if can_fail:
                raise CommandFailedError(command)
            else:
                raise HLLServerError(f"Got FAIL for {command}")

        return result

    @_auto_retry
    def _timed_request(self, command: str, can_fail=True, log_info=False):
        if log_info:
            logger.info(command)
        else:
            logger.debug(command)
        try:
            before_sent, after_sent, _ = self.conn.send(command.encode(), timed=True)
            before_received, after_received, result = self.conn.receive(timed=True)
            result = result.decode()
        except (
            RuntimeError,
            BrokenPipeError,
            socket.timeout,
            ConnectionResetError,
            UnicodeDecodeError,
        ):
            logger.exception("Failed request")
            raise HLLServerError(command)

        if result == "FAIL":
            if can_fail:
                raise CommandFailedError(command)
            else:
                raise HLLServerError(f"Got FAIL for {command}")

        return dict(
            before_sent=before_sent,
            after_sent=after_sent,
            before_received=before_received,
            after_received=after_received,
            result=result,
        )

    def _read_list(self, raw):
        res = raw.split(b"\t")

        try:
            expected_len = int(res[0])
            logger.debug("Expected list length %s", expected_len)
        except ValueError:
            raise HLLServerError(
                "Unexpected response from server." "Unable to get list length"
            )

        self.conn.lock()
        # Max 30 tries
        for i in range(1000):
            if expected_len <= len(res) - 1 and raw[-1] in [0, 9, 10]:  # \0 \t or \n
                logger.debug(
                    "List seems complete length is %s/%s last char is %s",
                    len(res),
                    expected_len,
                    raw[-1],
                )
                break
            logger.debug(
                "Reading again list length is %s/%s last char is %s",
                len(res),
                expected_len,
                raw[-1],
            )
            raw += self.conn.receive(unlock=False)
            res = raw.split(b"\t")
            # logger.warning(f"{res}|")

        self.conn.unlock()

        if res[-1] == b"":
            # There's a trailin \t
            res = res[:-1]
        if expected_len < len(res) - 1:
            raise HLLServerError(
                "Server returned incomplete list,"
                f" expected {expected_len} got {len(res) - 1}"
            )

        return [l.decode() for l in res[1:]]

    @_auto_retry
    def _get(self, item, is_list=False, can_fail=True):
        res = self._request(f"get {item}", can_fail, decode=not is_list)

        if not is_list:
            return res

        return self._read_list(res)

    def get_profanities(self):
        return self._get("profanity", is_list=True, can_fail=False)

    def do_ban_profanities(self, profanities_csv):
        return self._request(f"BanProfanity {profanities_csv}")

    def do_unban_profanities(self, profanities_csv):
        return self._request(f"UnbanProfanity {profanities_csv}")

    def get_name(self):
        return self._get("name", can_fail=False)

    def get_map(self):
        # server adds a _RESTART suffix after the name when the map is
        # loading
        return self._get("map", can_fail=False)

    def get_maps(self):
        return sorted(self._get("mapsforrotation", True, can_fail=False))

    def get_players(self):
        return self._get("players", True, can_fail=False)

    def get_playerids(self):
        return self._get("playerids", True, can_fail=False)

    def _is_info_correct(self, player, raw_data):
        try:
            lines = raw_data.split("\n")
            return lines[0] == f"Name: {player}"
        except Exception:
            logger.exception("Bad playerinfo data")
            return False

    def get_player_info(self, player, can_fail=True):
        data = self._request(f"playerinfo {player}", can_fail=can_fail)
        if not self._is_info_correct(player, data):
            data = self._request(f"playerinfo {player}", can_fail=can_fail)
        if not self._is_info_correct(player, data):
            raise CommandFailedError(
                "The game server is returning the wrong player info for %s we got %s",
                player,
                data,
            )
        return data

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

    def get_votekick_enabled(self):
        return self._get("votekickenabled", can_fail=False)

    def get_votekick_threshold(self):
        return self._get("votekickthreshold", can_fail=False)

    def get_map_rotation(self):
        return self._request("rotlist", can_fail=False).split("\n")[:-1]

    def get_slots(self):
        return self._get("slots", can_fail=False)

    def get_vip_ids(self):
        return self._get("vipids", True, can_fail=False)

    def get_admin_groups(self):
        return self._get("admingroups", True, can_fail=False)

    def get_autobalance_enabled(self):
        return self._get("autobalanceenabled", can_fail=False)

    @_auto_retry
    def get_logs(self, since_min_ago, filter_=""):
        res = self._request(f"showlog {since_min_ago}")
        if res == "EMPTY":
            return ""
        self.conn.lock()
        try:
            for i in range(30):
                if res[-1] == "\n":
                    break
                try:
                    res += self.conn.receive(unlock=False).decode()
                except (
                    RuntimeError,
                    BrokenPipeError,
                    socket.timeout,
                    ConnectionResetError,
                    UnicodeDecodeError,
                ):
                    logger.exception("Failed request")
                    raise HLLServerError(f"showlog {since_min_ago}")
        finally:
            self.conn.unlock()
        return res

    def get_timed_logs(self, since_min_ago, filter_=""):
        res = self._timed_request(f"showlog {since_min_ago}")
        for i in range(30):
            if res["result"][-1] == "\n":
                break
            res["result"] += self.conn.receive().decode()
        return res

    def get_idle_autokick_time(self):
        return self._get("idletime", can_fail=False)

    def get_max_ping_autokick(self):
        return self._get("highping", can_fail=False)

    def get_queue_length(self):
        return self._get("maxqueuedplayers", can_fail=False)

    def get_vip_slots_num(self):
        return self._get("numvipslots", can_fail=False)

    def set_autobalance_enabled(self, bool_str):
        """
        String bool is on / off
        """
        return self._request(f"setautobalanceenabled {bool_str}")

    def set_welcome_message(self, msg):
        return self._request(f"say {msg}", log_info=True, can_fail=False)

    def set_map(self, map_name):
        return self._request(f"map {map_name}", log_info=True)

    def set_idle_autokick_time(self, minutes):
        return self._request(f"setkickidletime {minutes}", log_info=True)

    def set_max_ping_autokick(self, max_ms):
        return self._request(f"sethighping {max_ms}", log_info=True)

    def set_autobalance_threshold(self, max_diff: int):
        return self._request(f"setautobalancethreshold {max_diff}", log_info=True)

    def set_team_switch_cooldown(self, minutes):
        return self._request(f"setteamswitchcooldown {minutes}", log_info=True)

    def set_queue_length(self, num):
        return self._request(f"setmaxqueuedplayers {num}", log_info=True)

    def set_vip_slots_num(self, num):
        return self._request(f"setnumvipslots {num}", log_info=True)

    @_escape_params
    def set_broadcast(self, msg):
        return self._request(f'broadcast "{msg}"', log_info=True, can_fail=False)

    def set_votekick_enabled(self, bool_str):
        """
        String bool is on / off
        """
        return self._request(f"setvotekickenabled {bool_str}")

    def set_votekick_threshold(self, threshold_pairs_str):
        """
        PlayerCount,Threshold[,PlayerCount,Threshold,...]
        """
        return self._request(f"setvotekickthreshold {threshold_pairs_str}")

    def do_reset_votekick_threshold(self):
        return self._request(f"resetvotekickthreshold", log_info=True)

    def do_switch_player_on_death(self, player):
        return self._request(f"switchteamondeath {player}", log_info=True)

    def do_switch_player_now(self, player):
        return self._request(f"switchteamnow {player}", log_info=True)

    def do_add_map_to_rotation(
        self,
        map_name: str,
        after_map_name: str = None,
        after_map_name_number: str = None,
    ):
        cmd = f"rotadd {map_name}"
        if after_map_name:
            cmd = f"{cmd} {after_map_name}"
            if after_map_name_number:
                cmd = f"{cmd} {after_map_name_number}"

        return self._request(cmd, can_fail=False, log_info=True)

    def do_remove_map_from_rotation(self, map_name, map_number: str = None):
        cmd = f"rotdel {map_name}"
        if map_number:
            cmd = f"{cmd} {map_number}"

        return self._request(cmd, can_fail=False, log_info=True)

    @_escape_params
    def do_punish(self, player, reason):
        return self._request(f'punish "{player}" "{reason}"', log_info=True)

    @_escape_params
    def do_kick(self, player, reason):
        return self._request(f'kick "{player}" "{reason}"', log_info=True)

    @_escape_params
    def do_temp_ban(
        self,
        player_name=None,
        steam_id_64=None,
        duration_hours=2,
        reason="",
        admin_name="",
    ):
        return self._request(
            f'tempban "{steam_id_64 or player_name}" {duration_hours} "{reason}" "{admin_name}"',
            log_info=True,
        )

    @_escape_params
    def do_perma_ban(
        self, player_name=None, steam_id_64=None, reason="", admin_name=""
    ):
        return self._request(
            f'permaban "{steam_id_64 or player_name}" "{reason}" "{admin_name}"',
            log_info=True,
        )

    def do_remove_temp_ban(self, ban_log):
        return self._request(f"pardontempban {ban_log}", log_info=True)

    def do_remove_perma_ban(self, ban_log):
        return self._request(f"pardonpermaban {ban_log}", log_info=True)

    @_escape_params
    def do_add_admin(self, steam_id_64, role, name):
        return self._request(
            f'adminadd "{steam_id_64}" "{role}" "{name}"', log_info=True
        )

    def do_remove_admin(self, steam_id_64):
        return self._request(f"admindel {steam_id_64}", log_info=True)

    @_escape_params
    def do_add_vip(self, steam_id_64, name):
        return self._request(f'vipadd {steam_id_64} "{name}"', log_info=True)

    def do_remove_vip(self, steam_id_64):
        return self._request(f"vipdel {steam_id_64}", log_info=True)

    @_escape_params
    def do_message_player(self, player=None, steam_id_64=None, message=""):
        return self._request(
            f'message "{steam_id_64 or player}" {message}',
            log_info=True,
        )

    def get_gamestate(self) -> List[str]:
        """
        Players: Allied: 0 - Axis: 1
        Score: Allied: 2 - Axis: 2
        Remaining Time: 0:11:51
        Map: foy_warfare
        Next Map: stmariedumont_warfare

        """
        # Has no trailing "\n"

        result = self._get("gamestate", can_fail=False)
        logger.debug("Gamestate results:\n|%s|", result)
        return result.split("\n")


if __name__ == "__main__":
    import os

    from rcon.settings import SERVER_INFO

    ctl = ServerCtl(SERVER_INFO)

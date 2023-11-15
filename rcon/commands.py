import logging
import socket
import threading
import time
from contextlib import contextmanager, nullcontext
from functools import wraps
from typing import List

from rcon.connection import HLLConnection
from rcon.types import ServerInfoType, VipId
from rcon.utils import exception_in_chain

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


class BrokenHllConnection(Exception):
    pass


def _auto_retry(method):
    @wraps(method)
    def wrap(self, *args, **kwargs):
        parent_connection = False
        if "conn" not in kwargs or kwargs["conn"] is None:
            logger.debug("auto-retry: acquiring connection from pool")
            connection = self.with_connection()
            kwargs["conn"] = connection
        else:
            parent_connection = True
            logger.debug("using passed in connection")
            connection = nullcontext(enter_result=kwargs["conn"])

        try:
            with connection as conn:
                kwargs["conn"] = conn
                return method(self, *args, **kwargs)
        except (HLLServerError, UnicodeDecodeError, OSError):
            if not self.auto_retry or parent_connection:
                raise
            time.sleep(5)
            logger.exception("Auto retrying %s %s %s", method.__name__, args, kwargs)

            logger.debug("auto-retry: acquiring new connection for retry from pool")
            with self.with_connection() as conn:
                kwargs["conn"] = conn
                try:
                    return method(self, *args, **kwargs)
                except (HLLServerError, UnicodeDecodeError, OSError) as e:
                    raise BrokenHllConnection from e
                # TODO loop and counter implement counter

    return wrap


class ServerCtl:
    """TODO: Use string format instead of interpolation as it could be a
    security risk

    set password not implemented on purpose
    """

    def __init__(
        self, config: ServerInfoType, auto_retry=1, max_open=20, max_idle=20
    ) -> None:
        self.maxOpen: int = max_open
        self.maxIdle: int = max_idle
        self.config = config
        self.auto_retry = auto_retry
        self.mu = threading.Lock()
        self.idles: list[HLLConnection] = []
        self.numOpen = 0

    @contextmanager
    def with_connection(self) -> HLLConnection:
        logger.debug("Waiting to acquire lock %s", threading.get_ident())
        if not self.mu.acquire(timeout=30):
            raise TimeoutError()

        if len(self.idles) != 0:
            conn = self.idles.pop()
            logger.debug("acquiring connection from idle pool: %s", conn.id)
            self.mu.release()

        elif self.numOpen >= self.maxOpen:
            logger.debug(
                "Max connections already open, waiting for connection returned to pool"
            )
            c = 0
            idle_len = len(self.idles)
            self.mu.release()
            while idle_len == 0:
                if c >= 30:
                    logger.error(
                        "waiting for connection returned to pool timed out after %s seconds",
                        c,
                    )
                    raise TimeoutError()
                c += 1
                time.sleep(1)

                if not self.mu.acquire(timeout=30):
                    raise TimeoutError()
                idle_len = len(self.idles)
                self.mu.release()

            if not self.mu.acquire(timeout=30):
                raise TimeoutError()
            conn = self.idles.pop()
            logger.debug("connection appeared in pool: %s, acquiring it", conn.id)
            self.mu.release()

        else:
            conn = HLLConnection()
            logger.debug("Opening a new connection with ID %s", conn.id)
            try:
                self._connect(conn)
                self.numOpen += 1
            finally:
                self.mu.release()

        ex = None
        try:
            yield conn
        except Exception as e:
            # All other errors, that might be caught (like UnicodeDecodeError) do not really qualify as an error of the
            # connection itself. Instead of reconnecting the existing connection here (conditionally), we simply discard
            # the connection, assuming it is broken. The pool will establish a new connection when needed.
            if isinstance(e.__context__, RuntimeError | OSError) or exception_in_chain(
                e, OSError
            ):
                logger.warning(
                    "Connection (%s) errored in thread %s: %s, removing from pool",
                    conn.id,
                    threading.get_ident(),
                    e,
                )
                with self.mu:
                    self.numOpen -= 1
                conn.close()
                raise

            if exception_in_chain(e, BrokenHllConnection):
                logger.warning(
                    "Connection (%s) marked as broken in thread %s, removing from pool",
                    conn.id,
                    threading.get_ident(),
                )
                with self.mu:
                    self.numOpen -= 1
                conn.close()
                if e.__context__ is not None:
                    raise e.__context__
                raise e

            ex = e

        logger.debug(
            "return connection (%s) from thread %s", conn.id, threading.get_ident()
        )
        if len(self.idles) >= self.maxIdle:
            logger.debug("Enough connections in pool, closing %s", conn.id)
            with self.mu:
                self.numOpen -= 1
            conn.close()
        else:
            logger.debug("Returning connection (%s) to pool", conn.id)

            self.idles.append(conn)

        if ex is not None:
            raise ex

    def _connect(self, conn: HLLConnection):
        try:
            conn.connect(
                self.config["host"], int(self.config["port"]), self.config["password"]
            )
        except (TypeError, ValueError) as e:
            logger.exception("Invalid connection information", e)
            raise

    @_auto_retry
    def _request(
        self,
        command: str,
        can_fail=True,
        log_info=False,
        decode=True,
        conn: HLLConnection = None,
    ):
        if conn is None:
            raise ValueError("conn parameter should never be None")
        if log_info:
            logger.info(command)
        else:
            logger.debug(command)
        try:
            conn.send(command.encode())
            if decode:
                result = conn.receive().decode()
            else:
                result = conn.receive()
        except (
            RuntimeError,
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
    def _timed_request(
        self, command: str, can_fail=True, log_info=False, conn: HLLConnection = None
    ):
        if conn is None:
            raise ValueError("conn parameter should never be None")
        if log_info:
            logger.info(command)
        else:
            logger.debug(command)
        try:
            before_sent, after_sent, _ = conn.send(command.encode(), timed=True)
            before_received, after_received, result = conn.receive(timed=True)
            result = result.decode()
        except (
            RuntimeError,
            BrokenPipeError,
            socket.timeout,
            ConnectionResetError,
            UnicodeDecodeError,
        ) as e:
            logger.exception("Failed request")
            raise HLLServerError(command) from e

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

    def _read_list(self, raw, conn: HLLConnection):
        res = raw.split(b"\t")

        try:
            expected_len = int(res[0])
            logger.debug("Expected list length %s", expected_len)
        except ValueError:
            raise HLLServerError(
                "Unexpected response from server." "Unable to get list length"
            )

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
            raw += conn.receive()
            res = raw.split(b"\t")

        if res[-1] == b"":
            # There's a trailing \t
            res = res[:-1]
        if expected_len < len(res) - 1:
            raise HLLServerError(
                "Server returned incomplete list,"
                f" expected {expected_len} got {len(res) - 1}"
            )

        return [l.decode() for l in res[1:]]

    @_auto_retry
    def _get(self, item, is_list=False, can_fail=True, conn: HLLConnection = None):
        if conn is None:
            raise ValueError("conn parameter should never be None")
        res = self._request(f"get {item}", can_fail, decode=not is_list, conn=conn)

        if not is_list:
            return res

        return self._read_list(res, conn)

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
            raise BrokenHllConnection() from CommandFailedError(
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

    def get_vip_ids(self) -> List[VipId]:
        with self.with_connection() as conn:
            res = self._get("vipids", True, can_fail=False, conn=conn)

            vip_ids: List[VipId] = []
            for item in res:
                try:
                    steam_id_64, name = item.split(" ", 1)
                    name = name.replace('"', "")
                    name = name.replace("\n", "")
                    name = name.strip()
                    vip_ids.append(dict(steam_id_64=steam_id_64, name=name))
                except ValueError as e:
                    raise BrokenHllConnection() from e
            return vip_ids

    def get_admin_groups(self):
        return self._get("admingroups", True, can_fail=False)

    def get_autobalance_enabled(self):
        return self._get("autobalanceenabled", can_fail=False)

    @_auto_retry
    def get_logs(self, since_min_ago, filter_="", conn: HLLConnection = None):
        if conn is None:
            raise ValueError("conn parameter should never be None")
        res = self._request(f"showlog {since_min_ago}", conn=conn)
        if res == "EMPTY":
            return ""
        for i in range(30):
            if res[-1] == "\n":
                break
            try:
                res += conn.receive().decode()
            except (
                RuntimeError,
                BrokenPipeError,
                socket.timeout,
                ConnectionResetError,
                UnicodeDecodeError,
            ):
                logger.exception("Failed request")
                raise HLLServerError(f"showlog {since_min_ago}")

        return res

    def get_timed_logs(self, since_min_ago, filter_=""):
        with self.with_connection() as conn:
            res = self._timed_request(f"showlog {since_min_ago}", conn=conn)
            for i in range(30):
                if res["result"][-1] == "\n":
                    break
                res["result"] += conn.receive().decode()
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

    def get_current_map_sequence(self):
        return self._request("listcurrentmapsequence").split("\n")[:-1]

    def get_map_shuffle_enabled(self):
        return self._request("querymapshuffle").endswith("TRUE")

    def set_map_shuffle_enabled(self, enabled: bool):
        current = self.get_map_shuffle_enabled()
        if current != enabled:
            self._request(f"togglemapshuffle")

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
        after_map_name: str,
        after_map_name_number: int = None,
    ):
        cmd = f"rotadd /Game/Maps/{map_name} /Game/Maps/{after_map_name}"
        if after_map_name_number:
            cmd = f"{cmd} {after_map_name_number}"

        return self._request(cmd, can_fail=False, log_info=True)

    def do_remove_map_from_rotation(self, map_name, map_number: int = None):
        cmd = f"rotdel /Game/Maps/{map_name}"
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
        return result.split("\n")


if __name__ == "__main__":
    from rcon.settings import SERVER_INFO

    ctl = ServerCtl(SERVER_INFO)

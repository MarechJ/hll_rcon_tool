import logging
import threading
import time
from contextlib import contextmanager, nullcontext
from enum import StrEnum
from functools import wraps
from typing import Generator, Sequence, Any, List

from rcon.connection import HLLConnection, Response, HLLMessageError
from rcon.maps import LayerType
from rcon.types import ServerInfoType, VipId, GameStateType
from rcon.utils import exception_in_chain

logger = logging.getLogger(__name__)

SUCCESS = "SUCCESS"


class GameMode(StrEnum):
    Warfare = "Warfare"
    Offensive = "Offensive"
    Skirmish = "Skirmish"


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
    def with_connection(self) -> Generator[HLLConnection, None, None]:
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

    def _connect(self, conn: HLLConnection) -> None:
        try:
            conn.connect(
                self.config["host"], int(self.config["port"]), self.config["password"]
            )
        except (TypeError, ValueError) as e:
            logger.exception("Invalid connection information", e)
            raise

    @_auto_retry
    def request(
            self,
            command: str,
            content: dict[str, Any] | str = "",
            log_info=False,
            conn: HLLConnection | None = None,
    ) -> Response:
        if conn is None:
            raise ValueError("conn parameter should never be None")
        if log_info:
            logger.info(command)
        else:
            logger.debug(command)
        try:
            return conn.exchange(command, 2, content)
        except (
                RuntimeError,
                UnicodeDecodeError,
        ) as e:
            logger.exception("Failed request")
            raise HLLServerError(command) from e

    def get_profanities(self) -> list[str]:
        return self.request("GetServerInformation", {"Name": "bannedwords", "Value": ""}).content_dict["bannedWords"]

    def ban_profanities(self, profanities: str) -> bool:
        self.request("AddBannedWords", {"BannedWords": profanities})
        return True

    def unban_profanities(self, profanities: str) -> bool:
        self.request("RemoveBannedWords", {"BannedWords": profanities})
        return True

    def get_name(self) -> str:
        return self.request("GetServerInformation", {"Name": "session", "Value": ""}).content_dict["serverName"]

    def get_map(self) -> str:
        # TODO: Either get from the current map sequence or from session GetServerInformation, both needs to be validated
        return ""

    def get_maps(self) -> list[str]:
        # TODO: Not available right now
        return []

    def get_players(self) -> list[str]:
        # TODO: Overwritten in subclass, maybe there is a better way now with rconv2
        pass

    def get_playerids(self) -> list[str]:
        return [x["iD"] for x in self.request("GetServerInformation", {"Name": "players", "Value": ""}).content_dict["players"]]

    def get_player_info(self, player_name: str, can_fail=True) -> dict[str, str] | None:
        for p in self.request("GetServerInformation", {"Name": "players", "Value": ""}).content_dict["players"]:
            if p["name"] == player_name:
                return p
        return None

    def get_admin_ids(self) -> list[str]:
        return [x["UserId"] for x in self.request("GetAdminUsers").content_dict["AdminUsers"]]

    def get_temp_bans(self) -> list[str]:
        return [x["UserId"] for x in self.request("GetTemporaryBans").content_dict["banList"]]

    def get_perma_bans(self) -> list[str]:
        return [x["UserId"] for x in self.request("GetPermanentBans").content_dict["banList"]]

    def get_team_switch_cooldown(self) -> int:
        # TODO: Not available right now
        return 0

    def get_autobalance_threshold(self) -> int:
        # TODO: Not available right now
        return 0

    def get_votekick_enabled(self) -> bool:
        # TODO: Not available right now
        return False

    def get_votekick_thresholds(self) -> int:
        # TODO: Not available right now
        return 0

    def get_map_rotation(self) -> list[str]:
        # TODO: Not available right now
        return [x["iD"] for x in self.request("GetServerInformation", {"Name": "maprotation", "Value": ""}).content_dict["mAPS"]]

    def get_slots(self) -> str:
        # TODO: Not available right now
        return ""

    def get_vip_ids(self) -> list[VipId]:
        # TODO: Not available right now
        return []

    def get_admin_groups(self) -> list[str]:
        return self.request("GetAdminGroups").content_dict["groupNames"]

    def get_autobalance_enabled(self) -> bool:
        # TODO: Not available right now
        return False

    def get_logs(
            self,
            since_min_ago: str | int,
            filter_: str = "",
            conn: HLLConnection | None = None,
    ) -> str:
        # TODO: Returned an empty list of entries on my test server, recheck when actual rconv2 is available
        return "\n".join(self.request("GetAdminLog", {"LogBackTrackTime": since_min_ago}).content_dict["entries"])

    def get_idle_autokick_time(self) -> int:
        return 0

    def get_max_ping_autokick(self) -> int:
        # TODO: Not available right now
        return 0

    def get_queue_length(self) -> int:
        # TODO: Verify if this value is updated instantly or after the current session ends or any async time
        return self.request("GetServerInformation", {"Name": "session", "Value": ""}).content_dict["maxQueueCount"]

    def get_vip_slots_num(self) -> int:
        # TODO: Verify if this value is updated instantly or after the current session ends or any async time
        return self.request("GetServerInformation", {"Name": "session", "Value": ""}).content_dict["maxVipQueueCount"]

    def set_autobalance_enabled(self, value: bool) -> bool:
        self.request("SetAutoBalance", {"EnableAutoBalance": value})
        return True

    def set_welcome_message(self, message):
        self.request("SendServerMessage", {"Message": message})

    def set_map(self, map_name: str):
        self.request("ChangeMap", {"MapName": map_name})

    def get_current_map_sequence(self) -> list[str]:
        # TODO: No command to get this info right now
        return [x["iD"] for x in self.request("GetServerInformation", {"Name": "maprotation", "Value": ""}).content_dict["mAPS"]]

    def get_map_shuffle_enabled(self) -> bool:
        # TODO: No command to get this info right now
        return False

    def set_map_shuffle_enabled(self, enabled: bool) -> None:
        self.request("ShuffleMapSequence", {"Enable": enabled})

    def set_idle_autokick_time(self, minutes) -> bool:
        self.request("SetIdleKickDuration", {"IdleTimeoutMinutes": minutes})
        return True

    def set_max_ping_autokick(self, max_ms) -> bool:
        self.request("SetHighPingThreshold", {"HighPingThresholdMs": max_ms})
        return True

    def set_autobalance_threshold(self, max_diff: int):
        self.request("SetAutoBalanceThreshold", {"AutoBalanceThreshold": max_diff})
        return True

    def set_team_switch_cooldown(self, minutes: int) -> bool:
        self.request("SetTeamSwitchCooldown", {"TeamSwitchTimer": minutes})
        return True

    def set_queue_length(self, value: int) -> bool:
        self.request("SetMaxQueuedPlayers", {"MaxQueuedPlayers": value})
        return True

    def set_vip_slots_num(self, value: int) -> bool:
        self.request("SetVipSlotCount", {"VipSlotCount": value})
        return True

    @_escape_params
    def set_broadcast(self, message: str):
        self.request("ServerBroadcast", {"Message": message})

    def set_votekick_enabled(self, value: bool) -> bool:
        self.request("SetVoteKick", {"Enabled": value})
        return True

    def set_votekick_thresholds(self, threshold_pairs: str):
        self.request("ResetKickThreshold", {"ThresholdValue": threshold_pairs})

    def reset_votekick_thresholds(self) -> bool:
        self.request("ResetKickThreshold", {})
        return True

    def switch_player_on_death(self, player_id) -> bool:
        # TODO: player_name changed to player_id: Possibly the frontend needs to be changed as well
        self.request("ForceTeamSwitch", {"PlayerId": player_id, "ForceMode": 0})
        return True

    def switch_player_now(self, player_id: str) -> bool:
        # TODO: player_name changed to player_id: Possibly the frontend needs to be changed as well
        self.request("ForceTeamSwitch", {"PlayerId": player_id, "ForceMode": 1})
        return True

    def add_map_to_rotation(
            self,
            map_name: str,
            after_map_name: str,
            after_map_name_number: int | None = None,
    ):
        # TODO: Verify that index logic is correct (hint: it probably isn't)
        # TODO #2: Remove after_map_name argument
        self.request("AddMapFromRotation", {"MapName": map_name, "Index": after_map_name_number + 1})

    def remove_map_from_rotation(
            self, map_name: str, map_number: int | None = None
    ):
        # TODO: Change signature to remove map name as possible argument
        self.request("RemoveMapFromRotation", {"Index": map_number})

    @_escape_params
    def punish(self, player_id: str, reason: str) -> bool:
        self.request("PunishPlayer", {"PlayerId": player_id, "Reason": reason})
        return True

    @_escape_params
    def kick(self, player_id: str, reason: str) -> bool:
        self.request("KickPlayer", {"PlayerId": player_id, "Reason": reason})
        return True

    @_escape_params
    def temp_ban(
            self,
            player_name: str | None = None,
            player_id: str | None = None,
            duration_hours: int = 2,
            reason: str = "",
            admin_name: str = "",
    ) -> bool:
        self.request("TemporaryBanPlayer", {"PlayerId": player_id, "Duration": duration_hours, "Reason": reason, "AdminName": admin_name})
        return True

    @_escape_params
    def perma_ban(
            self,
            player_name: str | None = None,
            player_id: str | None = None,
            reason: str = "",
            admin_name: str = "",
    ) -> bool:
        self.request("PermanentBanPlayer", {"PlayerId": player_id, "Reason": reason, "AdminName": admin_name})
        return True

    def remove_temp_ban(self, player_id: str) -> bool:
        self.request("RemoveTemporaryBan", {"PlayerId": player_id})
        return True

    def remove_perma_ban(self, player_id: str) -> bool:
        self.request("RemovePermanentBan", {"PlayerId": player_id})
        return True

    @_escape_params
    def add_admin(self, player_id, role, description) -> bool:
        self.request("AddAdmin", {"PlayerId": player_id, "Description": description})
        return True

    def remove_admin(self, player_id) -> bool:
        self.request("RemoveAdmin", {"PlayerId": player_id})
        return True

    @_escape_params
    def add_vip(self, player_id: str, description: str) -> bool:
        self.request("AddVipPlayer", {"PlayerId": player_id, "Description": description})
        return True

    def remove_vip(self, player_id) -> bool:
        self.request("RemoveVipPlayer", {"PlayerId": player_id})
        return True

    @_escape_params
    def message_player(self, player_name=None, player_id=None, message=""):
        self.request("MessagePlayer", {"Message": message, "PlayerId": player_id})

    def get_gamestate(self) -> GameStateType:
        s = self.request("GetServerInformation", {"Name": "session", "Value": ""}).content_dict
        # TODO: next_map is not included in session, and map name needs to be parsed, if possible.
        return GameStateType(
            next_map=None,
            axis_score=s["AxisScore"],
            allied_score=s["AlliedScore"],
            current_map=LayerType(
                map=s["MapName"],
                game_mode=s["GameMode"],
            ),
            time_remaining=s["RemainingMatchTime"],
            num_axis_players=s["AxisPlayerCount"],
            num_allied_players=s["AlliedPlayerCount"],
            raw_time_remaining=s["RemainingMatchTime"],
        )

    def get_objective_row(self, row: int):
        if not (0 <= row <= 4):
            raise ValueError("Row must be between 0 and 4")

        return self.get_objective_rows()[row]

    def get_objective_rows(self) -> List[List[str]]:
        details = self.request("GetClientReferenceData", "SetSectorLayout")
        parameters = details.content_dict["dialogueParameters"]
        if not parameters or not all(
                p["iD"].startswith("Sector_") for p in parameters[:5]
        ):
            msg = "Received unexpected response from server."
            raise HLLMessageError(msg)

        return [
            parameters[0]["valueMember"].split(","),
            parameters[1]["valueMember"].split(","),
            parameters[2]["valueMember"].split(","),
            parameters[3]["valueMember"].split(","),
            parameters[4]["valueMember"].split(","),
        ]

    def set_game_layout(self, objectives: Sequence[str]):
        if len(objectives) != 5:
            raise ValueError("5 objectives must be provided")
        print(self.request("SetSectorLayout", {
            "Sector_1": objectives[0],
            "Sector_2": objectives[1],
            "Sector_3": objectives[2],
            "Sector_4": objectives[3],
            "Sector_5": objectives[4],
        }).content)
        return list(objectives)

    def get_game_mode(self):
        """
        Any of "IntenseWarfare", "OffensiveWarfare", or ???
        """
        return self.request("GetServerInformation", {"Name": "session", "Value": ""}).content_dict["gameMode"]


    def set_match_timer(self, game_mode: GameMode, length: int):
        self.request("SetMatchTimer", {"GameMode": game_mode.value, "MatchLength": length})


    def remove_match_timer(self, game_mode: GameMode):
        self.request("RemoveMatchTimer", {"GameMode": game_mode.value})


    def set_warmup_timer(self, game_mode: GameMode, length: int):
        self.request("SetWarmupTimer", {"GameMode": game_mode.value, "WarmupLength": length})


    def remove_warmup_timer(self, game_mode: GameMode):
        self.request("RemoveWarmupTimer", {"GameMode": game_mode.value})


if __name__ == "__main__":
    from rcon.settings import SERVER_INFO

    ctl = ServerCtl(SERVER_INFO)

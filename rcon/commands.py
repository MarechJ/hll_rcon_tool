import logging
import threading
import time
from contextlib import contextmanager, nullcontext
from datetime import timedelta
from functools import wraps
from typing import Any, Generator, List, Literal, Sequence

from rcon.connection import Handle, HLLCommandError, HLLConnection, Response
from rcon.maps import LAYERS, MAPS, UNKNOWN_MAP_NAME, Environment, GameMode, LayerType
from rcon.types import (
    AdminType,
    GameStateType,
    MapSequenceResponse,
    ServerInfoType,
    SlotsType,
    VipIdType,
)
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


class HLLCommandFailedError(Exception):
    """Raised when a command fails"""

    pass


class HLLBrokenConnectionError(Exception):
    """Raised when the connection has broken and needs to be re-established"""


class ServerCtl:
    """TODO: Use string format instead of interpolation as it could be a
    security risk

    set password not implemented on purpose
    """

    def __init__(self, config: ServerInfoType, auto_retry=1) -> None:
        self.config = config
        self.auto_retry = auto_retry
        self.mu = threading.Lock()
        self.conns: dict[int, HLLConnection] = {}

    @contextmanager
    def with_connection(self) -> Generator[HLLConnection, None, None]:
        # TODO: Cleanup connections from threads that no longer exist

        thread_id = threading.get_ident()
        logger.debug("Waiting to acquire lock %s", thread_id)
        if not self.mu.acquire(timeout=30):
            raise TimeoutError()

        try:
            conn = self.conns.get(thread_id)
            if conn is None:
                conn = HLLConnection()
                try:
                    self._connect(conn)
                except Exception:
                    raise
                self.conns[thread_id] = conn
        finally:
            self.mu.release()

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
                    "Connection (%s) errored in thread %s: %s, removing",
                    conn.id,
                    thread_id,
                    e,
                )

                if not self.mu.acquire(timeout=30):
                    raise TimeoutError()

                try:
                    conn.close()
                    self.conns.pop(thread_id, None)
                finally:
                    self.mu.release()

                raise

            elif exception_in_chain(e, HLLBrokenConnectionError):
                logger.warning(
                    "Connection (%s) marked as broken in thread %s, removing",
                    conn.id,
                    thread_id,
                )

                if not self.mu.acquire(timeout=30):
                    raise TimeoutError()

                try:
                    conn.close()
                    self.conns.pop(thread_id, None)
                finally:
                    self.mu.release()

                if e.__context__ is not None:
                    raise e.__context__
                raise

            else:
                raise

    def _connect(self, conn: HLLConnection) -> None:
        try:
            conn.connect(
                self.config["host"], int(self.config["port"]), self.config["password"]
            )
        except (TypeError, ValueError) as e:
            logger.exception("Invalid connection information", e)
            raise

    def send(
        self,
        command: str,
        version: int,
        content: dict[str, Any] | str = "",
        log_info=False,
        conn: HLLConnection | None = None,
    ) -> Handle:
        if conn is None:
            logger.debug("acquiring new connection")
            connection = self.with_connection()
        else:
            logger.debug("using passed in connection")
            connection = nullcontext(enter_result=conn)

        if log_info:
            logger.info("Sending command:", command, content)
        else:
            logger.debug("Sending command:", command, content)

        try:
            with connection as conn:
                return conn.send(command, version, content)
        except (
            RuntimeError,
            UnicodeDecodeError,
        ):
            if self.auto_retry is False or conn is not None:
                raise

            logger.exception(
                "Auto retrying send %s %s %s after 1 second", command, version, content
            )
            time.sleep(1)

            with connection as conn:
                return conn.send(command, version, content)

    def receive(
        self,
        handle: Handle,
    ) -> Response:
        try:
            response = handle.receive()
            response.raise_for_status()
            return response

        except (HLLCommandFailedError, UnicodeDecodeError, OSError) as e:
            if not self.auto_retry:
                raise

            if (
                isinstance(e, HLLCommandError)
                and e.status_code >= 400
                and e.status_code < 500
            ):
                # Client error, do not retry
                raise

            logger.exception("Failed %s, resending after 1 second", handle.request)
            time.sleep(1)

            with self.with_connection() as conn:
                response = conn.exchange(
                    handle.request.name,
                    handle.request.version,
                    handle.request.content,
                )
                handle._response = response
                response.raise_for_status()
                return response

    def receive_optional(
        self,
        handle: Handle,
        ignore_internal_errors: bool = False,
    ) -> Response | None:
        try:
            response = handle.receive()
            return response if response.is_successful() else None

        except (HLLCommandFailedError, UnicodeDecodeError, OSError) as e:
            if isinstance(e, HLLCommandError):
                if ignore_internal_errors:
                    return None

            if not self.auto_retry:
                raise

            logger.exception("Failed %s, resending after 1 second", handle.request)
            time.sleep(1)

            with self.with_connection() as conn:
                response = conn.exchange(
                    handle.request.name,
                    handle.request.version,
                    handle.request.content,
                )
                handle._response = response

                try:
                    return response if response.is_successful() else None
                except HLLCommandError as e:
                    return response if ignore_internal_errors else None

    def receive_success(
        self,
        handle: Handle,
        ignore_internal_errors: bool = False,
    ) -> bool:
        return self.receive_optional(handle, ignore_internal_errors) is not None

    def exchange(
        self,
        command: str,
        version: int,
        content: dict[str, Any] | str = "",
        log_info=False,
        conn: HLLConnection | None = None,
    ) -> Response:
        handle = self.send(command, version, content, log_info=log_info, conn=conn)
        return self.receive(handle)

    def exchange_optional(
        self,
        command: str,
        version: int,
        content: dict[str, Any] | str = "",
        log_info=False,
        conn: HLLConnection | None = None,
    ) -> Response | None:
        handle = self.send(command, version, content, log_info=log_info, conn=conn)
        return self.receive_optional(handle)

    def exchange_success(
        self,
        command: str,
        version: int,
        content: dict[str, Any] | str = "",
        log_info=False,
        conn: HLLConnection | None = None,
    ) -> bool:
        handle = self.send(command, version, content, log_info=log_info, conn=conn)
        return self.receive_success(handle)

    def get_profanities(self) -> list[str]:
        return self.exchange(
            "GetServerInformation", 2, {"Name": "bannedwords", "Value": ""}
        ).content_dict["bannedWords"]

    def ban_profanities(self, profanities: str) -> bool:
        self.exchange("AddBannedWords", 2, {"BannedWords": profanities})
        return True

    def unban_profanities(self, profanities: str) -> bool:
        self.exchange("RemoveBannedWords", 2, {"BannedWords": profanities})
        return True

    def get_name(self) -> str:
        return self.exchange(
            "GetServerInformation", 2, {"Name": "session", "Value": ""}
        ).content_dict["serverName"]

    def get_map(self) -> str:
        return self.get_gamestate()["current_map"]["id"]

    def get_maps(self) -> list[str]:
        details = self.exchange("GetClientReferenceData", 2, "AddMapToRotation")
        parameters = details.content_dict["dialogueParameters"]
        if not parameters or parameters[0]["iD"] != "MapName":
            raise HLLCommandFailedError("Received unexpected response from server.")
        return parameters[0]["valueMember"].split(",")

    def get_player_ids(self) -> dict[str, str]:
        # TODO: Updated function signatures
        return {
            x["name"]: x["iD"]
            for x in self.exchange(
                "GetServerInformation", 2, {"Name": "players", "Value": ""}
            ).content_dict["players"]
        }

    def get_all_player_info(self) -> list[dict[str, Any]]:
        # TODO: Updated function signatures
        return self.exchange(
            "GetServerInformation", 2, {"Name": "players", "Value": ""}
        ).content_dict["players"]

    def get_player_info(self, player_id: str, can_fail=True) -> dict[str, Any] | None:
        # TODO: Updated function signatures
        return self.exchange(
            "GetServerInformation", 2, {"Name": "player", "Value": player_id}
        ).content_dict

    def get_admin_ids(self) -> list[AdminType]:
        return [
            {
                "player_id": x["userId"],
                "name": x["comment"],
                "role": x["group"],
            }
            for x in self.exchange("GetAdminUsers", 2).content_dict["adminUsers"]
        ]

    def get_temp_bans(self) -> list[dict]:
        return self.exchange("GetTemporaryBans", 2).content_dict["banList"]

    def get_perma_bans(self) -> list[dict]:
        return self.exchange("GetPermanentBans", 2).content_dict["banList"]

    def get_team_switch_cooldown(self) -> int:
        return self.exchange("GetTeamSwitchCooldown", 2).content_dict["teamSwitchTimer"]

    def get_autobalance_threshold(self) -> int:
        return self.exchange("GetAutoBalanceThreshold", 2).content_dict[
            "autoBalanceThreshold"
        ]

    def get_votekick_enabled(self) -> bool:
        return self.exchange("GetVoteKickEnabled", 2).content_dict["enable"]

    def get_votekick_thresholds(self) -> list[list[int]]:
        thresholds = self.exchange("GetVoteKickThreshold", 2).content_dict[
            "voteThresholdList"
        ]
        return [[int(x["playerCount"]), int(x["voteThreshold"])] for x in thresholds]

    def get_map_rotation(self) -> list[str]:
        return [
            x["iD"]
            for x in self.exchange(
                "GetServerInformation", 2, {"Name": "maprotation", "Value": ""}
            ).content_dict["mAPS"]
        ]

    def get_map_sequence(self) -> MapSequenceResponse:
        data = self.exchange(
            "GetServerInformation", 2, {"Name": "mapsequence", "Value": ""}
        ).content_dict
        return {
            # Map[iD] can be in format as '/Game/Maps/driel_offensive_ger'
            "maps": [x["iD"].split("/")[-1] for x in data["mAPS"]],
            "current_index": data["currentIndex"],
        }

    def get_slots(self) -> SlotsType:
        resp = self.exchange(
            "GetServerInformation", 2, {"Name": "session", "Value": ""}
        ).content_dict

        return SlotsType(
            current_players=resp["playerCount"],
            max_players=resp["maxPlayerCount"],
        )

    def get_vip_ids(self) -> list[VipIdType]:
        return [
            VipIdType(player_id=vip["iD"], name=vip["comment"])
            for vip in self.exchange(
                "GetServerInformation", 2, {"Name": "vipplayers", "Value": ""}
            ).content_dict["vipPlayers"]
        ]

    def get_admin_groups(self) -> list[str]:
        return self.exchange("GetAdminGroups", 2).content_dict["groupNames"]

    def get_autobalance_enabled(self) -> bool:
        return self.exchange("GetAutoBalanceEnabled", 2).content_dict["enable"]

    def get_logs(
        self,
        since_min_ago: int,
        filter_: str = "",
        conn: HLLConnection | None = None,
    ) -> list[str]:
        return [
            entry["message"]
            for entry in self.exchange(
                "GetAdminLog",
                2,
                {"LogBackTrackTime": since_min_ago * 60, "Filters": filter_},
                conn=conn,
            ).content_dict["entries"]
        ]

    def get_idle_autokick_time(self) -> int:
        return self.exchange("GetKickIdleDuration", 2).content_dict[
            "idleTimeoutMinutes"
        ]

    def get_max_ping_autokick(self) -> int:
        return self.exchange("GetHighPingThreshold", 2).content_dict[
            "highPingThresholdMs"
        ]

    def get_queue_length(self) -> int:
        # TODO: Verify if this value is updated instantly or after the current session ends or any async time
        return self.exchange(
            "GetServerInformation", 2, {"Name": "session", "Value": ""}
        ).content_dict["maxQueueCount"]

    def get_vip_slots_num(self) -> int:
        # TODO: Verify if this value is updated instantly or after the current session ends or any async time
        return self.exchange(
            "GetServerInformation", 2, {"Name": "session", "Value": ""}
        ).content_dict["maxVipQueueCount"]

    def set_autobalance_enabled(self, value: bool) -> bool:
        self.exchange("SetAutoBalanceEnabled", 2, {"Enable": value})
        return True

    def set_welcome_message(self, message):
        self.exchange("SetWelcomeMessage", 2, {"Message": message})

    def set_map(self, map_name: str):
        self.exchange("ChangeMap", 2, {"MapName": map_name})

    def get_map_shuffle_enabled(self) -> bool:
        # TODO: No command to get this info right now
        return False

    def set_map_shuffle_enabled(self, enabled: bool) -> None:
        self.exchange("SetMapShuffleEnabled", 2, {"Enable": enabled})

    def set_idle_autokick_time(self, minutes) -> bool:
        self.exchange("SetIdleKickDuration", 2, {"IdleTimeoutMinutes": minutes})
        return True

    def set_max_ping_autokick(self, max_ms) -> bool:
        self.exchange("SetHighPingThreshold", 2, {"HighPingThresholdMs": max_ms})
        return True

    def set_autobalance_threshold(self, max_diff: int):
        self.exchange("SetAutoBalanceThreshold", 2, {"AutoBalanceThreshold": max_diff})
        return True

    def set_team_switch_cooldown(self, minutes: int) -> bool:
        self.exchange("SetTeamSwitchCooldown", 2, {"TeamSwitchTimer": minutes})
        return True

    def set_queue_length(self, value: int) -> bool:
        self.exchange("SetMaxQueuedPlayers", 2, {"MaxQueuedPlayers": value})
        return True

    def set_vip_slots_num(self, value: int) -> bool:
        self.exchange("SetVipSlotCount", 2, {"VipSlotCount": value})
        return True

    @_escape_params
    def set_broadcast(self, message: str):
        self.exchange("ServerBroadcast", 2, {"Message": message})

    def set_votekick_enabled(self, value: bool) -> bool:
        self.exchange("SetVoteKickEnabled", 2, {"Enable": value})
        return True

    def set_votekick_thresholds(self, threshold_pairs: str):
        self.exchange("SetVoteKickThreshold", 2, {"ThresholdValue": threshold_pairs})

    def reset_votekick_thresholds(self) -> bool:
        self.exchange("ResetVoteKickThreshold", 2, {})
        return True

    def switch_player_on_death(self, player_id: str) -> bool:
        # TODO: player_name changed to player_id: Possibly the frontend needs to be changed as well
        return self.exchange_success(
            "ForceTeamSwitch", 2, {"PlayerId": player_id, "ForceMode": 0}
        )

    def switch_player_now(self, player_id: str) -> bool:
        # TODO: player_name changed to player_id: Possibly the frontend needs to be changed as well
        return self.exchange_success(
            "ForceTeamSwitch", 2, {"PlayerId": player_id, "ForceMode": 1}
        )

    def remove_player_from_squad(self, player_id: str, reason: str) -> None:
        self.exchange_success(
            "RemovePlayerFromPlatoon", 2, {"PlayerId": player_id, "Reason": reason}
        )

    def disband_squad(self, team_index: int, squad_index: int, reason: str) -> None:
        self.exchange_success(
            "DisbandPlatoon",
            2,
            {"TeamIndex": team_index, "SquadIndex": squad_index, "Reason": reason},
        )

    def add_map_to_rotation(
        self,
        map_name: str,
        after_map_name: str | None = None,
    ):
        rotation = self.get_map_rotation()

        map_index = len(rotation)
        if after_map_name:
            try:
                map_index = rotation.index(after_map_name or "")
            except ValueError:
                pass

        self.add_map_to_rotation_at_index(map_name, map_index)

    def add_map_to_rotation_at_index(self, map_name: str, map_index: int):
        self.exchange("AddMapToRotation", 2, {"MapName": map_name, "Index": map_index})

    def remove_map_from_rotation(self, map_name: str):
        rotation = self.get_map_rotation()
        try:
            map_index = rotation.index(map_name)
        except ValueError:
            raise HLLCommandFailedError(f"Map {map_name} not in rotation")

        self.remove_map_from_rotation_at_index(map_index)

    def remove_map_from_rotation_at_index(self, map_index: int):
        self.exchange("RemoveMapFromRotation", 2, {"Index": map_index})

    def add_map_to_sequence_at_index(self, map_name: str, map_index: int):
        self.exchange("AddMapToSequence", 2, {"MapName": map_name, "Index": map_index})

    def remove_map_from_sequence_at_index(self, map_index: int):
        self.exchange("RemoveMapFromSequence", 2, {"Index": map_index})

    def move_map_in_sequence(self, current_index: int, new_index: int) -> None:
        self.exchange(
            "MoveMapInSequence",
            2,
            {"CurrentIndex": current_index, "NewIndex": new_index},
        )

    @_escape_params
    def punish(self, player_id: str, reason: str) -> bool:
        return self.exchange_success(
            "PunishPlayer", 2, {"PlayerId": player_id, "Reason": reason}
        )

    @_escape_params
    def kick(self, player_id: str, reason: str) -> bool:
        return self.exchange_success(
            "KickPlayer", 2, {"PlayerId": player_id, "Reason": reason}
        )

    @_escape_params
    def temp_ban(
        self,
        player_id: str,
        duration_hours: int = 2,
        reason: str = "",
        admin_name: str = "",
    ) -> bool:
        return self.exchange_success(
            "TemporaryBanPlayer",
            2,
            {
                "PlayerId": player_id,
                "Duration": duration_hours,
                "Reason": reason,
                "AdminName": admin_name,
            },
        )

    @_escape_params
    def perma_ban(
        self,
        player_id: str,
        reason: str = "",
        admin_name: str = "",
    ) -> bool:
        return self.exchange_success(
            "PermanentBanPlayer",
            2,
            {"PlayerId": player_id, "Reason": reason, "AdminName": admin_name},
        )

    def remove_temp_ban(self, player_id: str) -> bool:
        return self.exchange_success("RemoveTemporaryBan", 2, {"PlayerId": player_id})

    def remove_perma_ban(self, player_id: str) -> bool:
        return self.exchange_success("RemovePermanentBan", 2, {"PlayerId": player_id})

    @_escape_params
    def add_admin(self, player_id, role, description) -> bool:
        return self.exchange_success(
            "AddAdmin",
            2,
            {"PlayerId": player_id, "AdminGroup": role, "Comment": description},
        )

    def remove_admin(self, player_id) -> bool:
        return self.exchange_success("RemoveAdmin", 2, {"PlayerId": player_id})

    @_escape_params
    def add_vip(self, player_id: str, description: str) -> bool:
        return self.exchange_success(
            "AddVip", 2, {"PlayerId": player_id, "Description": description}
        )

    def remove_vip(self, player_id) -> bool:
        return self.exchange_success("RemoveVip", 2, {"PlayerId": player_id})

    @_escape_params
    def message_player(self, player_id: str, message: str) -> bool:
        return self.exchange_success(
            "MessagePlayer", 2, {"Message": message, "PlayerId": player_id}
        )

    @_escape_params
    def message_all_players(self, message: str) -> bool:
        return self.exchange_success("MessageAllPlayers", 2, {"Message": message})

    @_escape_params
    def bulk_message_players(self, player_ids: list[str], messages: list[str]) -> bool:
        if len(player_ids) != len(messages):
            raise HLLCommandFailedError(
                "Must have an equal amount of players and messages"
            )

        handles = [
            self.send("MessagePlayer", 2, {"Message": message, "PlayerId": player_id})
            for player_id, message in zip(player_ids, messages)
        ]
        responses = [self.receive_success(handle) for handle in handles]
        return any(responses)

    def get_gamestate(self) -> GameStateType:
        s = self.exchange(
            "GetServerInformation", 2, {"Name": "session", "Value": ""}
        ).content_dict
        map_sequence = self.get_map_sequence()

        time_remaining = timedelta(seconds=int(s["remainingMatchTime"]))
        seconds_remaining = int(time_remaining.total_seconds())
        raw_time_remaining = f"{seconds_remaining // 3600}:{(seconds_remaining // 60) % 60:02}:{seconds_remaining % 60:02}"

        game_mode = GameMode(s["gameMode"].lower())

        try:
            current_map = LAYERS[s["mapId"].lower()]
        except Exception:
            current_map = LAYERS[UNKNOWN_MAP_NAME]

        try:
            next_map_index = map_sequence["current_index"] + 1
            if next_map_index >= len(map_sequence["maps"]):
                next_map_index = 0
            next_map = map_sequence["maps"][next_map_index]
        except Exception:
            next_map = LAYERS[UNKNOWN_MAP_NAME]

        return GameStateType(
            next_map=next_map.model_dump(),
            axis_score=s["axisScore"],
            axis_faction=s["axisFaction"],
            num_axis_players=s["axisPlayerCount"],
            allied_score=s["alliedScore"],
            allied_faction=s["alliedFaction"],
            num_allied_players=s["alliedPlayerCount"],
            current_map=current_map.model_dump(),
            raw_time_remaining=raw_time_remaining,
            time_remaining=time_remaining,
            game_mode=game_mode,
            match_time=s["matchTime"],
            queue_count=s["queueCount"],
            max_queue_count=s["maxQueueCount"],
            vip_queue_count=s["vipQueueCount"],
            max_vip_queue_count=s["maxVipQueueCount"],
            server_name=s["serverName"],
        )

    def get_objective_row(self, row: int):
        if not (0 <= row <= 4):
            raise ValueError("Row must be between 0 and 4")

        return self.get_objective_rows()[row]

    def get_objective_rows(self) -> List[List[str]]:
        details = self.exchange("GetClientReferenceData", 2, "SetSectorLayout")
        parameters = details.content_dict["dialogueParameters"]
        if not parameters or not all(
            p["iD"].startswith("Sector_") for p in parameters[:5]
        ):
            msg = "Received unexpected response from server."
            raise HLLCommandFailedError(msg)

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
        print(
            self.exchange(
                "SetSectorLayout",
                2,
                {
                    "Sector_1": objectives[0],
                    "Sector_2": objectives[1],
                    "Sector_3": objectives[2],
                    "Sector_4": objectives[3],
                    "Sector_5": objectives[4],
                },
            ).content
        )
        return list(objectives)

    def get_game_mode(self) -> Literal["Warfare", "Offensive", "Skirmish"]:
        return self.exchange(
            "GetServerInformation", 2, {"Name": "session", "Value": ""}
        ).content_dict["gameMode"]

    def set_match_timer(self, game_mode: GameMode, length: int):
        self.exchange(
            "SetMatchTimer", 2, {"GameMode": game_mode.value, "MatchLength": length}
        )

    def remove_match_timer(self, game_mode: GameMode):
        self.exchange("RemoveMatchTimer", 2, {"GameMode": game_mode.value})

    def set_warmup_timer(self, game_mode: GameMode, length: int):
        self.exchange(
            "SetWarmupTimer", 2, {"GameMode": game_mode.value, "WarmupLength": length}
        )

    def remove_warmup_timer(self, game_mode: GameMode):
        self.exchange("RemoveWarmupTimer", 2, {"GameMode": game_mode.value})

    def set_dynamic_weather_enabled(self, map_name: str, enabled: bool):
        self.exchange(
            "SetDynamicWeatherEnabled", 2, {"MapId": map_name, "Enable": enabled}
        )


if __name__ == "__main__":
    from rcon.settings import SERVER_INFO

    ctl = ServerCtl(SERVER_INFO)

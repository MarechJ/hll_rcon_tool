import json
import logging
import os
import random
import re
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from functools import cached_property
from itertools import chain
from time import sleep
from typing import Any, Iterable, List, Literal, Optional, Sequence, overload

from dateutil import parser

import rcon.steam_utils
from rcon.cache_utils import get_redis_client, invalidates, ttl_cache
from rcon.commands import SUCCESS, CommandFailedError, ServerCtl, VipId
from rcon.maps import UNKNOWN_MAP_NAME, Layer, is_server_loading_map, parse_layer
from rcon.models import PlayerID, PlayerVIP, enter_session, GameLayout
from rcon.player_history import get_profiles, safe_save_player_action, save_player, get_player_profile
from rcon.settings import SERVER_INFO
from rcon.types import (
    AdminType,
    GameLayoutRandomConstraints,
    GameServerBanType,
    GameStateType,
    GetDetailedPlayer,
    GetDetailedPlayers,
    GetPlayersType,
    ParsedLogsType,
    PlayerActionState,
    ServerInfoType,
    SlotsType,
    StatusType,
    StructuredLogLineType,
    StructuredLogLineWithMetaData,
    VipIdType,
)
from rcon.user_config.rcon_connection_settings import RconConnectionSettingsUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.utils import BaseUserConfig
from rcon.utils import (
    ALL_ROLES,
    ALL_ROLES_KEY_INDEX_MAP,
    INDEFINITE_VIP_DATE,
    default_player_info_dict,
    get_server_number,
    parse_raw_player_info,
)

PLAYER_ID = "player_id"
NAME = "name"
ROLE = "role"

TEMP_BAN = "temp"
PERMA_BAN = "perma"

USER_CONFIG_NAME_PATTERN = re.compile(r"set_.*_config")

# The base level of actions that will always show up in the Live view
# actions filter from the call to `get_recent_logs`
LOG_ACTIONS = [
    "DISCONNECTED",
    "CHAT[Allies]",
    "CHAT[Axis]",
    "CHAT[Allies][Unit]",
    "KILL",
    "CONNECTED",
    "CHAT[Allies][Team]",
    "CHAT[Axis][Team]",
    "CHAT[Axis][Unit]",
    "CHAT",
    "VOTE COMPLETED",
    "VOTE STARTED",
    "VOTE",
    "TEAMSWITCH",
    "TK AUTO",
    "TK AUTO KICKED",
    "TK AUTO BANNED",
    "ADMIN",
    "ADMIN KICKED",
    "ADMIN BANNED",
    "MATCH",
    "MATCH START",
    "MATCH ENDED",
    "MESSAGE",
]
logger = logging.getLogger(__name__)


CTL: Optional["Rcon"] = None


def get_rcon(credentials: ServerInfoType | None = None):
    """Return a initialized Rcon connection to the game server

    This maintains a single initialized instance across a Python interpreter
    instance unless someone explicitly chooses to use multiple instances.
    This also doesn't automatically attempt to connect to the game server on
    module import.

    Args:
        credentials: A dict of the game server IP, RCON port and RCON password
    """
    global CTL

    if credentials is None:
        credentials = SERVER_INFO

    if CTL is None:
        CTL = Rcon(credentials)
    return CTL


def do_run_commands(rcon, commands):
    for command, params in commands.items():
        try:
            logger.info("Applying %s %s", command, params)

            # Allow people to apply partial changes to a user config to make
            # auto settings less gigantic
            if is_user_config_func(command):
                # super dirty we should probably make an actual look up table
                # but all the names are consistent
                get_config_command = f"g{command[1:]}"
                config: BaseUserConfig = rcon.__getattribute__(get_config_command)()
                # get the existing config, override anything set in params
                merged_params = config.model_dump() | params

                if "by" not in merged_params:
                    merged_params["by"] = "AutoSettings"

                rcon.__getattribute__(command)(**merged_params)
            else:
                # Non user config settings
                rcon.__getattribute__(command)(**params)
        except AttributeError as e:
            logger.exception(
                "%s is not a valid command, double check the name!", command
            )
        except Exception as e:
            logger.exception("Unable to apply %s %s: %s", command, params, e)
        time.sleep(5)  # go easy on the server


def is_user_config_func(name: str) -> bool:
    return re.match(USER_CONFIG_NAME_PATTERN, name) is not None


class Rcon(ServerCtl):
    settings = (
        ("team_switch_cooldown", int),
        ("autobalance_threshold", int),
        ("idle_autokick_time", int),
        ("max_ping_autokick", int),
        ("queue_length", int),
        ("vip_slots_num", int),
        ("autobalance_enabled", bool),
        ("votekick_enabled", bool),
        ("votekick_thresholds", str),
    )
    MAX_SERV_NAME_LEN = 1024  # I totally made up that number. Unable to test
    slots_regexp = re.compile(r"^\d{1,3}/\d{2,3}$")
    map_regexp = re.compile(r"^(\w+_?)+$")
    chat_regexp = re.compile(r"CHAT\[(Team|Unit)\]\[(.*)\((Allies|Axis)/(.*)\)\]: (.*)")
    player_info_pattern = r"(.*)\(((Allies)|(Axis))/(\d+)\)"
    player_info_regexp = re.compile(r"(.*)\(((Allies)|(Axis))/(\d+)\)")
    log_time_regexp = re.compile(r".*\((\d+)\).*")
    connect_disconnect_pattern = re.compile(r"(.+) \((.*)\)")
    kill_teamkill_pattern = re.compile(
        r"(.*)\((?:Allies|Axis)\/(.*)\) -> (.*)\((?:Allies|Axis)\/(.*)\) with (.*)"
    )
    camera_pattern = re.compile(r"\[(.*) \((.*)\)\] (.*)")
    teamswitch_pattern = re.compile(r"TEAMSWITCH\s(.*)\s\((.*\s>\s.*)\)")
    kick_ban_pattern = re.compile(
        r"(KICK|BAN): \[(.*)\] (.*\[(KICKED|BANNED|PERMANENTLY|YOU|Host|Anti-Cheat|[^\]]*)[^\]]*)(?:\])*"
    )
    vote_pattern = re.compile(
        r"VOTESYS: Player \[(.*)\] voted \[.*\] for VoteID\[\d+\]"
    )
    vote_started_pattern = re.compile(
        r"VOTESYS: Player \[(.*)\] Started a vote of type \(.*\) against \[(.*)\]. VoteID: \[\d+\]"
    )
    vote_complete_pattern = re.compile(r"VOTESYS: Vote \[\d+\] completed. Result: (.*)")
    vote_expired_pattern = re.compile(r"VOTESYS: Vote \[\d+\] (expired|prematurely)")
    vote_passed_pattern = re.compile(r"VOTESYS: (Vote Kick \{(.*)\} .*\[(.*)\])")
    # Need the DOTALL flag to allow `.` to capture newlines in multi line messages
    message_pattern = re.compile(
        r"MESSAGE: player \[(.+)\((.*)\)\], content \[(.+)\]", re.DOTALL
    )

    def __init__(self, *args, pool_size: bool | None = None, **kwargs):
        config = RconConnectionSettingsUserConfig.load_from_db()
        super().__init__(
            *args, **kwargs, max_open=config.max_open, max_idle=config.max_idle
        )
        if pool_size is not None:
            self.pool_size = pool_size
        else:
            self.pool_size = config.thread_pool_size

        self._current_map = parse_layer(UNKNOWN_MAP_NAME)
        self._next_map = parse_layer(UNKNOWN_MAP_NAME)

    @property
    def current_map(self) -> Layer:
        """Store the last valid map we've seen, game server reports Untitled_ maps when loading"""
        return self._current_map

    @current_map.setter
    def current_map(self, map_name: str):
        if not is_server_loading_map(map_name):
            self._current_map = parse_layer(map_name)

    @property
    def next_map(self) -> Layer:
        """Store the next map as reported by the `gamestate` command"""
        return self._next_map

    @next_map.setter
    def next_map(self, map_name: str):
        self._next_map = parse_layer(map_name)

    @cached_property
    def thread_pool(self):
        return ThreadPoolExecutor(self.pool_size)

    def run_in_pool(self, function_name: str, *args, **kwargs):
        return self.thread_pool.submit(getattr(self, function_name), *args, **kwargs)

    @ttl_cache(ttl=5)
    def get_players(self) -> list[GetPlayersType]:
        player_ids = {
            player_id: {NAME: name, PLAYER_ID: player_id}
            for name, player_id in self.get_playerids()
        }
        # can't pickle dict keys object
        steam_profiles = rcon.steam_utils.get_steam_profiles_mult_players(
            steam_id_64s=[k for k in player_ids.keys()]
        )

        vip_player_ids = set(v[PLAYER_ID] for v in super().get_vip_ids())
        profiles = {
            p[PLAYER_ID]: p
            for p in get_profiles([player_id for player_id in player_ids.keys()])
        }

        players: dict[str, GetPlayersType] = {}
        for player_id in player_ids.keys():
            profile = steam_profiles.get(player_id)
            players[player_id] = {
                NAME: player_ids[player_id]["name"],
                PLAYER_ID: player_id,
                "country": profile.get("country") if profile else None,
                "steam_bans": profile.get("bans") if profile else None,
                "profile": profiles.get(player_id),
                "is_vip": player_id in vip_player_ids,
            }

        return [p for p in players.values()]

    def get_detailed_players(self) -> GetDetailedPlayers:
        players = self.get_players()
        fail_count = 0
        players_by_id: dict[str, GetDetailedPlayer] = {}

        futures: dict[Future[Any], GetDetailedPlayer] = {}
        for player in players:
            res =  self.run_in_pool("get_detailed_player_info", player[NAME], player)
            futures[res] = player

        for future in as_completed(futures):
            try:
                player_data: GetDetailedPlayer = future.result()
            except Exception:
                logger.error("Failed to get info for %s", futures[future][PLAYER_ID])
                fail_count += 1
                player_data = default_player_info_dict(futures[future][NAME])
            player = futures[future]
            player.update(player_data)
            players_by_id[player[PLAYER_ID]] = player

        return {
            "players": players_by_id,
            "fail_count": fail_count,
        }

    @ttl_cache(ttl=2, cache_falsy=False)
    def get_team_view(self):
        teams = {}
        detailed_players = self.get_detailed_players()
        players_by_id = detailed_players["players"]
        fail_count = detailed_players["fail_count"]

        for player in players_by_id.values():
            player_id = player[PLAYER_ID]

            teams.setdefault(player.get("team"), {}).setdefault(
                player.get("unit_name"), {}
            ).setdefault("players", []).append(player)

        for team, squads in teams.items():
            if team is None:
                continue
            for squad_name, squad in squads.items():
                squad["players"] = sorted(
                    squad["players"],
                    key=lambda player: (
                        ALL_ROLES_KEY_INDEX_MAP.get(player.get("role"), len(ALL_ROLES)),
                        player.get(PLAYER_ID),
                    ),
                )
                squad["type"] = self._guess_squad_type(squad)
                squad["has_leader"] = self._has_leader(squad)

                try:
                    squad["combat"] = sum(p["combat"] for p in squad["players"])
                    squad["offense"] = sum(p["offense"] for p in squad["players"])
                    squad["defense"] = sum(p["defense"] for p in squad["players"])
                    squad["support"] = sum(p["support"] for p in squad["players"])
                    squad["kills"] = sum(p["kills"] for p in squad["players"])
                    squad["deaths"] = sum(p["deaths"] for p in squad["players"])
                except Exception as e:
                    logger.exception(e)

        game = {}
        for team, squads in teams.items():
            if team is None:
                continue
            commander = [
                squad for _, squad in squads.items() if squad["type"] == "commander"
            ]
            if not commander:
                commander = None
            else:
                commander = (
                    commander[0]["players"][0] if commander[0].get("players") else None
                )

            game[team] = {
                "squads": {
                    squad_name: squad
                    for squad_name, squad in squads.items()
                    if squad["type"] != "commander"
                },
                "commander": commander,
                "combat": sum(s["combat"] for s in squads.values()),
                "offense": sum(s["offense"] for s in squads.values()),
                "defense": sum(s["defense"] for s in squads.values()),
                "support": sum(s["support"] for s in squads.values()),
                "kills": sum(s["kills"] for s in squads.values()),
                "deaths": sum(s["deaths"] for s in squads.values()),
                "count": sum(len(s["players"]) for s in squads.values()),
            }

        return dict(fail_count=fail_count, **game)

    @ttl_cache(ttl=1)
    def get_structured_logs(
        self,
        since_min_ago: int,
        filter_action: str | None = None,
        filter_player: str | None = None,
    ) -> ParsedLogsType:
        raw = super().get_logs(since_min_ago)
        return self.parse_logs(raw, filter_action, filter_player)

    def get_admin_groups(self) -> list[str]:
        # Defined here to avoid circular imports with commands.py
        return super().get_admin_groups()

    def get_logs(
        self, since_min_ago: str | int, filter_: str = "", by: str = ""
    ) -> str:
        """Returns raw text logs from the game server with no parsing performed

        You most likely want to use a different method/endpoint to get parsed logs.
        """

        # by is included as it's passed in as part of the API exposure
        # Defined here to avoid circular imports with commands.py
        return super().get_logs(since_min_ago=since_min_ago, filter_=filter_)

    @overload
    def get_playerids(
        self, as_dict: Literal[False] = False
    ) -> list[tuple[str, str]]: ...
    @overload
    def get_playerids(self, as_dict: Literal[True] = False) -> dict[str, str]: ...

    def get_playerids(self, as_dict=False) -> dict[str, str] | list[tuple[str, str]]:
        raw_list = super().get_playerids()

        player_list: list[tuple[str, str]] = []
        player_dict: dict[str, str] = {}
        for playerinfo in raw_list:
            # playerinfo='some_dude : 76561199400000000
            name, player_id = playerinfo.rsplit(":", 1)
            name = name[:-1]
            player_id = player_id[1:]
            player_dict[name] = player_id
            player_list.append((name, player_id))

        return player_dict if as_dict else player_list

    def get_vips_count(self) -> int:
        players = self.get_playerids()

        vips = {v[PLAYER_ID] for v in self.get_vip_ids()}
        vip_count = 0
        for _, player_id in players:
            if player_id in vips:
                vip_count += 1

        return vip_count

    def _guess_squad_type(
        self, squad
    ) -> Literal["armor", "recon", "commander", "infantry"]:
        for player in squad.get("players", []):
            if player.get("role") in ["tankcommander", "crewman"]:
                return "armor"
            if player.get("role") in ["spotter", "sniper"]:
                return "recon"
            if player.get("role") in ["armycommander"]:
                return "commander"

        return "infantry"

    def _has_leader(self, squad) -> bool:
        for players in squad.get("players", []):
            if players.get("role") in ["tankcommander", "officer", "spotter"]:
                return True
        return False

    @ttl_cache(ttl=60 * 60 * 24, cache_falsy=False)
    def get_player_info(self, player_name: str, can_fail=False):
        try:
            try:
                raw = super().get_player_info(player_name, can_fail=can_fail)
                name, player_id, *rest = raw.split("\n")
            except (CommandFailedError, Exception):
                sleep(2)
                name = player_name
                player_id_lookup = self.get_playerids(as_dict=True)
                player_id = player_id_lookup.get(name)
            if not player_id:
                return {}

            profile = rcon.steam_utils.get_steam_profile(steam_id_64=player_id)

        except (CommandFailedError, ValueError):
            # Making that debug instead of exception as it's way to spammy
            logger.exception("Can't get player info for %s", player_name)
            # logger.exception("Can't get player info for %s", player)
            return {}
        name = name.split(": ", 1)[-1]
        player_id = player_id.split(": ", 1)[-1]
        if name != player_name:
            logger.error(
                "get_player_info('%s') returned for a different name: %s %s",
                player_name,
                name,
                player_id,
            )
            return {}
        return {
            NAME: name,
            PLAYER_ID: player_id,
            "country": profile.get("country") if profile else None,
            "steam_bans": profile.get("bans") if profile else None,
        }

    @ttl_cache(ttl=2, cache_falsy=False)
    def get_detailed_player_info(self, player_name: str, player: GetPlayersType | None = None) -> GetDetailedPlayer:
        raw = super().get_player_info(player_name)
        if not raw:
            raise CommandFailedError("Got bad data")

        """
        Name: T17 Scott
        steamID64: 01234567890123456
        Team: Allies            # "None" when not in team
        Role: Officer
        Unit: 0 - Able          # Absent when not in unit
        Loadout: NCO            # Absent when not in team
        Kills: 0 - Deaths: 0
        Score: C 50, O 0, D 40, S 10
        Level: 34
        """

        player_data = parse_raw_player_info(raw, player_name)
        if player is not None and 'is_vip' in player:
            player_data["is_vip"] = player.get('is_vip')
        else:
            vip_player_ids = set(v[PLAYER_ID] for v in super().get_vip_ids())
            player_data["is_vip"] = player_data["player_id"] in vip_player_ids

        if player is not None and 'profile' in player:
            player_data["profile"] = player.get('profile')
        else:
            profile = get_player_profile(player_data["player_id"], 1)
            player_data["profile"] = profile

        return player_data

    @ttl_cache(ttl=60 * 10)
    def get_admin_ids(self) -> list[AdminType]:
        res = super().get_admin_ids()
        admins: list[AdminType] = []
        for item in res:
            player_id, role, name = item.split(" ", 2)
            admins.append({PLAYER_ID: player_id, NAME: name[1:-1], ROLE: role})
        return admins

    def add_admin(self, player_id, role, description) -> bool:
        with invalidates(Rcon.get_admin_ids):
            return super().add_admin(player_id, role, description)

    def remove_admin(self, player_id) -> bool:
        with invalidates(Rcon.get_admin_ids):
            return super().remove_admin(player_id)

    @ttl_cache(ttl=60)
    def get_perma_bans(self) -> list[GameServerBanType]:
        bans: list[GameServerBanType] = []
        for raw_ban in super().get_perma_bans():
            try:
                ban = self._struct_ban(ban=raw_ban, type_=PERMA_BAN)
                bans.append(ban)
            except ValueError:
                logger.exception("Invalid perma ban line: %s", raw_ban)

        return bans

    @ttl_cache(ttl=60)
    def get_temp_bans(self) -> list[GameServerBanType]:
        bans: list[GameServerBanType] = []
        for raw_ban in super().get_temp_bans():
            try:
                ban = self._struct_ban(ban=raw_ban, type_=TEMP_BAN)
                bans.append(ban)
            except ValueError:
                logger.exception("Invalid temp ban line: %s", raw_ban)

        return bans

    def _struct_ban(self, ban, type_) -> GameServerBanType:
        # Avoid errors on empty temp bans
        if ban == "":
            return {
                "type": type_,
                "name": None,
                PLAYER_ID: None,
                "timestamp": None,
                "ban_time": None,
                "reason": None,
                "by": None,
                "raw": ban,
            }

        # name, time = ban.split(', banned on ')
        # '76561197984877751 : nickname "Dr.WeeD" banned for 2 hours on 2020.12.03-12.40.08 for "None" by admin "test"'
        player_id, rest = ban.split(" :", 1)
        name = None
        reason = None
        by = None
        date = None

        if "nickname" in rest:
            name = rest.split('" banned', 1)[0]
            name = name.split(' nickname "', 1)[-1]

        groups = re.match(r".*(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}.\d{2}) (.*)", ban)
        if groups and groups.groups():
            date = groups.group(1)
            try:
                reason = groups.group(2)
            except:
                logger.error("Unable to extract reason from ban")
        by = ban.split(" by admin ", -1)[-1]

        return {
            "type": type_,
            "name": name,
            PLAYER_ID: player_id,
            # TODO FIX
            "timestamp": None,
            "ban_time": date,
            "reason": reason,
            "by": by.replace('"', ""),
            "raw": ban,
        }

    def get_bans(self) -> list[GameServerBanType]:
        try:
            return self.get_temp_bans() + self.get_perma_bans()
        except Exception:
            self.get_temp_bans.cache_clear()
            self.get_perma_bans.cache_clear()
            raise

    def get_ban(self, player_id: str) -> list[GameServerBanType]:
        """
        get all bans from player_id
        @param player_id: steam_id_64 or windows store ID of a user
        @return: a array of bans
        """
        bans = self.get_bans()
        return list(filter(lambda x: x.get(PLAYER_ID) == player_id, bans))

    @ttl_cache(ttl=60 * 5)
    def get_vip_ids(self) -> list[VipIdType]:
        res: list[VipId] = super().get_vip_ids()
        player_dicts = []

        vip_expirations: dict[str, datetime]
        with enter_session() as session:
            server_number = get_server_number()

            players: list[PlayerVIP] = (
                session.query(PlayerVIP)
                .filter(PlayerVIP.server_number == server_number)
                .all()
            )
            vip_expirations = {
                player.player.player_id: player.expiration for player in players
            }

        for item in res:
            player: VipIdType = {
                PLAYER_ID: item[PLAYER_ID],
                NAME: item["name"],
                "vip_expiration": None,
            }
            player["vip_expiration"] = vip_expirations.get(item[PLAYER_ID], None)
            player_dicts.append(player)

        return sorted(player_dicts, key=lambda d: d[NAME])

    def remove_vip(self, player_id) -> bool:
        """Removes VIP status on the game server and removes their PlayerVIP record."""

        # Remove VIP before anything else in case we have errors
        with invalidates(Rcon.get_vip_ids):
            result = super().remove_vip(player_id)

        server_number = get_server_number()
        with enter_session() as session:
            player: PlayerID | None = (
                session.query(PlayerID)
                .filter(PlayerID.player_id == player_id)
                .one_or_none()
            )
            if player and player.vip:
                logger.info(
                    f"Removed VIP from {player_id} expired: {player.vip.expiration}"
                )
                # TODO: This is an incredibly dumb fix because I can't get
                # the changes to persist otherwise
                vip_record: PlayerVIP | None = (
                    session.query(PlayerVIP)
                    .filter(
                        PlayerVIP.player_id_id == player.id,
                        PlayerVIP.server_number == server_number,
                    )
                    .one_or_none()
                )
                session.delete(vip_record)
            elif player and not player.vip:
                logger.warning(f"{player_id} has no PlayerVIP record")
            else:
                # This is okay since you can give VIP to someone who has never been on a game server
                # or that your instance of CRCON hasn't seen before, but you might want to prune these
                logger.warning(f"{player_id} has no PlayerSteamID record")

        return result

    def add_vip(
        self, player_id: str, description: str, expiration: str | None = None
    ) -> str:
        """Adds VIP status on the game server and adds or updates their PlayerVIP record."""
        with invalidates(Rcon.get_vip_ids):
            # Add VIP before anything else in case we have errors
            result = super().add_vip(player_id, description)

        expiration = expiration or ""
        # postgres and Python have different max date limits
        # https://docs.python.org/3.8/library/datetime.html#datetime.MAXYEAR
        # https://www.postgresql.org/docs/12/datatype-datetime.html

        server_number = get_server_number()
        # If we're unable to parse the date, treat them as indefinite VIPs
        expiration_date: str | datetime
        try:
            expiration_date = parser.parse(expiration)
        except (parser.ParserError, OverflowError):
            logger.warning(
                f"Unable to parse {expiration=} for {description=} {player_id=}"
            )
            # For our purposes (human lifespans) we can use 200 years in the future as
            # the equivalent of indefinite VIP access
            expiration_date = INDEFINITE_VIP_DATE

        # Find a player and update their expiration date if it exists or create a new record if not
        with enter_session() as session:
            player: PlayerID | None = (
                session.query(PlayerID)
                .filter(PlayerID.player_id == player_id)
                .one_or_none()
            )
            if player is None:
                # If a player has never been on the server before and their record is
                # being created from a VIP list upload, their alias will be saved with
                # whatever name is in the upload file which may have metadata in it since
                # people use the free form name field in VIP uploads to store stuff
                save_player(player_name=description, player_id=player_id)
                # Can't use a return value from save_player or it's not bound
                # to the session https://docs.sqlalchemy.org/en/20/errors.html#error-bhk3
                player = (
                    session.query(PlayerID)
                    .filter(PlayerID.player_id == player_id)
                    .one()
                )

            vip_record: PlayerVIP | None = (
                session.query(PlayerVIP)
                .filter(
                    PlayerVIP.server_number == server_number,
                    PlayerVIP.player_id_id == player.id,
                )
                .one_or_none()
            )

            if vip_record is None:
                vip_record = PlayerVIP(
                    expiration=expiration_date,
                    player_id_id=player.id,
                    server_number=server_number,
                )
                logger.info(
                    f"Added new PlayerVIP record {player.player_id=} {expiration_date=}"
                )
                session.add(vip_record)
            else:
                previous_expiration = vip_record.expiration.isoformat()
                vip_record.expiration = expiration_date
                logger.info(
                    f"Modified PlayerVIP record {player.player_id=} {vip_record.expiration} {previous_expiration=}"
                )

        return result

    def remove_all_vips(self) -> bool:
        vips = self.get_vip_ids()
        for vip in vips:
            try:
                self.remove_vip(vip[PLAYER_ID])
            except (CommandFailedError, ValueError):
                raise

        return True

    def message_player(
        self,
        player_name=None,
        player_id=None,
        message: str = "",
        by: str = "",
        save_message: bool = False,
    ) -> str:
        config = RconServerSettingsUserConfig.load_from_db()
        if config.message_enhancements.enabled:
            message_header: str = config.message_enhancements.message_header
            if message_header:
                message = f"{message_header}\n\n{message}"
            message_footer: str = config.message_enhancements.message_footer
            # append to message if not empty. separate with blank line.
            if message_footer:
                message = f"{message}\n\n{message_footer}"

        res = super().message_player(player_name, player_id, message)
        if save_message:
            safe_save_player_action(
                rcon=self,
                player_name=player_name,
                action_type=PlayerActionState.MESSAGE,
                reason=message,
                by=by,
                player_id=player_id,
            )
        return res

    def get_gamestate(self) -> GameStateType:
        """
        Returns player counts, team scores, remaining match time and current/next map

        Players: Allied: 0 - Axis: 1
        Score: Allied: 2 - Axis: 2
        Remaining Time: 0:11:51
        Map: foy_warfare
        Next Map: stmariedumont_warfare"""
        with invalidates(
            Rcon.team_sizes,
            Rcon.get_team_objective_scores,
            Rcon.get_round_time_remaining,
        ):
            (
                raw_team_size,
                raw_score,
                raw_time_remaining,
                raw_current_map,
                raw_next_map,
            ) = super().get_gamestate()

        num_allied_players: int = None  # type: ignore
        num_axis_players: int = None  # type: ignore
        allied_score: int = None  # type: ignore
        axis_score: int = None  # type: ignore
        hours: int = None  # type: ignore
        mins: int = None  # type: ignore
        secs: int = None  # type: ignore

        if match := re.match(r"Players: Allied: (\d+) - Axis: (\d+)", raw_team_size):
            num_allied_players, num_axis_players = match.groups()  # type: ignore

        if match := re.match(r"Score: Allied: (\d+) - Axis: (\d+)", raw_score):
            allied_score, axis_score = match.groups()  # type: ignore

        if match := re.match(
            r"Remaining Time: (\d):(\d{2}):(\d{2})", raw_time_remaining
        ):
            hours, mins, secs = match.groups()  # type: ignore

        if not all(
            [
                num_allied_players,
                num_axis_players,
                allied_score,
                axis_score,
                hours,
                mins,
                secs,
            ]
        ):
            raise ValueError("Game server returned junk for get_gamestate")

        raw_time_remaining = raw_time_remaining.split("Remaining Time: ")[1]
        # Handle Untitled_ style map names when maps are loading
        self.current_map = raw_current_map.split(": ")[1]
        self.next_map = raw_next_map.split(": ")[1]

        time_remaining = timedelta(
            hours=float(hours), minutes=float(mins), seconds=float(secs)
        )

        return {
            "num_allied_players": int(num_allied_players),
            "num_axis_players": int(num_axis_players),
            "allied_score": int(allied_score),
            "axis_score": int(axis_score),
            "raw_time_remaining": raw_time_remaining,
            "time_remaining": time_remaining,
            "current_map": self.current_map.model_dump(),
            "next_map": self.next_map.model_dump(),
        }

    @ttl_cache(ttl=2, cache_falsy=False)
    def team_sizes(self) -> tuple[int, int]:
        """Returns the number of allied/axis players respectively"""
        result = self.get_gamestate()

        return result["num_allied_players"], result["num_axis_players"]

    @ttl_cache(ttl=2, cache_falsy=False)
    def get_team_objective_scores(self) -> tuple[int, int]:
        """Returns the number of objectives held by the allied/axis team respectively"""
        result = self.get_gamestate()

        return result["allied_score"], result["axis_score"]

    @ttl_cache(ttl=2, cache_falsy=False)
    def get_round_time_remaining(self) -> float:
        """Returns the amount of time left in the round as seconds"""
        result = self.get_gamestate()
        return result["time_remaining"].total_seconds()

    @ttl_cache(ttl=60)
    def get_next_map(self) -> Layer:
        """Return the next map in the rotation as determined by the gameserver through the gamestate command"""
        # On initialization this is set to UNKNOWN_MAP_NAME and isn't updated until the first time
        # get_gamestate is called, so refresh it to make sure it is always correct
        # especially because the next map can change due to map rotation changes
        self.get_gamestate()

        return self.next_map

    def set_map(self, map_name: str) -> None:
        with invalidates(Rcon.get_map, Rcon.get_next_map):
            try:
                res = super().set_map(map_name)
                if res != SUCCESS:
                    raise CommandFailedError(res)
            except CommandFailedError:
                maps = [map_.id for map_ in self.get_map_rotation()]
                self.add_map_to_rotation(
                    map_name, maps[len(maps) - 1], maps.count(maps[len(maps) - 1])
                )
                if res := super().set_map(map_name) != SUCCESS:
                    raise CommandFailedError(res)

    @ttl_cache(ttl=10)
    def get_map(self) -> Layer:
        current_map = super().get_map()
        if not self.map_regexp.match(current_map):
            raise CommandFailedError("Server returned wrong data")

        self.current_map = current_map

        return self.current_map

    @ttl_cache(ttl=60 * 5)
    def get_current_map_sequence(self) -> list[str]:
        return super().get_current_map_sequence()

    @ttl_cache(ttl=60 * 10)
    def get_map_shuffle_enabled(self) -> bool:
        return super().get_map_shuffle_enabled()

    def set_map_shuffle_enabled(self, enabled: bool) -> None:
        with invalidates(
            Rcon.get_current_map_sequence,
            Rcon.get_map_shuffle_enabled,
            Rcon.get_next_map,
        ):
            return super().set_map_shuffle_enabled(enabled)

    @ttl_cache(ttl=60 * 30)
    def get_name(self) -> str:
        name = super().get_name()
        if len(name) > self.MAX_SERV_NAME_LEN:
            raise CommandFailedError("Server returned wrong data")
        return name

    @ttl_cache(ttl=60 * 10)
    def get_team_switch_cooldown(self) -> int:
        return int(super().get_team_switch_cooldown())

    def set_team_switch_cooldown(self, minutes: int) -> bool:
        with invalidates(Rcon.get_team_switch_cooldown):
            return super().set_team_switch_cooldown(minutes)

    @ttl_cache(ttl=60 * 10)
    def get_autobalance_threshold(self) -> int:
        return int(super().get_autobalance_threshold())

    def set_autobalance_threshold(self, max_diff: int) -> bool:
        with invalidates(Rcon.get_autobalance_threshold):
            return super().set_autobalance_threshold(max_diff)

    @ttl_cache(ttl=60 * 10)
    def get_idle_autokick_time(self) -> int:
        return int(super().get_idle_autokick_time())

    def set_idle_autokick_time(self, minutes) -> bool:
        with invalidates(Rcon.get_idle_autokick_time):
            return super().set_idle_autokick_time(minutes)

    @ttl_cache(ttl=60 * 10)
    def get_max_ping_autokick(self) -> int:
        return int(super().get_max_ping_autokick())

    def set_max_ping_autokick(self, max_ms) -> bool:
        with invalidates(Rcon.get_max_ping_autokick):
            return super().set_max_ping_autokick(max_ms)

    @ttl_cache(ttl=60 * 10)
    def get_queue_length(self) -> int:
        return int(super().get_queue_length())

    def set_queue_length(self, value: int) -> bool:
        with invalidates(Rcon.get_queue_length):
            return super().set_queue_length(value)

    @ttl_cache(ttl=60 * 10)
    def get_vip_slots_num(self) -> int:
        return int(super().get_vip_slots_num())

    def set_vip_slots_num(self, value: int) -> bool:
        with invalidates(Rcon.get_vip_slots_num):
            return super().set_vip_slots_num(value)

    def get_welcome_message(self):
        red = get_redis_client()
        msg: bytes = red.get("WELCOME_MESSAGE")  # type: ignore
        if msg:
            return msg.decode()

        # JSON can't serialize bytes and the welcome messgae
        # can be set to an empty string
        if msg == b"":
            msg = None

        return msg

    def set_welcome_message(self, message: str) -> str:
        """Set the in game welcome (rules) message and return the previous message if set"""
        from rcon.broadcast import format_message

        try:
            formatted = format_message(self, message)
        except Exception:
            logger.exception("Unable to format message")
            formatted = message

        prev: bytes | None = None
        try:
            red = get_redis_client()
            prev = red.set("WELCOME_MESSAGE", message, get=True)  # type: ignore
        except Exception:
            logger.exception("Can't save message in redis: %s", message)

        super().set_welcome_message(formatted)
        return prev.decode() if prev else ""

    def get_broadcast_message(self) -> str | bytes | None:
        """Returns the current broadcast message if the cache is set

        There is no RCON command to get the current broadcast message so it can only
        be retrieved if it was set by CRCON and the cache has not expired
        """
        red = get_redis_client()
        msg: bytes = red.get("BROADCAST_MESSAGE")  # type: ignore
        if isinstance(msg, (str, bytes)):
            return msg.decode()
        return msg

    def set_broadcast(self, message: str) -> str:
        """Set the in game broadcast message and return the previous message if set"""
        from rcon.broadcast import format_message

        try:
            formatted = format_message(self, message)
        except Exception:
            logger.exception("Unable to format message")
            formatted = message

        prev: bytes | None = None
        try:
            red = get_redis_client()
            prev = red.set("BROADCAST_MESSAGE", message, get=True)  # type: ignore
            red.expire("BROADCAST_MESSAGE", 60 * 30)
        except Exception:
            logger.exception("Can't save message in redis: %s", message)

        super().set_broadcast(formatted)
        return prev.decode() if prev else ""

    @ttl_cache(ttl=5)
    def get_slots(self) -> SlotsType:
        """Return the current number of connected players and max players allowed"""
        res = super().get_slots()
        if not self.slots_regexp.match(res):
            raise CommandFailedError("Server returned crap")

        current_players, max_players = tuple(map(int, res.split("/", maxsplit=1)))
        return {"current_players": current_players, "max_players": max_players}

    @ttl_cache(ttl=5, cache_falsy=False)
    def get_status(self) -> StatusType:
        config = RconServerSettingsUserConfig.load_from_db()
        slots = self.get_slots()
        current_players = slots["current_players"]
        max_players = slots["max_players"]
        return {
            "name": self.get_name(),
            "map": self.get_gamestate()["current_map"],
            "current_players": current_players,
            "max_players": max_players,
            "short_name": config.short_name,
            "server_number": int(get_server_number()),
        }

    @ttl_cache(ttl=60 * 60 * 24)
    def get_maps(self) -> list[Layer]:
        return [parse_layer(m) for m in super().get_maps()]

    # TODO: fix typing
    def get_server_settings(self):
        settings = {}
        for name, type_ in self.settings:
            try:
                settings[name] = type_(getattr(self, f"get_{name}")())
            except:
                logger.exception("Failed to retrieve settings %s", name)
                raise
        return settings

    @staticmethod
    def _extract_time(raw_timestamp: str) -> datetime:
        """Parse a unix timestamp to a UTC Python datetime"""
        try:
            return datetime.utcfromtimestamp(int(raw_timestamp))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Time {raw_timestamp} is not a valid integer") from e

    @ttl_cache(ttl=60 * 10)
    def get_profanities(self) -> list[str]:
        return super().get_profanities()

    @ttl_cache(ttl=60 * 10)
    def get_autobalance_enabled(self) -> bool:
        return super().get_autobalance_enabled() == "on"

    @ttl_cache(ttl=60 * 10)
    def get_votekick_enabled(self) -> bool:
        return super().get_votekick_enabled() == "on"

    @ttl_cache(ttl=60 * 10)
    def get_votekick_thresholds(self) -> list[tuple[int, int]]:
        res = super().get_votekick_thresholds()

        if res == "":
            return []

        pairs = res.split(",")
        return [(int(pair[0]), int(pair[1])) for pair in zip(pairs[0::2], pairs[1::2])]

    def set_autobalance_enabled(self, value: bool) -> bool:
        with invalidates(self.get_autobalance_enabled):
            return super().set_autobalance_enabled("on" if value else "off")

    def set_votekick_enabled(self, value: bool) -> bool:
        with invalidates(self.get_votekick_enabled):
            return super().set_votekick_enabled("on" if value else "off")

    def set_votekick_thresholds(
        self, threshold_pairs: list[tuple[int, int]]
    ) -> str | bool:
        with invalidates(self.get_votekick_thresholds):
            flattened = [str(val) for val in chain.from_iterable(threshold_pairs)]
            res = super().set_votekick_thresholds(",".join(flattened))
            if res != SUCCESS:
                logger.error("Unable to set votekick threshold: %s", res)
                raise CommandFailedError(res)
            else:
                return res == SUCCESS

    def reset_votekick_thresholds(self) -> bool:
        with invalidates(self.get_votekick_thresholds):
            return super().reset_votekick_thresholds()

    def set_profanities(self, profanities: list[str]) -> list[str]:
        current = self.get_profanities()
        with invalidates(self.get_profanities):
            removed = set(current) - set(profanities)
            added = set(profanities) - set(current)
            if removed:
                self.unban_profanities(list(removed))
            if added:
                self.ban_profanities(list(added))

        return profanities

    def unban_profanities(self, profanities: list[str]) -> bool:
        if not isinstance(profanities, list):
            profanities = [profanities]
        with invalidates(self.get_profanities):
            return super().unban_profanities(",".join(profanities))

    def ban_profanities(self, profanities: list[str]) -> bool:
        if not isinstance(profanities, list):
            profanities = [profanities]
        with invalidates(self.get_profanities):
            return super().ban_profanities(",".join(profanities))

    def punish(self, player_name: str, reason: str, by: str) -> bool:
        res = super().punish(player_name, reason)
        safe_save_player_action(
            rcon=self,
            player_name=player_name,
            action_type=PlayerActionState.PUNISH,
            reason=reason,
            by=by,
        )
        return res

    def switch_player_now(self, player_name: str) -> bool:
        return super().switch_player_now(player_name)

    def switch_player_on_death(self, player_name, by) -> bool:
        return super().switch_player_on_death(player_name)

    def kick(self, player_name, reason, by, player_id: str | None = None) -> bool:
        with invalidates(Rcon.get_players):
            res = super().kick(player_name, reason)

        safe_save_player_action(
            rcon=self,
            player_name=player_name,
            action_type=PlayerActionState.KICK,
            reason=reason,
            by=by,
            player_id=player_id,
        )
        return res

    def temp_ban(
        self,
        player_name: str | None = None,
        player_id: str | None = None,
        duration_hours: int = 2,
        reason: str = "",
        by: str = "",
    ) -> bool:
        with invalidates(Rcon.get_players, Rcon.get_temp_bans):
            if player_name and re.match(r"\d+", player_name):
                info = self.get_player_info(player_name)
                player_id = info.get(PLAYER_ID, None)

            res = super().temp_ban(
                player_name, player_id, duration_hours, reason, admin_name=by
            )

            safe_save_player_action(
                rcon=self,
                player_name=player_name,
                action_type=PlayerActionState.TEMPBAN,
                reason=reason,
                by=by,
                player_id=player_id,
            )
            return res

    def remove_temp_ban(self, player_id: str) -> bool:
        """Remove a temp ban by player ID or game server ban log"""
        with invalidates(Rcon.get_temp_bans):
            return super().remove_temp_ban(player_id)

    def remove_perma_ban(self, player_id: str) -> bool:
        """Remove a perma ban by ban log. Note that a player ID is a valid ban log."""
        with invalidates(Rcon.get_perma_bans):
            return super().remove_perma_ban(player_id)

        return False

    def perma_ban(self, player_name=None, player_id=None, reason="", by="") -> bool:
        with invalidates(Rcon.get_players, Rcon.get_perma_bans):
            # TODO: this won't work with windows store IDs
            if player_name and re.match(r"\d+", player_name):
                info = self.get_player_info(player_name)
                player_id = info.get(PLAYER_ID, None)

            res = super().perma_ban(player_name, player_id, reason, admin_name=by)
            safe_save_player_action(
                rcon=self,
                player_name=player_name,
                action_type=PlayerActionState.PERMABAN,
                reason=reason,
                by=by,
                player_id=player_id,
            )
            return res

    @ttl_cache(60 * 5)
    def get_map_rotation(self) -> list[Layer]:
        l = super().get_map_rotation()

        maps: list[Layer] = []
        for map_ in l:
            if not self.map_regexp.match(map_):
                raise CommandFailedError("Server return wrong data")

            maps.append(parse_layer(map_))
        return maps

    def add_map_to_rotation(
        self,
        map_name: str,
        after_map_name: str | None = None,
        after_map_name_number: int | None = None,
    ) -> str:
        with invalidates(Rcon.get_map_rotation, Rcon.get_next_map):
            if after_map_name is None:
                current = [map_.id for map_ in self.get_map_rotation()]
                after_map_name = current[len(current) - 1]
                after_map_name_number = current.count(after_map_name)

            return super().add_map_to_rotation(
                map_name, after_map_name, after_map_name_number
            )

    def remove_map_from_rotation(self, map_name: str, map_number: int | None = None):
        with invalidates(Rcon.get_map_rotation, Rcon.get_next_map):
            return super().remove_map_from_rotation(map_name, map_number)

    def remove_maps_from_rotation(self, map_names: list[str]) -> Literal["SUCCESS"]:
        with invalidates(Rcon.get_map_rotation, Rcon.get_next_map):
            for map_name in map_names:
                super().remove_map_from_rotation(map_name)
            return SUCCESS

    def add_maps_to_rotation(self, map_names: list[str]) -> list[tuple[str, str]]:
        """Add the given maps to the rotation, returns the game server response for each map"""
        with invalidates(Rcon.get_map_rotation, Rcon.get_next_map):
            existing = [map_.id for map_ in self.get_map_rotation()]
            last = existing[len(existing) - 1]
            map_numbers = {last: existing.count(last)}
            results: list[tuple[str, str]] = []
            for map_name in map_names:
                res = super().add_map_to_rotation(
                    map_name, last, map_numbers.get(last, 1)
                )
                results.append((map_name, res))
                last = map_name
                map_numbers[last] = map_numbers.get(last, 0) + 1

        return results

    def set_maprotation(self, map_names: list[str]) -> list[Layer]:
        if not map_names:
            raise CommandFailedError("Empty rotation")

        map_names = list(map_names)
        logger.info("Apply map rotation %s", map_names)

        with invalidates(Rcon.get_map_rotation, Rcon.get_next_map):
            current_as_layers = self.get_map_rotation()
            current = [map_.id for map_ in current_as_layers]
            logger.info("Current rotation: %s", current)
            if map_names == current:
                logger.debug("Map rotation is the same, nothing to do")
                return current_as_layers

            # we remove all but the first
            for map_ in current[1:]:
                map_without_number = map_.rsplit(" ")[0]
                logger.info("Removing from rotation: '%s'", map_without_number)
                super().remove_map_from_rotation(map_without_number)

            if len(current) > 0:
                last = current[0]
                map_number = {last: 1}
            else:
                last = map_names[0]
                map_number = {}

            for map_ in map_names:
                logger.info("Adding to rotation: '%s'", map_)
                super().add_map_to_rotation(map_, last, map_number.get(last, 1))
                last = map_
                map_number[last] = map_number.get(last, 0) + 1

            # Now we can remove the first from the previous rotation
            super().remove_map_from_rotation(current[0], 1)

        return self.get_map_rotation()

    @ttl_cache(ttl=10)
    def get_objective_row(self, row: int):
        return super().get_objective_row(row)

    def get_objective_rows(self) -> List[List[str]]:
        return [self.get_objective_row(row) for row in range(5)]

    def set_game_layout(
        self,
        objectives: Sequence[str | int | None],
        random_constraints: GameLayoutRandomConstraints = 0,
    ):
        if len(objectives) != 5:
            raise ValueError("5 objectives must be provided")

        obj_rows = self.get_objective_rows()
        parsed_objs: list[str] = []
        for row, (obj, obj_row) in enumerate(zip(objectives, obj_rows)):
            if isinstance(obj, str):
                # Verify whether the objective exists, or if it can be logically determined
                if obj in obj_row:
                    parsed_objs.append(obj)
                elif obj in ("left", "top"):
                    parsed_objs.append(obj_row[0])
                elif obj in ("center", "mid"):
                    parsed_objs.append(obj_row[1])
                elif obj in ("right", "bottom"):
                    parsed_objs.append(obj_row[2])
                else:
                    raise ValueError(
                        "Objective %s does not exist in row %s" % (obj, row)
                    )

            elif isinstance(obj, int):
                # Use index of the objective
                if not (0 <= obj <= 2):
                    raise ValueError(
                        "Objective index %s is out of range 0-2 in row %s"
                        % (obj, row + 1)
                    )
                parsed_objs.append(obj_row[obj])

            elif obj is None:
                # Choose randomly
                if random_constraints:
                    # Sort later
                    parsed_objs.append(None)
                else:
                    # No constraints, no need for a special algorithm
                    parsed_objs.append(random.choice(obj_row))

        # Special algorithm to apply randomness with constraints. Prioritizes rows with already
        # determined neighbors to avoid conflicts in situations with two neighbors.
        while None in parsed_objs:
            # If no rows are predetermined, determine the middle row first
            if all(obj is None for obj in parsed_objs):
                parsed_objs[2] = random.choice(obj_rows[2])

            for row, obj in enumerate(parsed_objs):
                # Skip if row is already determined
                if obj is not None:
                    continue

                # Get the indices of the objectives of neighboring rows, if they are already determined
                neighbors = []
                if row > 0 and parsed_objs[row - 1] is not None:
                    neighbors.append(obj_rows[row - 1].index(parsed_objs[row - 1]))
                if row < 4 and parsed_objs[row + 1] is not None:
                    neighbors.append(obj_rows[row + 1].index(parsed_objs[row + 1]))

                # Skip this row for now if neither of its neighbors had their objective determined yet
                if not neighbors:
                    continue

                # Create a list of available objectives
                obj_row = obj_rows[row]
                obj_choices = obj_row.copy()
                for neighbor_idx in neighbors:
                    # Apply constraints
                    if random_constraints & GameLayoutRandomConstraints.ALWAYS_ADJACENT:
                        # Cannot have two objectives follow each other up on opposite sides of the map
                        if neighbor_idx == 0:
                            obj_choices[2] = None
                        elif neighbor_idx == 2:
                            obj_choices[0] = None
                    if random_constraints & GameLayoutRandomConstraints.ALWAYS_DIAGONAL:
                        # Cannot have two objectives in a straight row
                        obj_choices[neighbor_idx] = None

                # Pick an objective. If none are viable, discard constraints.
                parsed_objs[row] = random.choice(
                    [c for c in obj_choices if c is not None] or obj_row
                )

        red = get_redis_client()
        red.set('GAME_LAYOUT', json.dumps(GameLayout(requested=objectives, set=parsed_objs)))
        return super().set_game_layout(parsed_objs)

    @staticmethod
    def parse_log_line(raw_line: str) -> StructuredLogLineType:
        """Parse a single raw RCON log event or raise a ValueError"""

        player: str | None = None
        player2: str | None = None
        player_id_1: str | None = None
        player_id_2: str | None = None
        weapon: str | None = None
        action: str | None = None
        content: str = raw_line
        sub_content: str | None = None

        if raw_line.startswith("KILL") or raw_line.startswith("TEAM KILL"):
            # KILL: Muctar(Axis/71234567891234567) -> Chris(Allies/71234567891234576) with GEWEHR 43
            # TEAM KILL: SonofJack(Allies/71234567891234567) -> Joseph Cannon(Allies/71234567891234576) with M1 GARAND
            action, content = raw_line.split(": ", 1)
            if match := re.match(Rcon.kill_teamkill_pattern, content):
                player, player_id_1, player2, player_id_2, weapon = match.groups()
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")
        elif raw_line.startswith("DISCONNECTED") or raw_line.startswith("CONNECTED"):
            action, name_and_player_id = raw_line.split(" ", 1)
            if match := re.match(Rcon.connect_disconnect_pattern, name_and_player_id):
                player, player_id_1 = match.groups()
                content = name_and_player_id
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")
        elif raw_line.startswith("CHAT"):
            # CHAT[Team][Azure(Allies/71234567891234567)]: supply truck bot hq for nodes
            # CHAT[Unit][dominguez1987(Axis/71234567891234567)]: back
            if match := Rcon.chat_regexp.match(raw_line):
                scope, player, side, player_id_1, sub_content = match.groups()
                action = f"CHAT[{side}][{scope}]"
                content = f"{player}: {sub_content} ({player_id_1})"
        elif raw_line.upper().startswith("TEAMSWITCH"):
            # TEAMSWITCH Plebs_23 (Axis > None)
            # TEAMSWITCH SupremeOneechan (None > Allies)
            action = "TEAMSWITCH"
            if match := re.match(Rcon.teamswitch_pattern, raw_line):
                player, sub_content = match.groups()
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")
        elif raw_line.startswith("KICK") or raw_line.startswith("BAN"):
            if match := re.match(Rcon.kick_ban_pattern, raw_line):
                _action, player, sub_content, type_ = match.groups()
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")

            if type_ == "PERMANENTLY":
                type_ = "PERMA BANNED"
            elif type_ == "YOU":
                type_ = "IDLE"
            elif type_ == "Host":
                type_ = ""
            elif type_ == "Anti-Cheat":
                type_ = "ANTI-CHEAT"
            elif type_ == "KICKED":
                type_ = "KICKED"
            elif type_ == "BANNED":
                type_ = "BANNED"
            else:
                type_ = "MISC"

            action = f"ADMIN {type_}".strip()

            if "FOR TEAM KILLING" in raw_line:
                action = f"TK AUTO {type_}"

            # Reconstruct the log line without the newlines and tack on the trailing ] we lose
            content = f"{_action}: [{player}] {sub_content}"
            if content[-1] != "]":
                content += "]"
                sub_content = sub_content + "]" if sub_content else ""
        elif raw_line.startswith("VOTE"):
            action = "VOTE"

            _, sub_content = raw_line.split("VOTESYS: ", 1)
            content = sub_content

            # VOTESYS: Player [Dingbat252] voted [PV_Favour] for VoteID[2]
            if match := re.match(Rcon.vote_pattern, raw_line):
                player = match.groups()[0]
            # VOTESYS: Player [NoodleArms] Started a vote of type (PVR_Kick_Abuse) against [buscÃ´O-sensei]. VoteID: [2]
            elif match := re.match(
                Rcon.vote_started_pattern,
                raw_line,
            ):
                action = "VOTE STARTED"
                player, player2 = match.groups()
            # VOTESYS: Vote [2] completed. Result: PVR_Passed
            elif match := re.match(Rcon.vote_complete_pattern, raw_line):
                action = "VOTE COMPLETED"
            # VOTESYS: Vote [1] expired before completion.
            elif match := re.match(Rcon.vote_expired_pattern, raw_line):
                action = "VOTE EXPIRED"
            # VOTESYS: Vote Kick {buscÃ´O-sensei} successfully passed. [For: 2/1 - Against: 0]
            elif match := re.match(Rcon.vote_passed_pattern, raw_line):
                action = "VOTE PASSED"
                content, player, sub_content = match.groups()
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")

        elif raw_line.upper().startswith("PLAYER"):
            # Player [Fachi (71234567891234567)] Entered Admin Camera
            action = "CAMERA"
            _, content = raw_line.split(" ", 1)

            if match := re.match(Rcon.camera_pattern, content):
                player, player_id_1, sub_content = match.groups()
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")

        elif raw_line.upper().startswith("MATCH START"):
            # MATCH START UTAH BEACH WARFARE
            action = "MATCH START"
            _, sub_content = raw_line.split("MATCH START ")
            content = raw_line
        elif raw_line.upper().startswith("MATCH ENDED"):
            # MATCH ENDED `Kharkov WARFARE` ALLIED (0 - 5) AXIS
            action = "MATCH ENDED"
            _, sub_content = raw_line.split("MATCH ENDED ")
        elif raw_line.upper().startswith("MESSAGE"):
            action = "MESSAGE"
            raw_line = raw_line.replace("\n", " ")
            content = raw_line
            if match := re.match(Rcon.message_pattern, raw_line):
                player, player_id_1, message_content = match.groups()
                content = f"{player}({player_id_1}): {message_content}"
                sub_content = message_content
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")

        if action is None:
            raise ValueError(f"Unknown type line: '{raw_line}'")

        return {
            "action": action,
            "player_name_1": player,
            "player_id_1": player_id_1,
            "player_name_2": player2,
            "player_id_2": player_id_2,
            "weapon": weapon,
            "message": content,
            "sub_content": sub_content,
        }

    @staticmethod
    def split_raw_log_lines(raw_logs: str) -> Iterable[tuple[str, str, str]]:
        """Split raw game server logs into the relative time, timestamp and content"""
        if raw_logs != "":
            logs = raw_logs.strip("\n")
            logs = re.split(r"^(\[.+? \((\d+)\)\])", logs, flags=re.M)
            logs = zip(logs[1::3], logs[2::3], logs[3::3])
            for raw_relative_time, raw_timestamp, raw_log_line in logs:
                yield raw_relative_time, raw_timestamp, raw_log_line.strip()

    @staticmethod
    def parse_logs(
        raw_logs: str,
        filter_action: str | None = None,
        filter_player: str | None = None,
    ) -> ParsedLogsType:
        """Parse a chunk of raw gameserver RCON logs"""
        synthetic_actions = LOG_ACTIONS
        now = datetime.now()
        parsed_log_lines: list[StructuredLogLineWithMetaData] = []
        actions: set[str] = set()
        players: set[str] = set()

        for raw_relative_time, raw_timestamp, raw_log_line in Rcon.split_raw_log_lines(
            raw_logs
        ):
            time = Rcon._extract_time(raw_timestamp)
            try:
                log_line = Rcon.parse_log_line(raw_log_line)

                if filter_action and not log_line["action"].startswith(filter_action):
                    continue

                if filter_player and filter_player not in raw_log_line:
                    continue

                parsed_log_lines.append(
                    {
                        "version": 1,
                        "timestamp_ms": int(time.timestamp() * 1000),
                        "event_time": datetime.fromtimestamp(int(raw_timestamp)),
                        "relative_time_ms": (time - now).total_seconds() * 1000,
                        "raw": raw_relative_time + " " + raw_log_line,
                        "line_without_time": raw_log_line,
                        "action": log_line["action"],
                        "player_name_1": log_line["player_name_1"],
                        "player_id_1": log_line["player_id_1"],
                        "player_name_2": log_line["player_name_2"],
                        "player_id_2": log_line["player_id_2"],
                        "weapon": log_line["weapon"],
                        "message": log_line["message"],
                        "sub_content": log_line["sub_content"],
                    }
                )
            except ValueError:
                logger.error(
                    f"Unable to parse line: '{raw_relative_time} {raw_timestamp} {raw_log_line}'"
                )
                continue

            if player := log_line["player_name_1"]:
                players.add(player)

            if player2 := log_line["player_name_2"]:
                players.add(player2)

            actions.add(log_line["action"])

        parsed_log_lines.reverse()

        return {
            "actions": list(actions | set(synthetic_actions)),
            "players": list(players),
            "logs": parsed_log_lines,
        }

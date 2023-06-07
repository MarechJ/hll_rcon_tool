import logging
import os
import re
from concurrent.futures import as_completed
from datetime import datetime, timedelta
from functools import update_wrapper
from time import sleep
from typing import Dict, Iterable, List, Optional, Tuple, Union, TypedDict

from rcon.cache_utils import get_redis_client, invalidates, ttl_cache
from rcon.commands import CommandFailedError, ServerCtl, VipId
from rcon.models import PlayerVIP, enter_session
from rcon.steam_utils import (
    get_player_country_code,
    get_player_has_bans,
    get_players_country_code,
    get_players_have_bans,
)
from rcon.types import (
    GameState,
    GetPlayersType,
    ParsedLogsType,
    StructuredLogLineType,
    StructuredLogLineWithMetaData,
    GetDetailedPlayer,
)
from rcon.utils import get_server_number

STEAMID = "steam_id_64"
NAME = "name"
ROLE = "role"
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

MOD_ALLOWED_CMDS = set()


def mod_users_allowed(func):
    """Wrapper to flag a method as something that moderator
    accounts are allowed to use.

    Moderator accounts should be able to manage online players,
    for instance banning them. Viewing or changing server settings
    like map rotation or VIPs should not be allowed.
    """
    MOD_ALLOWED_CMDS.add(func.__name__)
    update_wrapper(wrapper=mod_users_allowed, wrapped=func)
    return func


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
        ("votekick_threshold", str),
    )
    MAX_SERV_NAME_LEN = 1024  # I totally made up that number. Unable to test
    slots_regexp = re.compile(r"^\d{1,3}/\d{2,3}$")
    map_regexp = re.compile(r"^(\w+_?)+$")
    chat_regexp = re.compile(
        r"CHAT\[(Team|Unit)\]\[(.*)\((Allies|Axis)/(\d+)\)\]: (.*)"
    )
    player_info_pattern = r"(.*)\(((Allies)|(Axis))/(\d+)\)"
    player_info_regexp = re.compile(r"(.*)\(((Allies)|(Axis))/(\d+)\)")
    log_time_regexp = re.compile(r".*\((\d+)\).*")
    connect_disconnect_pattern = re.compile(r"(.+) \((\d+)\)")
    # Checking for steam ID length so people can't exploit it with a name like: short(Axis/123) ->
    kill_teamkill_pattern = re.compile(
        r"(.*)\((?:Allies|Axis)\/(\d{17})\) -> (.*)\((?:Allies|Axis)\/(\d{17})\) with (.*)"
    )
    camera_pattern = re.compile(r"\[(.*)\s{1}\((\d+)\)\] (.*)")
    teamswitch_pattern = re.compile(r"TEAMSWITCH\s(.*)\s\((.*\s>\s.*)\)")
    kick_ban_pattern = re.compile(
        r"(KICK|BAN): \[(.*)\] (.*\[(KICKED|BANNED|PERMANENTLY|YOU|Host|Anti-Cheat)[^\]]*)(?:\])*"
    )
    vote_pattern = re.compile(
        r"VOTESYS: Player \[(.*)\] voted \[.*\] for VoteID\[\d+\]"
    )
    vote_started_pattern = re.compile(
        r"VOTESYS: Player \[(.*)\] Started a vote of type \(.*\) against \[(.*)\]. VoteID: \[\d+\]"
    )
    vote_complete_pattern = re.compile(r"VOTESYS: Vote \[\d+\] completed. Result: (.*)")
    vote_expired_pattern = re.compile(r"VOTESYS: Vote \[\d+\] expired")
    vote_passed_pattern = re.compile(r"VOTESYS: (Vote Kick \{(.*)\} .*\[(.*)\])")
    # Need the DOTALL flag to allow `.` to capture newlines in multi line messages
    message_pattern = re.compile(
        r"MESSAGE: player \[(.+)\((\d+)\)\], content \[(.+)\]", re.DOTALL
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @mod_users_allowed
    def get_playerids(self, as_dict=False):
        raw_list = super().get_playerids()

        player_list = []
        player_dict = {}
        for playerinfo in raw_list:
            name, steamid = playerinfo.rsplit(":", 1)
            name = name[:-1]
            steamid = steamid[1:]
            player_dict[name] = steamid
            player_list.append((name, steamid))

        return player_dict if as_dict else player_list

    @mod_users_allowed
    def get_vips_count(self):
        players = self.get_playerids()

        vips = {v["steam_id_64"] for v in self.get_vip_ids()}
        vip_count = 0
        for _, steamid in players:
            if steamid in vips:
                vip_count += 1

        return vip_count

    def _guess_squad_type(self, squad):
        for player in squad.get("players", []):
            if player.get("role") in ["tankcommander", "crewman"]:
                return "armor"
            if player.get("role") in ["spotter", "sniper"]:
                return "recon"
            if player.get("role") in ["armycommander"]:
                return "commander"

        return "infantry"

    def _has_leader(self, squad):
        for players in squad.get("players", []):
            if players.get("role") in ["tankcommander", "officer", "spotter"]:
                return True
        return False

    @mod_users_allowed
    @ttl_cache(ttl=60 * 60 * 24, cache_falsy=False)
    def get_player_info(self, player, can_fail=False):
        try:
            try:
                raw = super().get_player_info(player, can_fail=can_fail)
                name, steam_id_64, *rest = raw.split("\n")
            except (CommandFailedError, Exception):
                sleep(2)
                name = player
                steam_id_64 = self.get_playerids(as_dict=True).get(name)
            if not steam_id_64:
                return {}

            country = get_player_country_code(steam_id_64)
            steam_bans = get_player_has_bans(steam_id_64)

        except (CommandFailedError, ValueError):
            # Making that debug instead of exception as it's way to spammy
            logger.exception("Can't get player info for %s", player)
            # logger.exception("Can't get player info for %s", player)
            return {}
        name = name.split(": ", 1)[-1]
        steam_id = steam_id_64.split(": ", 1)[-1]
        if name != player:
            logger.error(
                "get_player_info('%s') returned for a different name: %s %s",
                player,
                name,
                steam_id,
            )
            return {}
        return {
            NAME: name,
            STEAMID: steam_id,
            "country": country,
            "steam_bans": steam_bans,
        }

    def _get_default_info_dict(self, player) -> GetDetailedPlayer:
        return dict(
            name=player,
            unit_id=None,
            unit_name=None,
            loadout=None,
            team=None,
            role=None,
            kills=0,
            deaths=0,
            combat=0,
            offense=0,
            defense=0,
            support=0,
            level=0,
        )

    @mod_users_allowed
    @ttl_cache(ttl=2, cache_falsy=False)
    def get_detailed_player_info(self, player) -> GetDetailedPlayer:
        raw = super().get_player_info(player)
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

        data = self._get_default_info_dict(player)
        raw_data = {}

        for line in raw.split("\n"):
            if not line:
                continue
            if ": " not in line:
                logger.warning("Invalid info line: %s", line)
                continue

            key, val = line.split(": ", 1)
            raw_data[key.lower()] = val

        logger.debug(raw_data)
        # Remap keys and parse values
        data[STEAMID] = raw_data.get("steamid64")
        data["team"] = raw_data.get("team", "None")
        if raw_data["role"].lower() == "armycommander":
            data["unit_id"], data["unit_name"] = (-1, "Commmand")
        else:
            data["unit_id"], data["unit_name"] = (
                raw_data.get("unit").split(" - ")
                if raw_data.get("unit")
                else ("None", None)
            )
        data["kills"], data["deaths"] = (
            raw_data.get("kills").split(" - Deaths: ")
            if raw_data.get("kills")
            else ("0", "0")
        )
        for k in ["role", "loadout", "level"]:
            data[k] = raw_data.get(k)

        scores = dict(
            [
                score.split(" ", 1)
                for score in raw_data.get("score", "C 0, O 0, D 0, S 0").split(", ")
            ]
        )
        map_score = {"C": "combat", "O": "offense", "D": "defense", "S": "support"}
        for key, val in map_score.items():
            data[map_score[key]] = scores.get(key, "0")

        # Typecast values
        # cast strings to lower
        for key in ["team", "unit_name", "role", "loadout"]:
            data[key] = data[key].lower() if data.get(key) else None

        # cast string numbers to ints
        for key in [
            "kills",
            "deaths",
            "level",
            "combat",
            "offense",
            "defense",
            "support",
            "unit_id",
        ]:
            try:
                data[key] = int(data[key])
            except (ValueError, TypeError):
                data[key] = 0

        return data

    @mod_users_allowed
    @ttl_cache(ttl=60 * 60 * 24)
    def get_admin_ids(self):
        res = super().get_admin_ids()
        admins = []
        for item in res:
            steam_id_64, role, name = item.split(" ", 2)
            admins.append({STEAMID: steam_id_64, NAME: name[1:-1], ROLE: role})
        return admins

    @mod_users_allowed
    def get_online_console_admins(self):
        admins = self.get_admin_ids()
        players = self.get_players()
        online = []
        admins_ids = set(a["steam_id_64"] for a in admins)

        for player in players:
            if player["steam_id_64"] in admins_ids:
                online.append(player["name"])

        return online

    def do_add_admin(self, steam_id_64, role, name):
        with invalidates(Rcon.get_admin_ids):
            return super().do_add_admin(steam_id_64, role, name)

    def do_remove_admin(self, steam_id_64):
        with invalidates(Rcon.get_admin_ids):
            return super().do_remove_admin(steam_id_64)

    @mod_users_allowed
    @ttl_cache(ttl=2)
    def get_players_fast(self) -> List[GetPlayersType]:
        players = {}
        ids = []

        for name, steam_id_64 in self.get_playerids():
            players[steam_id_64] = {NAME: name, STEAMID: steam_id_64}
            ids.append(steam_id_64)

        countries = self.thread_pool.submit(get_players_country_code, ids)
        bans = self.thread_pool.submit(get_players_have_bans, ids)

        for future in as_completed([countries, bans]):
            d = future.result()
            for steamid, data in d.items():
                players.get(steamid, {}).update(data)

        return list(players.values())

    @mod_users_allowed
    @ttl_cache(ttl=5)
    def get_players(self):
        return self.get_players_fast()

        # Below is legacy
        names = super().get_players()
        players = []
        for n in names:
            player = {NAME: n}
            player.update(self.get_player_info(n))
            players.append(player)

        return players

    @mod_users_allowed
    @ttl_cache(ttl=60)
    def get_perma_bans(self):
        return super().get_perma_bans()

    @mod_users_allowed
    @ttl_cache(ttl=60)
    def get_temp_bans(self):
        res = super().get_temp_bans()
        logger.debug(res)
        return res

    def _struct_ban(self, ban, type_):
        # Avoid errors on empty temp bans
        if ban == "":
            return {
                "type": type_,
                "name": None,
                "steam_id_64": None,
                "timestamp": None,
                "ban_time": None,
                "reason": None,
                "by": None,
                "raw": ban,
            }

        # name, time = ban.split(', banned on ')
        # '76561197984877751 : nickname "Dr.WeeD" banned for 2 hours on 2020.12.03-12.40.08 for "None" by admin "test"'
        steamd_id_64, rest = ban.split(" :", 1)
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
            "steam_id_64": steamd_id_64,
            # TODO FIX
            "timestamp": None,
            "ban_time": date,
            "reason": reason,
            "by": by.replace('"', ""),
            "raw": ban,
        }

    @mod_users_allowed
    def get_bans(self):
        try:
            temp_bans = []
            for b in self.get_temp_bans():
                try:
                    temp_bans.append(self._struct_ban(b, "temp"))
                except ValueError:
                    logger.exception("Invalid temp ban line: %s", b)
            bans = []
            for b in self.get_perma_bans():
                try:
                    bans.append(self._struct_ban(b, "perma"))
                except ValueError:
                    logger.exception("Invalid perm ban line: %s", b)
        except Exception:
            self.get_temp_bans.cache_clear()
            self.get_perma_bans.cache_clear()
            raise
        # Most recent first
        bans.reverse()
        return temp_bans + bans

    @mod_users_allowed
    def do_unban(self, steam_id_64) -> List[str]:
        """Remove all temporary and permanent bans from the steam_id_64"""
        bans = self.get_bans()
        type_to_func = {
            "temp": self.do_remove_temp_ban,
            "perma": self.do_remove_perma_ban,
        }
        failed_ban_removals: List[str] = []
        for b in bans:
            if b.get("steam_id_64") == steam_id_64:
                # TODO: This is no longer true as of U13
                # The game server will sometimes continue to report expired temporary bans
                # (verified as of 10 Aug 2022 U12 Hotfix)
                # which will prevent removing permanent bans if we don't catch the failed removal

                # We swallow exceptions here and test for failed unbans in views.py
                try:
                    type_to_func[b["type"]](b["raw"])
                except CommandFailedError:
                    message = f"Unable to remove {b['type']} ban from {steam_id_64}"
                    logger.exception(message)
                    failed_ban_removals.append(message)

        return failed_ban_removals

    @mod_users_allowed
    def get_ban(self, steam_id_64):
        """
        get all bans from steam_id_64
        @param steam_id_64: steam_id_64 of a user
        @return: a array of bans
        """
        bans = self.get_bans()
        return list(filter(lambda x: x.get("steam_id_64") == steam_id_64, bans))

    @mod_users_allowed
    @ttl_cache(ttl=60 * 60)
    def get_vip_ids(self) -> List[Dict[str, Union[str, Optional[datetime]]]]:
        res: List[VipId] = super().get_vip_ids()
        player_dicts = []

        vip_expirations: Dict[str, datetime]
        with enter_session() as session:
            server_number = get_server_number()

            players: list[PlayerVIP] = (
                session.query(PlayerVIP)
                .filter(PlayerVIP.server_number == server_number)
                .all()
            )
            vip_expirations = {
                player.steamid.steam_id_64: player.expiration for player in players
            }

        for item in res:
            player = dict(zip((STEAMID, NAME), (item["steam_id_64"], item["name"])))
            player["vip_expiration"] = vip_expirations.get(item["steam_id_64"], None)
            player_dicts.append(player)

        return sorted(player_dicts, key=lambda d: d[NAME])

    def do_remove_vip(self, steam_id_64):
        with invalidates(Rcon.get_vip_ids):
            return super().do_remove_vip(steam_id_64)

    def do_add_vip(self, name, steam_id_64):
        with invalidates(Rcon.get_vip_ids):
            return super().do_add_vip(steam_id_64, name)

    def do_remove_all_vips(self):
        vips = self.get_vip_ids()
        for vip in vips:
            try:
                self.do_remove_vip(vip["steam_id_64"])
            except (CommandFailedError, ValueError):
                raise

        return "SUCCESS"

    @mod_users_allowed
    def get_gamestate(self) -> GameState:
        """
        Returns player counts, team scores, remaining match time and current/next map

        Players: Allied: 0 - Axis: 1
        Score: Allied: 2 - Axis: 2
        Remaining Time: 0:11:51
        Map: foy_warfare
        Next Map: stmariedumont_warfare"""
        with invalidates(
            Rcon.team_sizes, Rcon.team_objective_scores, Rcon.round_time_remaining
        ):
            (
                raw_team_size,
                raw_score,
                raw_time_remaining,
                raw_current_map,
                raw_next_map,
            ) = super().get_gamestate()

        num_allied_players, num_axis_players = re.match(
            r"Players: Allied: (\d+) - Axis: (\d+)", raw_team_size
        ).groups()
        allied_score, axis_score = re.match(
            r"Score: Allied: (\d+) - Axis: (\d+)", raw_score
        ).groups()
        hours, mins, secs = re.match(
            r"Remaining Time: (\d):(\d{2}):(\d{2})", raw_time_remaining
        ).groups()

        raw_time_remaining = raw_time_remaining.split("Remaining Time: ")[1]
        current_map = raw_current_map.split(": ")[1]
        next_map = raw_next_map.split(": ")[1]

        return {
            "num_allied_players": int(num_allied_players),
            "num_axis_players": int(num_axis_players),
            "allied_score": int(allied_score),
            "axis_score": int(axis_score),
            "time_remaining": timedelta(
                hours=float(hours), minutes=float(mins), seconds=float(secs)
            ),
            "raw_time_remaining": raw_time_remaining,
            "current_map": current_map,
            "next_map": next_map,
        }

    @ttl_cache(ttl=2, cache_falsy=False)
    def team_sizes(self) -> Tuple[int, int]:
        """Returns the number of allied/axis players respectively"""
        result = self.get_gamestate()

        return result["num_allied_players"], result["num_axis_players"]

    @ttl_cache(ttl=2, cache_falsy=False)
    def team_objective_scores(self) -> Tuple[int, int]:
        """Returns the number of objectives held by the allied/axis team respectively"""
        result = self.get_gamestate()

        return result["allied_score"], result["axis_score"]

    @ttl_cache(ttl=2, cache_falsy=False)
    def round_time_remaining(self) -> timedelta:
        """Returns the amount of time left in the round as a timedelta"""
        result = self.get_gamestate()

        return result["time_remaining"]

    @mod_users_allowed
    @ttl_cache(ttl=60)
    def get_next_map(self):
        # TODO: think about whether or not the new gamestate command can simplify this
        current = self.get_map()
        current = current.replace("_RESTART", "")
        rotation = self.get_map_rotation()
        try:
            next_id = rotation.index(current)
            next_id += 1
            if next_id == len(rotation):
                next_id = 0
            return rotation[next_id]
        except ValueError:
            logger.error(
                "Can't find %s in rotation, assuming next map as first map of rotation",
                current,
            )
            return rotation[0]

    def set_map(self, map_name):
        with invalidates(Rcon.get_map):
            try:
                res = super().set_map(map_name)
                if res != "SUCCESS":
                    raise CommandFailedError(res)
            except CommandFailedError:
                maps = self.get_map_rotation()
                self.do_add_map_to_rotation(map_name, maps[len(maps) - 1], maps.count(maps[len(maps) - 1]))
                if super().set_map(map_name) != "SUCCESS":
                    raise CommandFailedError(res)

    @mod_users_allowed
    @ttl_cache(ttl=10)
    def get_map(self):
        # TODO: think about whether or not the new gamestate command can simplify this
        current_map = super().get_map()
        if not self.map_regexp.match(current_map):
            raise CommandFailedError("Server returned wrong data")

        return current_map

    @ttl_cache(ttl=60 * 60)
    def get_current_map_sequence(self):
        return super().get_current_map_sequence()

    @ttl_cache(ttl=60 * 60)
    def get_map_shuffle_enabled(self):
        return super().get_map_shuffle_enabled()

    def set_map_shuffle_enabled(self, enabled: bool):
        with invalidates(Rcon.get_current_map_sequence, Rcon.get_map_shuffle_enabled):
            return super().set_map_shuffle_enabled(enabled)

    @mod_users_allowed
    @ttl_cache(ttl=60 * 60)
    def get_name(self):
        name = super().get_name()
        if len(name) > self.MAX_SERV_NAME_LEN:
            raise CommandFailedError("Server returned wrong data")
        return name

    @ttl_cache(ttl=60 * 60)
    def get_team_switch_cooldown(self):
        return int(super().get_team_switch_cooldown())

    def set_team_switch_cooldown(self, minutes):
        with invalidates(Rcon.get_team_switch_cooldown):
            return super().set_team_switch_cooldown(minutes)

    @ttl_cache(ttl=60 * 60)
    def get_autobalance_threshold(self):
        return int(super().get_autobalance_threshold())

    def set_autobalance_threshold(self, max_diff):
        with invalidates(Rcon.get_autobalance_threshold):
            return super().set_autobalance_threshold(max_diff)

    @ttl_cache(ttl=60 * 60)
    def get_idle_autokick_time(self):
        return int(super().get_idle_autokick_time())

    def set_idle_autokick_time(self, minutes):
        with invalidates(Rcon.get_idle_autokick_time):
            return super().set_idle_autokick_time(minutes)

    @ttl_cache(ttl=60 * 60)
    def get_max_ping_autokick(self):
        return int(super().get_max_ping_autokick())

    def set_max_ping_autokick(self, max_ms):
        with invalidates(Rcon.get_max_ping_autokick):
            return super().set_max_ping_autokick(max_ms)

    @ttl_cache(ttl=60 * 60)
    def get_queue_length(self):
        return int(super().get_queue_length())

    def set_queue_length(self, num):
        with invalidates(Rcon.get_queue_length):
            return super().set_queue_length(num)

    @ttl_cache(ttl=60 * 60)
    def get_vip_slots_num(self):
        return super().get_vip_slots_num()

    def set_vip_slots_num(self, num):
        with invalidates(Rcon.get_vip_slots_num):
            return super().set_vip_slots_num(num)

    def get_welcome_message(self):
        red = get_redis_client()
        msg = red.get("WELCOME_MESSAGE")
        if msg:
            return msg.decode()
        return msg

    def set_welcome_message(self, msg, save=True):
        from rcon.broadcast import format_message

        prev = None

        try:
            red = get_redis_client()
            if save:
                prev = red.getset("WELCOME_MESSAGE", msg)
            else:
                prev = red.get("WELCOME_MESSAGE")
            red.expire("WELCOME_MESSAGE", 60 * 60 * 24 * 7)
        except Exception:
            logger.exception("Can't save message in redis: %s", msg)

        try:
            formatted = format_message(self, msg)
        except Exception:
            logger.exception("Unable to format message")
            formatted = msg

        super().set_welcome_message(formatted)
        return prev.decode() if prev else ""

    def get_broadcast_message(self):
        red = get_redis_client()
        msg = red.get("BROADCAST_MESSAGE")
        if isinstance(msg, (str, bytes)):
            return msg.decode()
        return msg

    def set_broadcast(self, msg, save=True):
        from rcon.broadcast import format_message

        prev = None

        try:
            red = get_redis_client()
            if save:
                prev = red.getset("BROADCAST_MESSAGE", msg)
            else:
                prev = red.get("BROADCAST_MESSAGE")
            red.expire("BROADCAST_MESSAGE", 60 * 30)
        except Exception:
            logger.exception("Can't save message in redis: %s", msg)

        try:
            formatted = format_message(self, msg)
        except Exception:
            logger.exception("Unable to format message")
            formatted = msg

        super().set_broadcast(formatted)
        return prev.decode() if prev else ""

    @mod_users_allowed
    @ttl_cache(ttl=5)
    def get_slots(self):
        res = super().get_slots()
        if not self.slots_regexp.match(res):
            raise CommandFailedError("Server returned crap")
        return res

    @mod_users_allowed
    @ttl_cache(ttl=5, cache_falsy=False)
    def get_status(self):
        slots = self.get_slots()
        return {
            "name": self.get_name(),
            "map": self.get_map(),
            "nb_players": slots,
            "short_name": os.getenv("SERVER_SHORT_NAME", None) or "HLL Rcon",
            "player_count": slots.split("/")[0],
        }

    @ttl_cache(ttl=60 * 60 * 24)
    def get_maps(self):
        return super().get_maps()

    def get_server_settings(self):
        settings = {}
        for name, type_ in self.settings:
            try:
                settings[name] = type_(getattr(self, f"get_{name}")())
            except:
                logger.exception("Failed to retrieve settings %s", name)
                raise
        return settings

    def do_save_setting(self, name, value):
        if not name in dict(self.settings):
            raise ValueError(f"'{name}' can't be save with this method")

        return getattr(self, f"set_{name}")(value)

    def _convert_relative_time(self, from_, time_str):
        time, unit = time_str.split(" ")
        if unit == "ms":
            return from_ - timedelta(milliseconds=int(time))
        if unit == "sec":
            return from_ - timedelta(seconds=float(time))
        if unit == "min":
            minutes, seconds = time.split(":")
            return from_ - timedelta(minutes=float(minutes), seconds=float(seconds))
        if unit == "hours":
            hours, minutes, seconds = time.split(":")
            return from_ - timedelta(
                hours=int(hours), minutes=int(minutes), seconds=int(seconds)
            )

    @staticmethod
    def _extract_time(raw_timestamp: str) -> datetime:
        """Parse a unix timestamp to a UTC Python datetime"""
        try:
            return datetime.utcfromtimestamp(int(raw_timestamp))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Time {raw_timestamp} is not a valid integer") from e

    @ttl_cache(ttl=60 * 60)
    def get_profanities(self):
        return super().get_profanities()

    @ttl_cache(ttl=60 * 60)
    def get_autobalance_enabled(self):
        return super().get_autobalance_enabled() == "on"

    @ttl_cache(ttl=60 * 60)
    def get_votekick_enabled(self):
        return super().get_votekick_enabled() == "on"

    @ttl_cache(ttl=60 * 60)
    def get_votekick_threshold(self):
        res = super().get_votekick_threshold()
        if isinstance(res, str):
            return res.strip()
        return res

    def set_autobalance_enabled(self, bool_):
        with invalidates(self.get_autobalance_enabled):
            return super().set_autobalance_enabled("on" if bool_ else "off")

    def set_votekick_enabled(self, bool_):
        with invalidates(self.get_votekick_enabled):
            return super().set_votekick_enabled("on" if bool_ else "off")

    def set_votekick_threshold(self, threshold_pairs):
        # Todo use proper data structure
        with invalidates(self.get_votekick_threshold):
            res = super().set_votekick_threshold(threshold_pairs)
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {res}")
            logger.error("Threshold res %s", res)
            if res.lower().startswith("error"):
                logger.error("Unable to set votekick threshold: %s", res)
                raise CommandFailedError(res)

    def do_reset_votekick_threshold(self):
        with invalidates(self.get_votekick_threshold):
            return super().do_reset_votekick_threshold()

    def set_profanities(self, profanities):
        current = self.get_profanities()
        with invalidates(self.get_profanities):
            removed = set(current) - set(profanities)
            added = set(profanities) - set(current)
            if removed:
                self.do_unban_profanities(list(removed))
            if added:
                self.do_ban_profanities(list(added))

        return profanities

    def do_unban_profanities(self, profanities):
        if not isinstance(profanities, list):
            profanities = [profanities]
        with invalidates(self.get_profanities):
            return super().do_unban_profanities(",".join(profanities))

    def do_ban_profanities(self, profanities):
        if not isinstance(profanities, list):
            profanities = [profanities]
        with invalidates(self.get_profanities):
            return super().do_ban_profanities(",".join(profanities))

    @mod_users_allowed
    def do_punish(self, player, reason):
        return super().do_punish(player, reason)

    @mod_users_allowed
    def do_switch_player_now(self, player):
        return super().do_switch_player_now(player)

    @mod_users_allowed
    def do_switch_player_on_death(self, player):
        return super().do_switch_player_on_death(player)

    @mod_users_allowed
    def do_kick(self, player, reason):
        with invalidates(Rcon.get_players):
            return super().do_kick(player, reason)

    @mod_users_allowed
    def do_temp_ban(
        self, player=None, steam_id_64=None, duration_hours=2, reason="", admin_name=""
    ):
        with invalidates(Rcon.get_players, Rcon.get_temp_bans):
            if player and re.match(r"\d+", player):
                info = self.get_player_info(player)
                steam_id_64 = info.get(STEAMID, None)
                return super().do_temp_ban(
                    None, steam_id_64, duration_hours, reason, admin_name
                )

            return super().do_temp_ban(
                player, steam_id_64, duration_hours, reason, admin_name
            )

    @mod_users_allowed
    def do_remove_temp_ban(self, ban_log):
        with invalidates(Rcon.get_temp_bans):
            return super().do_remove_temp_ban(ban_log)

    @mod_users_allowed
    def do_remove_perma_ban(self, ban_log):
        with invalidates(Rcon.get_perma_bans):
            return super().do_remove_perma_ban(ban_log)

    @mod_users_allowed
    def do_perma_ban(self, player=None, steam_id_64=None, reason="", admin_name=""):
        with invalidates(Rcon.get_players, Rcon.get_perma_bans):
            if player and re.match(r"\d+", player):
                info = self.get_player_info(player)
                steam_id_64 = info.get(STEAMID, None)
                return super().do_perma_ban(None, steam_id_64, reason, admin_name)

            return super().do_perma_ban(player, steam_id_64, reason, admin_name)

    @ttl_cache(60 * 5)
    def get_map_rotation(self):
        l = super().get_map_rotation()

        for map_ in l:
            if not self.map_regexp.match(map_):
                raise CommandFailedError("Server return wrong data")
        return l

    def do_add_map_to_rotation(
        self, map_name, after_map_name: str = None, after_map_name_number: int = None
    ):
        with invalidates(Rcon.get_map_rotation):
            if after_map_name is None:
                current = self.get_map_rotation()
                after_map_name = current[len(current) - 1]
                after_map_name_number = current.count(after_map_name)

            super().do_add_map_to_rotation(
                map_name, after_map_name, after_map_name_number
            )

    def do_remove_map_from_rotation(self, map_name, map_number: int = None):
        with invalidates(Rcon.get_map_rotation):
            super().do_remove_map_from_rotation(map_name, map_number)

    def do_remove_maps_from_rotation(self, maps):
        with invalidates(Rcon.get_map_rotation):
            for map_name in maps:
                super().do_remove_map_from_rotation(map_name)
            return "SUCCESS"

    def do_add_maps_to_rotation(self, maps):
        with invalidates(Rcon.get_map_rotation):
            existing = self.get_map_rotation()
            last = existing[len(existing) - 1]
            map_numbers = {last: existing.count(last)}
            for map_name in maps:
                super().do_add_map_to_rotation(map_name, last, map_numbers.get(last, 1))
                last = map_name
                map_numbers[last] = map_numbers.get(last, 0) + 1
            return "SUCCESS"

    def set_maprotation(self, rotation):
        if not rotation:
            raise CommandFailedError("Empty rotation")

        rotation = list(rotation)
        logger.info("Apply map rotation %s", rotation)

        with invalidates(Rcon.get_map_rotation):
            current = self.get_map_rotation()
            logger.info("Current rotation: %s", current)
            if rotation == current:
                logger.debug("Map rotation is the same, nothing to do")
                return current

            # we remove all but the first
            for map_ in current[1:]:
                map_without_number = map_.rsplit(" ")[0]
                logger.info("Removing from rotation: '%s'", map_without_number)
                super().do_remove_map_from_rotation(map_without_number)

            last = current[0]
            map_number = {last: 1}
            for map_ in rotation:
                logger.info("Adding to rotation: '%s'", map_)
                super().do_add_map_to_rotation(map_, last, map_number.get(last, 1))
                last = map_
                map_number[last] = map_number.get(last, 0) + 1

            # Now we can remove the first from the previous rotation
            super().do_remove_map_from_rotation(current[0], 1)

        return self.get_map_rotation()

    @staticmethod
    def parse_log_line(raw_line: str) -> StructuredLogLineType:
        """Parse a single raw RCON log event or raise a ValueError"""

        player: str | None = None
        player2: str | None = None
        steam_id_64_1: str | None = None
        steam_id_64_2: str | None = None
        weapon: str | None = None
        action: str | None = None
        content: str = raw_line
        sub_content: str | None = None

        if raw_line.startswith("KILL") or raw_line.startswith("TEAM KILL"):
            # KILL: Muctar(Axis/71234567891234567) -> Chris(Allies/71234567891234576) with GEWEHR 43
            # TEAM KILL: SonofJack(Allies/71234567891234567) -> Joseph Cannon(Allies/71234567891234576) with M1 GARAND
            action, content = raw_line.split(": ", 1)
            if match := re.match(Rcon.kill_teamkill_pattern, content):
                player, steam_id_64_1, player2, steam_id_64_2, weapon = match.groups()
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")
        elif raw_line.startswith("DISCONNECTED") or raw_line.startswith("CONNECTED"):
            action, name_and_steam_id = raw_line.split(" ", 1)
            if match := re.match(Rcon.connect_disconnect_pattern, name_and_steam_id):
                player, steam_id_64_1 = match.groups()
                content = name_and_steam_id
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")
        elif raw_line.startswith("CHAT"):
            # CHAT[Team][Azure(Allies/71234567891234567)]: supply truck bot hq for nodes
            # CHAT[Unit][dominguez1987(Axis/71234567891234567)]: back
            if match := Rcon.chat_regexp.match(raw_line):
                scope, player, side, steam_id_64_1, sub_content = match.groups()
                action = f"CHAT[{side}][{scope}]"
                content = f"{player}: {sub_content} ({steam_id_64_1})"
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

            action = f"ADMIN {type_}".strip()

            if "FOR TEAM KILLING" in raw_line:
                action = f"TK AUTO {type_}"

            # Reconstruct the log line without the newlines and tack on the trailing ] we lose
            content = f"{_action}: [{player}] {sub_content}"
            if content[-1] != "]":
                content += "]"
                sub_content += "]"
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
                player, steam_id_64_1, sub_content = match.groups()
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
                player, steam_id_64_1, message_content = match.groups()
                content = f"{player}({steam_id_64_1}): {message_content}"
                sub_content = message_content
            else:
                raise ValueError(f"Unable to parse line: {raw_line}")

        if action is None:
            raise ValueError(f"Unknown type line: '{raw_line}'")

        return {
            "action": action,
            "player": player,
            "steam_id_64_1": steam_id_64_1,
            "player2": player2,
            "steam_id_64_2": steam_id_64_2,
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
        raw_logs: str, filter_action=None, filter_player=None
    ) -> ParsedLogsType:
        """Parse a chunk of raw gameserver RCON logs"""
        synthetic_actions = LOG_ACTIONS
        now = datetime.now()
        parsed_log_lines: List[StructuredLogLineWithMetaData] = []
        actions: set[str] = set()
        players: set[str] = set()

        for raw_relative_time, raw_timestamp, raw_log_line in Rcon.split_raw_log_lines(
            raw_logs
        ):
            time = Rcon._extract_time(raw_timestamp)
            try:
                log_line = Rcon.parse_log_line(raw_log_line)
                parsed_log_lines.append(
                    {
                        "version": 1,
                        "timestamp_ms": int(time.timestamp() * 1000),
                        "relative_time_ms": (time - now).total_seconds() * 1000,
                        "raw": raw_relative_time + " " + raw_log_line,
                        "line_without_time": raw_log_line,
                        "action": log_line["action"],
                        "player": log_line["player"],
                        "steam_id_64_1": log_line["steam_id_64_1"],
                        "player2": log_line["player2"],
                        "steam_id_64_2": log_line["steam_id_64_2"],
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

            if filter_action and not log_line["action"].startswith(filter_action):
                continue

            if filter_player and filter_player not in raw_log_line:
                continue

            if player := log_line["player"]:
                players.add(player)

            if player2 := log_line["player2"]:
                players.add(player2)

            actions.add(log_line["action"])

        parsed_log_lines.reverse()

        return {
            "actions": list(actions | set(synthetic_actions)),
            "players": list(players),
            "logs": parsed_log_lines,
        }

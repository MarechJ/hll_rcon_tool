import logging
import os
import re
from concurrent.futures import as_completed
from datetime import datetime, timedelta
from functools import update_wrapper
from time import sleep
from typing import Dict, List, Optional, Tuple, Union

from rcon.cache_utils import get_redis_client, invalidates, ttl_cache
from rcon.commands import CommandFailedError, HLLServerError, ServerCtl
from rcon.models import PlayerVIP, enter_session
from rcon.player_history import get_profiles
from rcon.steam_utils import (
    get_player_country_code,
    get_player_has_bans,
    get_players_country_code,
    get_players_have_bans,
)
from rcon.types import GameState, GetPlayersType, StructuredLogLine
from rcon.utils import get_server_number

STEAMID = "steam_id_64"
NAME = "name"
ROLE = "role"
# ["CHAT[Allies]", "CHAT[Axis]", "CHAT", "VOTE STARTED", "VOTE COMPLETED"]
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
    slots_regexp = re.compile(r"^\d{1,3}/\d{2,3}$")
    map_regexp = re.compile(r"^(\w+_?)+$")
    chat_regexp = re.compile(
        r"CHAT\[((Team)|(Unit))\]\[(.*)\(((Allies)|(Axis))/(\d+)\)\]: (.*)"
    )
    player_info_pattern = r"(.*)\(((Allies)|(Axis))/(\d+)\)"
    player_info_regexp = re.compile(r"(.*)\(((Allies)|(Axis))/(\d+)\)")
    MAX_SERV_NAME_LEN = 1024  # I totally made up that number. Unable to test
    log_time_regexp = re.compile(r".*\((\d+)\).*")

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
    @ttl_cache(ttl=60, cache_falsy=False)
    def get_team_view(self):
        teams = {}
        players_by_id = {}
        for player in super().get_players():
            try:
                info = self.get_detailed_player_info(player)
                print(info)
            except (HLLServerError, CommandFailedError):
                logger.exception("Unable to get %s info", player)
                try:
                    steam_id_64 = self.get_playerids(as_dict=True).get(player)
                    info = self._get_default_info_dict(player)
                    info[STEAMID] = steam_id_64
                except Exception:
                    logger.exception(
                        "Unable to get %s info with playerids either", player
                    )
                    continue

            players_by_id[info.get(STEAMID)] = info

        logger.debug("Getting DB profiles")
        steam_profiles = {
            profile[STEAMID]: profile
            for profile in get_profiles(list(players_by_id.keys()))
        }
        logger.debug("Getting VIP list")
        try:
            vips = set(v[STEAMID] for v in self.get_vip_ids())
        except Exception:
            logger.exception("Failed to get VIPs")
            vips = set()

        for player in players_by_id.values():
            steam_id_64 = player[STEAMID]
            profile = steam_profiles.get(player.get("steam_id_64"), {}) or {}
            player["profile"] = profile
            player["is_vip"] = steam_id_64 in vips
            steaminfo = profile.get("steaminfo", {}) or {}
            player["country"] = steaminfo.get("country", "private")
            # TODO refresh ban info and store into DB to avoid IOs here
            player["steam_bans"] = get_player_has_bans(steam_id_64)
            teams.setdefault(player.get("team"), {}).setdefault(
                player.get("unit_name"), {}
            ).setdefault("players", []).append(player)

        for team, squads in teams.items():
            if team is None:
                continue
            for squad_name, squad in squads.items():
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
                    logger.exception()

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

        return game

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

    def _get_default_info_dict(self, player):
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
    def get_detailed_player_info(self, player):
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
        res = super().get_vip_ids()
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
            try:
                steam_id_64, name = item.split(" ", 1)
                name = name.replace('"', "")
                name = name.replace("\n", "")
                name = name.strip()
            except ValueError:
                self._reconnect()
                raise
            player = dict(zip((STEAMID, NAME), (steam_id_64, name)))
            player["vip_expiration"] = vip_expirations.get(steam_id_64, None)
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
                self._reconnect()
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
                self.do_add_map_to_rotation(map_name)
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
    def _extract_time(time_str):
        groups = Rcon.log_time_regexp.match(time_str)
        if not groups:
            raise ValueError("Unable to extract time from '%s'", time_str)
        try:
            return datetime.fromtimestamp(int(groups.group(1)))
        except (ValueError, TypeError) as e:
            raise ValueError("Time '%s' is not a valid integer", time_str) from e

    @mod_users_allowed
    @ttl_cache(ttl=2)
    def get_structured_logs(
        self, since_min_ago, filter_action=None, filter_player=None
    ):
        raw = super().get_logs(since_min_ago)
        return self.parse_logs(raw, filter_action, filter_player)

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
        self, map_name, after_map_name: str = None, after_map_name_number: str = None
    ):
        with invalidates(Rcon.get_map_rotation):
            super().do_add_map_to_rotation(
                map_name, after_map_name, after_map_name_number
            )

    def do_remove_map_from_rotation(self, map_name, map_number: str = None):
        with invalidates(Rcon.get_map_rotation):
            super().do_remove_map_from_rotation(map_name, map_number)

    def do_remove_maps_from_rotation(self, maps):
        with invalidates(Rcon.get_map_rotation):
            for map_name in maps:
                super().do_remove_map_from_rotation(map_name)
            return "SUCCESS"

    def do_add_maps_to_rotation(self, maps):
        with invalidates(Rcon.get_map_rotation):
            for map_name in maps:
                super().do_add_map_to_rotation(map_name)
            return "SUCCESS"

    def set_maprotation(self, rotation):
        if not rotation:
            raise CommandFailedError("Empty rotation")

        rotation = list(rotation)
        logger.info("Apply map rotation %s", rotation)

        current = self.get_map_rotation()
        logger.info("Current rotation: %s", current)
        if rotation == current:
            logger.debug("Map rotation is the same, nothing to do")
            return current
        with invalidates(Rcon.get_map_rotation):
            # we remove all but the first
            for map_ in current[1:]:
                map_without_number = map_.rsplit(" ")[0]
                logger.info("Removing from rotation: '%s'", map_without_number)
                super().do_remove_map_from_rotation(map_without_number)

            for map_ in rotation:
                logger.info("Adding to rotation: '%s'", map_)
                super().do_add_map_to_rotation(map_)

            # Now we can remove the first from the previous rotation
            super().do_remove_map_from_rotation(current[0])

        return self.get_map_rotation()

    @mod_users_allowed
    @ttl_cache(ttl=60 * 2)
    def get_scoreboard(self, minutes=180, sort="ratio"):
        logs = self.get_structured_logs(minutes, "KILL")
        scoreboard = []
        for player in logs["players"]:
            if not player:
                continue
            kills = 0
            death = 0
            for log in logs["logs"]:
                if log["player"] == player:
                    kills += 1
                elif log["player2"] == player:
                    death += 1
            if kills == 0 and death == 0:
                continue
            scoreboard.append(
                {
                    "player": player,
                    "(real) kills": kills,
                    "(real) death": death,
                    "ratio": kills / max(death, 1),
                }
            )

        scoreboard = sorted(scoreboard, key=lambda o: o[sort], reverse=True)
        for o in scoreboard:
            o["ratio"] = "%.2f" % o["ratio"]

        return scoreboard

    @mod_users_allowed
    @ttl_cache(ttl=60 * 2)
    def get_teamkills_boards(self, sort="TK Minutes"):
        logs = self.get_structured_logs(180)
        scoreboard = []
        for player in logs["players"]:
            if not player:
                continue
            first_timestamp = float("inf")
            last_timestamp = 0
            tk = 0
            death_by_tk = 0
            for log in logs["logs"]:
                if log["player"] == player or log["player2"] == player:
                    first_timestamp = min(log["timestamp_ms"], first_timestamp)
                    last_timestamp = max(log["timestamp_ms"], last_timestamp)
                if log["action"] == "TEAM KILL":
                    if log["player"] == player:
                        tk += 1
                    elif log["player2"] == player:
                        death_by_tk += 1
            if tk == 0 and death_by_tk == 0:
                continue
            scoreboard.append(
                {
                    "player": player,
                    "Teamkills": tk,
                    "Death by TK": death_by_tk,
                    "Estimated play time (minutes)": (last_timestamp - first_timestamp)
                    // 1000
                    // 60,
                    "TK Minutes": tk
                    / max((last_timestamp - first_timestamp) // 1000 // 60, 1),
                }
            )

        scoreboard = sorted(scoreboard, key=lambda o: o[sort], reverse=True)
        for o in scoreboard:
            o["TK Minutes"] = "%.2f" % o["TK Minutes"]

        return scoreboard

    @staticmethod
    def parse_logs(raw, filter_action=None, filter_player=None):
        synthetic_actions = LOG_ACTIONS
        now = datetime.now()
        res: List[StructuredLogLine] = []
        actions = set()
        players = set()

        for line in raw.split("\n"):
            if not line:
                continue
            try:
                time, rest = line.split("] ", 1)
                # time = self._convert_relative_time(now, time[1:])
                time = Rcon._extract_time(time[1:])
                sub_content = (
                    action
                ) = player = player2 = weapon = steam_id_64_1 = steam_id_64_2 = None
                content = rest
                if rest.startswith("DISCONNECTED") or rest.startswith("CONNECTED"):
                    action, content = rest.split(" ", 1)
                elif rest.startswith("KILL") or rest.startswith("TEAM KILL"):
                    action, content = rest.split(": ", 1)
                elif rest.startswith("CHAT"):
                    match = Rcon.chat_regexp.match(rest)
                    groups = match.groups()
                    scope = groups[0]
                    side = groups[4]
                    player = groups[3]
                    steam_id_64_1 = groups[-2]
                    action = f"CHAT[{side}][{scope}]"
                    sub_content = groups[-1]
                    # import ipdb; ipdb.set_trace()
                    content = f"{player}: {sub_content} ({steam_id_64_1})"
                elif rest.startswith("VOTESYS"):
                    # [15:49 min (1606998428)] VOTE Player [[fr]ELsass_blitz] Started a vote of type (PVR_Kick_Abuse) against [拢儿]. VoteID: [1]
                    action = "VOTE"
                    if (
                        rest.startswith("VOTESYS Player")
                        and " against " in rest.lower()
                    ):
                        action = "VOTE STARTED"
                        groups = re.match(
                            r"VOTESYS Player \[(.*)\].* against \[(.*)\]\. VoteID: \[\d+\]",
                            rest,
                        )
                        player = groups[1]
                        player2 = groups[2]
                    elif rest.startswith("VOTESYS Player") and "voted" in rest.lower():
                        groups = re.match(r"VOTESYS Player \[(.*)\] voted.*", rest)
                        player = groups[1]
                    elif "completed" in rest.lower():
                        action = "VOTE COMPLETED"
                    elif "kick" in rest.lower():
                        action = "VOTE COMPLETED"
                        groups = re.match(r"VOTESYS Vote Kick \{(.*)\}.*", rest)
                        player = groups[1]
                    else:
                        player = ""
                        player2 = None
                    sub_content = rest.split("VOTE")[-1]
                    content = rest.split("VOTE")[-1]
                elif rest.upper().startswith("PLAYER"):
                    action = "CAMERA"
                    _, content = rest.split(" ", 1)
                    matches = re.match(r"\[(.*)\s{1}\((\d+)\)\]", content)
                    if matches and len(matches.groups()) == 2:
                        player, steam_id_64_1 = matches.groups()
                        _, sub_content = content.rsplit("]", 1)
                    else:
                        logger.error("Unable to parse line: %s", line)
                elif rest.upper().startswith("TEAMSWITCH"):
                    action = "TEAMSWITCH"
                    matches = re.match(r"TEAMSWITCH\s(.*)\s\(((.*)\s>\s(.*))\)", rest)
                    if matches and len(matches.groups()) == 4:
                        player, sub_content, *_ = matches.groups()
                    else:
                        logger.error("Unable to parse line: %s", line)
                elif rest.startswith("KICK") or rest.startswith("BAN"):
                    if "FOR TEAM KILLING" in rest:
                        action = "TK AUTO"
                    else:
                        action = "ADMIN"
                    matches = re.match(
                        r"(.*):\s\[(.*)\]\s(.*\[(KICKED|BANNED|PERMANENTLY|YOU)\s.*)",
                        rest,
                    )
                    if matches and len(matches.groups()) == 4:
                        _, player, sub_content, type_ = matches.groups()
                        if type_ == "PERMANENTLY":
                            type_ = "PERMA BANNED"
                        if type_ == "YOU":
                            type_ = "IDLE"
                        action = f"{action} {type_}"
                    else:
                        logger.error("Unable to parse line: %s", line)
                elif rest.upper().startswith("MATCH START"):
                    action = "MATCH START"
                    _, sub_content = rest.split("MATCH START ")
                elif rest.upper().startswith("MATCH ENDED"):
                    action = "MATCH ENDED"
                    _, sub_content = rest.split("MATCH ENDED ")
                elif rest.upper().startswith("MESSAGE"):

                    action = "MESSAGE"
                    groups = re.match(
                        r"MESSAGE: player \[(.+)\((\d+)\)\], content \[(.+)\]", rest
                    ).groups()
                    player, steam_id_64_1, content = groups
                    content = f"{player}({steam_id_64_1}): {content}"

                else:
                    logger.error("Unkown type line: '%s'", line)
                    continue
                if action in {"CONNECTED", "DISCONNECTED"}:
                    # player = content
                    try:
                        groups = re.match(r"(.+) \((\d+)\)", content).groups()
                        player, steam_id_64 = groups
                        steam_id_64_1 = steam_id_64
                    except AttributeError:
                        # Handle U12 format for the U13 release
                        # TODO: remove release after U13 is out
                        player = content

                if action in {"KILL", "TEAM KILL"}:
                    parts = re.split(Rcon.player_info_pattern + r" -> ", content, 1)
                    player = parts[1]
                    steam_id_64_1 = parts[-2]
                    player2 = parts[-1]
                    player2, weapon = player2.rsplit(" with ", 1)
                    player2, *_, steam_id_64_2 = Rcon.player_info_regexp.match(
                        player2
                    ).groups()

                players.add(player)
                players.add(player2)
                actions.add(action)
            except:
                # logger.exception("Invalid line: '%s'", line)
                continue
            if filter_action and not action.startswith(filter_action):
                continue
            if filter_player and filter_player not in line:
                continue

            res.append(
                {
                    "version": 1,
                    "timestamp_ms": int(time.timestamp() * 1000),
                    "relative_time_ms": (time - now).total_seconds() * 1000,
                    "raw": line,
                    "line_without_time": rest,
                    "action": action,
                    "player": player,
                    "steam_id_64_1": steam_id_64_1,
                    "player2": player2,
                    "steam_id_64_2": steam_id_64_2,
                    "weapon": weapon,
                    "message": content,
                    "sub_content": sub_content,
                }
            )

        res.reverse()
        return {
            "actions": list(actions) + synthetic_actions,
            "players": list(players),
            "logs": res,
        }

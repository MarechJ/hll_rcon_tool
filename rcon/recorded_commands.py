from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import cached_property
from logging import getLogger
from typing import List, Union

from dateutil import parser, relativedelta

from rcon.cache_utils import ttl_cache
from rcon.config import get_config
from rcon.extended_commands import NAME, STEAMID, Rcon, mod_users_allowed
from rcon.models import AdvancedConfigOptions, PlayerSteamID, PlayerVIP, enter_session
from rcon.player_history import (
    add_player_to_blacklist,
    get_profiles,
    safe_save_player_action,
)
from rcon.types import EnrichedGetPlayersType
from rcon.utils import get_server_number

logger = getLogger(__name__)


class RecordedRcon(Rcon):
    """
    Note beware of using the cache in this layer
    """

    def __init__(self, *args, pool_size=None, **kwargs):
        super().__init__(*args, **kwargs)

        # config/default_config.yml config.yml, etc.
        config = get_config()
        try:
            self.advanced_settings = AdvancedConfigOptions(
                **config["ADVANCED_CRCON_SETTINGS"]
            )
        except ValueError:
            # This might look dumb but pydantic provides useful error messages in the
            # stack trace and we don't have to remember to keep updating this if we add
            # any more fields to the ADVANCED_CRCON_SETTINGS config
            logger.exception()

        if pool_size is not None:
            self.pool_size = pool_size
        else:
            self.pool_size = self.advanced_settings.thread_pool_size

    @cached_property
    def thread_pool(self):
        return ThreadPoolExecutor(self.pool_size)

    @cached_property
    def connection_pool(self):
        logger.info("Initializing Rcon connection pool of size %s", self.pool_size)
        pool = [RecordedRcon(self.config) for _ in range(self.pool_size)]
        for idx, rcon in enumerate(pool):
            logger.debug("Connecting rcon %s/%s", idx + 1, self.pool_size)
            rcon._connect()
        logger.info("Done initialzing Rcon connection pool")
        return pool

    def run_in_pool(self, process_number: int, function_name: str, *args, **kwargs):
        return self.thread_pool.submit(
            getattr(
                self.connection_pool[process_number % self.pool_size], function_name
            ),
            *args,
            **kwargs,
        )

    @mod_users_allowed
    @ttl_cache(ttl=2, cache_falsy=False)
    def get_team_view_fast(self):
        teams = {}
        players_by_id = {}
        players = self.get_players_fast()
        fail_count = 0

        futures = {
            self.run_in_pool(idx, "get_detailed_player_info", player[NAME]): player
            for idx, player in enumerate(players)
        }
        for future in as_completed(futures):
            try:
                player_data = future.result()
            except Exception:
                logger.exception("Failed to get info for %s", futures[future])
                fail_count += 1
                player_data = self._get_default_info_dict(futures[future][NAME])
            player = futures[future]
            player.update(player_data)
            players_by_id[player[STEAMID]] = player

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

        return dict(fail_count=fail_count, **game)

    def do_punish(self, player, reason, by):
        res = super().do_punish(player, reason)
        safe_save_player_action(
            rcon=self, player_name=player, action_type="PUNISH", reason=reason, by=by
        )
        return res

    def do_kick(self, player, reason, by):
        res = super().do_kick(player, reason)
        safe_save_player_action(
            rcon=self, player_name=player, action_type="KICK", reason=reason, by=by
        )
        return res

    def do_temp_ban(
        self, player=None, steam_id_64=None, duration_hours=2, reason="", by=""
    ):
        res = super().do_temp_ban(
            player, steam_id_64, duration_hours, reason, admin_name=by
        )
        safe_save_player_action(
            rcon=self,
            player_name=player,
            action_type="TEMPBAN",
            reason=reason,
            by=by,
            steam_id_64=steam_id_64,
        )
        return res

    def do_perma_ban(self, player=None, steam_id_64=None, reason="", by=""):
        res = super().do_perma_ban(player, steam_id_64, reason, admin_name=by)
        safe_save_player_action(
            rcon=self,
            player_name=player,
            action_type="PERMABAN",
            reason=reason,
            by=by,
            steam_id_64=steam_id_64,
        )
        try:
            if not steam_id_64:
                info = self.get_player_info(player)
                steam_id_64 = info["steam_id_64"]
            # TODO add author
            add_player_to_blacklist(steam_id_64, reason, by=by)
        except:
            logger.exception("Unable to blacklist")
        return res

    def do_switch_player_on_death(self, player, by):
        res = super().do_switch_player_on_death(player)
        return res

    def do_switch_player_now(self, player, by):
        res = super().do_switch_player_now(player)
        return res

    def invalidate_player_list_cache(self):
        super().get_players.cache_clear()

    def get_players(self) -> List[EnrichedGetPlayersType]:
        players = super().get_players()

        vips = set(v["steam_id_64"] for v in super().get_vip_ids())
        steam_ids = [p.get(STEAMID) for p in players if p.get(STEAMID)]
        profiles = {p["steam_id_64"]: p for p in get_profiles(steam_ids)}

        for p in players:
            p.update(
                {
                    "profile": profiles.get(p.get(STEAMID)),
                    "is_vip": p.get(STEAMID) in vips,
                }
            )

        return players

    def do_message_player(
        self, player_name=None, steam_id_64=None, message="", by="", save_message=False
    ):
        res = super().do_message_player(player_name, steam_id_64, message)
        if save_message:
            safe_save_player_action(
                rcon=self,
                player_name=player_name,
                action_type="MESSAGE",
                reason=message,
                by=by,
                steam_id_64=steam_id_64,
            )
        return res

    def do_remove_vip(self, steam_id_64):
        """Removes VIP status on the game server and removes their PlayerVIP record."""

        # Remove VIP before anything else in case we have errors
        result = super().do_remove_vip(steam_id_64)

        server_number = get_server_number()
        with enter_session() as session:
            player: PlayerSteamID = (
                session.query(PlayerSteamID)
                .filter(PlayerSteamID.steam_id_64 == steam_id_64)
                .one_or_none()
            )
            if player and player.vip:
                logger.info(
                    f"Removed VIP from {steam_id_64} expired: {player.vip.expiration}"
                )
                # TODO: This is an incredibly dumb fix because I can't get
                # the changes to persist otherwise
                vip_record: PlayerVIP = (
                    session.query(PlayerVIP)
                    .filter(
                        PlayerVIP.playersteamid_id == player.id,
                        PlayerVIP.server_number == server_number,
                    )
                    .one_or_none()
                )
                session.delete(vip_record)
            elif player and not player.vip:
                logger.warning(f"{steam_id_64} has no PlayerVIP record")
            else:
                # This is okay since you can give VIP to someone who has never been on a game server
                # or that your instance of CRCON hasn't seen before, but you might want to prune these
                logger.warning(f"{steam_id_64} has no PlayerSteamID record")

        return result

    def do_add_vip(self, name, steam_id_64, expiration: str = ""):
        """Adds VIP status on the game server and adds or updates their PlayerVIP record."""

        # Add VIP before anything else in case we have errors
        result = super().do_add_vip(name, steam_id_64)

        # postgres and Python have different max date limits
        # https://docs.python.org/3.8/library/datetime.html#datetime.MAXYEAR
        # https://www.postgresql.org/docs/12/datatype-datetime.html

        server_number = get_server_number()
        # If we're unable to parse the date, treat them as indefinite VIPs
        expiration_date: Union[str, datetime]
        try:
            expiration_date = parser.parse(expiration)
        except (parser.ParserError, OverflowError):
            logger.warning(f"Unable to parse {expiration=} for {name=} {steam_id_64=}")
            # For our purposes (human lifespans) we can use 200 years in the future as
            # the equivalent of indefinite VIP access
            expiration_date = datetime.utcnow() + relativedelta.relativedelta(years=200)

        # Find a player and update their expiration date if it exists or create a new record if not
        with enter_session() as session:
            player: PlayerSteamID = (
                session.query(PlayerSteamID)
                .filter(PlayerSteamID.steam_id_64 == steam_id_64)
                .one_or_none()
            )

            # If there's no PlayerSteamID record the player has never been on the server before
            # Adding VIP to them is still valid as it's tracked on the game server
            # The service that prunes expired VIPs checks for VIPs without a PlayerVIP record
            # and creates them there as indefinite VIPs
            if player:
                vip_record: PlayerVIP = (
                    session.query(PlayerVIP)
                    .filter(
                        PlayerVIP.server_number == server_number,
                        PlayerVIP.playersteamid_id == player.id,
                    )
                    .one_or_none()
                )
                new_vip_record = PlayerVIP(
                    expiration=expiration_date,
                    playersteamid_id=player.id,
                    server_number=server_number,
                )
                if not vip_record:
                    logger.info(
                        f"Added new PlayerVIP record {player.steam_id_64=} {expiration_date=}"
                    )
                    # TODO: This is an incredibly dumb fix because I can't get
                    # the changes to persist otherwise
                    session.add(new_vip_record)
                else:
                    previous_expiration = vip_record.expiration.isoformat()

                    # TODO: This is an incredibly dumb fix because I can't get
                    # the changes to persist otherwise
                    session.delete(vip_record)
                    session.commit()
                    session.add(new_vip_record)
                    logger.info(
                        f"Modified PlayerVIP record {player.steam_id_64=} {player.vip.expiration=} {previous_expiration=}"
                    )

        return result

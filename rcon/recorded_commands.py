from datetime import datetime
from logging import getLogger
from typing import Union
import os

from dateutil import parser, relativedelta
from sqlalchemy.orm.attributes import flag_dirty

from rcon.cache_utils import ttl_cache
from rcon.commands import ServerCtl
from rcon.extended_commands import NAME, STEAMID, Rcon, invalidates
from rcon.models import PlayerSteamID, PlayerVIP, enter_session
from rcon.player_history import (
    add_player_to_blacklist,
    get_profiles,
    safe_save_player_action,
)
from rcon.utils import get_server_number


logger = getLogger(__name__)


class RecordedRcon(Rcon):
    """
    Note beware of using the cache in this layer
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def get_players(self):
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
                logger.info(f"Removed VIP from {steam_id_64} {player.vip.expiration}")
                logger.info(f"player.vip={player.vip}")
                session.delete(player.vip)
            elif player and not player.vip:
                logger.error(f"player= {player} player.vip={player.vip}")
                logger.warning(f"{steam_id_64} has no PlayerVIP record")
            else:
                # This is okay since you can give VIP to someone who has never been on a game server
                # or that your instance of CRCON hasn't seen before
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
                if not player.vip:
                    vip_record = PlayerVIP(
                        expiration=expiration_date,
                        playersteamid_id=player.id,
                        server_number=server_number,
                    )
                    logger.info(
                        f"Added new PlayerVIP record {player.steam_id_64=} {expiration_date=}"
                    )
                    session.add(vip_record)
                else:
                    vip_record = player.vip

                    previous_expiration = vip_record.expiration.isoformat()
                    vip_record.playersteamid_id = player.id
                    vip_record.expiration_date = expiration_date
                    logger.info(f"dirty={session.dirty}")
                    flag_dirty(vip_record)
                    session.add(vip_record)
                    logger.info(f"dirty={session.dirty}")
                    session.flush()
                    logger.info(f"dirty={session.dirty}")
                    logger.info(
                        f"player.vip={player.vip} id={player.vip.id} exp={player.vip.expiration} server_num={player.vip.server_number}"
                    )
                    logger.info(
                        f"Modified PlayerVIP record {player.steam_id_64=} {player.vip.expiration_date=} {previous_expiration=}"
                    )

        return result

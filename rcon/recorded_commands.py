from logging import getLogger

from rcon.cache_utils import ttl_cache
from rcon.commands import ServerCtl
from rcon.extended_commands import NAME, STEAMID, Rcon, invalidates
from rcon.player_history import (
    add_player_to_blacklist,
    get_profiles,
    safe_save_player_action,
)

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

from logging import getLogger

from rcon.player_history import safe_save_player_action, add_player_to_blacklist, get_profiles
from rcon.extended_commands import Rcon, STEAMID, NAME, invalidates
from rcon.cache_utils import ttl_cache
from rcon.commands import ServerCtl

logger = getLogger(__name__)


class RecordedRcon(Rcon):
    """
    Note beware of using the cache in this layer
    """

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

    def do_temp_ban(self, player, reason, by):
        res = super().do_temp_ban(player, reason)
        safe_save_player_action(
            rcon=self, player_name=player, action_type="TEMPBAN", reason=reason, by=by)
        return res

    def do_perma_ban(self, player, reason, by):
        res = super().do_perma_ban(player, reason)
        safe_save_player_action(
            rcon=self, player_name=player, action_type="PERMABAN", reason=reason, by=by
        )
        try:
            info = self.get_player_info(player)
            add_player_to_blacklist(info['steam_id_64'], reason)
        except:
            logger.exception("Unable to blacklist")
        return res

    def do_switch_player_on_death(self, player, by):
        res = super().do_switch_player_on_death(player)
        return res

    def do_switch_player_now(self, player, by):
        res = super().do_switch_player_now(player)
        return res

    def get_players(self):
        players = super().get_players()

        steam_ids = [p.get(STEAMID) for p in players if p.get(STEAMID)]
        profiles = {p['steam_id_64']: p for p in get_profiles(steam_ids)}

        for p in players:
            p.update(
                {'profile': profiles.get(p.get(STEAMID))}
            )

        return players

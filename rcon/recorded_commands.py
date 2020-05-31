from logging import getLogger

from rcon.player_history import safe_save_player_action, add_player_to_blacklist, get_player_profile
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
        with invalidates(self._get_profile):
            safe_save_player_action(
                rcon=self, player_name=player, action_type="PUNISH", reason=reason, by=by
            )
        return res

    def do_kick(self, player, reason, by):
        res = super().do_kick(player, reason)
        with invalidates(self._get_profile):
            safe_save_player_action(
                rcon=self, player_name=player, action_type="KICK", reason=reason, by=by
            )
        return res

    def do_temp_ban(self, player, reason, by):
        res = super().do_temp_ban(player, reason)
        with invalidates(self._get_profile):
            safe_save_player_action(
                rcon=self, player_name=player, action_type="TEMPBAN", reason=reason, by=by)
        return res

    def do_perma_ban(self, player, reason, by):
        res = super().do_perma_ban(player, reason)
        with invalidates(self._get_profile):
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

    @ttl_cache(ttl=60 * 60 * 24)
    def _get_profile(self, steam_id_64):
        return get_player_profile(steam_id_64, 0)

    def get_player_info(self, player):
        res = super().get_player_info(player)
        if not res:
            return res
        res.update(
            {'profile': self._get_profile(res[STEAMID]) or {}}
        )
        return res

    @ttl_cache(ttl=5)
    def get_players(self):
        """ 
        Duplicate the code here to make sure we don't hit the wrong cache
        We might want to rethink the hierachy or where the caching is happening
        """
        names = ServerCtl.get_players(self)
        players = []
        for n in names:
            player = {NAME: n}
            player.update(self.get_player_info(n))
            players.append(player)

        return players    

 
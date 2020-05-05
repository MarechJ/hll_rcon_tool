from logging import getLogger

from rcon.player_history import safe_save_player_action, add_player_to_blacklist
from rcon.extended_commands import Rcon

logger = getLogger(__name__)

class RecordedRcon(Rcon):
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
        safe_save_player_action(
            rcon=self, player_name=player, action_type="SWITCHTEAMONDEATH", reason='', by=by
        )
        return res

    def do_switch_player_now(self, player, by):
        res = super().do_switch_player_now(player)
        safe_save_player_action(
            rcon=self, player_name=player, action_type="SWITCHTEAMNOW", reason='', by=by
        )
        return res
import logging
import re

from rcon.game_logs import on_connected
from rcon.hooks import inject_player_ids
from rcon.player_history import get_player_profile, player_has_flag
from rcon.rcon_ import Rcon
from rcon.rcon_discord import send_to_discord_audit
from rcon.settings import SERVER_INFO
from rcon.user_config.name_kicks import NameKickUserConfig

logger = logging.getLogger(__name__)


recorded_rcon = Rcon(SERVER_INFO)


@on_connected
@inject_player_ids
def auto_kick(_, log, name, steam_id_64):
    config = NameKickUserConfig.load_from_db()

    for r in config.regular_expressions:
        try:
            profile = get_player_profile(steam_id_64, 0)
            for f in config.whitelist_flags:
                if player_has_flag(profile, f):
                    logger.debug(
                        "Not checking nickname validity for whitelisted player %s (%s)",
                        name,
                        steam_id_64,
                    )
                    return
        except:
            logger.exception("Unable to check player profile")

        if re.match(r, name):
            logger.info("%s matched player %s", r, name)
            recorded_rcon.do_kick(
                player=name, reason=config.kick_reason, by="NAME_KICK"
            )
            try:
                send_to_discord_audit(
                    f"`{name}` kicked from regexp `{r}`",
                    by="NAME_KICK",
                    webhookurls=[config.discord_webhook_url],
                )
            except Exception:
                logger.error("Unable to send to audit_log")
            return

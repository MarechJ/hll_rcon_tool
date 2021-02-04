import logging
import re

from rcon.player_history import get_player_profile
from rcon.recorded_commands import RecordedRcon
from rcon.discord import send_to_discord_audit
from rcon.config import get_config
from rcon.settings import SERVER_INFO
from rcon.game_logs import on_connected

logger = logging.getLogger(__name__)


recorded_rcon = RecordedRcon(SERVER_INFO)


@on_connected
def auto_kick(_, log):
    try:
        config = get_config().get('NAME_KICKS')
    except KeyError:
        logger.error("Invalid configuration file, NAME_KICKS key is missing")
        return

    for r in config['regexps']:
        name = log["player"]
        info = recorded_rcon.get_player_info(name)
        try:
            profile = get_player_profile(info["steam_id_64"], 0)
            flags = profile["flags"]

            if flags and set(config.get("whitelist_flags", [])) & set(f["flag"] in flags):
                logger.debug("Not checking nickname validity for whitelisted player %s (%s)", name, info["steam_id_64"])
                return
        except:
            logger.exception("Unable to check player profile")

        if re.match(r, name):
            logger.info("%s matched player %s", r, name)
            recorded_rcon.do_kick(player=name, reason=config["reason"], by="NAME_KICK")
            try:
                send_to_discord_audit(f"`{name}` kicked from regexp `{r}`", by="NAME_KICK", webhookurl=config.get("discord_webhook_url"))
            except Exception:
                logger.error("Unable to send to audit_log")
            return
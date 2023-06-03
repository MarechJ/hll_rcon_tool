import logging
import re

from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.game_logs import on_connected
from rcon.hooks import inject_player_ids
from rcon.player_history import get_player_profile, player_has_flag
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO

logger = logging.getLogger(__name__)


recorded_rcon = RecordedRcon(SERVER_INFO)


@on_connected
@inject_player_ids
def auto_kick(_, log, name, steam_id_64):
    try:
        config = get_config().get("NAME_KICKS")
    except KeyError:
        logger.error("Invalid configuration file, NAME_KICKS key is missing")
        return

    for r in config["regexps"]:
        try:
            profile = get_player_profile(steam_id_64, 0)
            for f in config.get("whitelist_flags", []):
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
            recorded_rcon.do_kick(player=name, reason=config["reason"], by="NAME_KICK")
            try:
                send_to_discord_audit(
                    f"`{name}` kicked from regexp `{r}`",
                    by="NAME_KICK",
                    webhookurl=config.get("discord_webhook_url"),
                )
            except Exception:
                logger.error("Unable to send to audit_log")
            return
        
@on_connected
@inject_player_ids
def auto_kick_by_level(_, log, name, steam_id_64):
    logger.info("Entering auto_kick_by_level hook")
    try:
        config = get_config().get("LEVEL_KICKS")
    except KeyError:
        logger.warning("Invalid configuration file, LEVEL_KICKS key is missing")
        return

    minLevel = config["min_level"]
    playerLevel = 0
    try:
        player = recorded_rcon.get_detailed_player_info(name)
        playerLevel = player.get('level')
        
        profile = get_player_profile(steam_id_64, 0)
        for f in config.get("whitelist_flags", []):
            if player_has_flag(profile, f):
                logger.debug(
                    "Not checking player level validity for whitelisted player %s (%s)",
                    name,
                    steam_id_64,
                )
                return
    except:
        logger.exception("Unable to check player profile")

    if playerLevel < minLevel:
        logger.info("player %s of level %i under level %i", name, playerLevel, minLevel)
        recorded_rcon.do_kick(player=name, reason=config["reason"], by="LEVEL_KICK")
        try:
            send_to_discord_audit(
                f"`{name}` kicked from minimum level `{minLevel}`",
                by="LEVEL_KICK",
                webhookurl=config.get("discord_webhook_url"),
            )
        except Exception:
            logger.error("Unable to send to audit_log")
        return

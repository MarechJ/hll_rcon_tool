import logging
import time
from typing import List

from rcon.cache_utils import get_redis_client
from rcon.commands import CommandFailedError, HLLServerError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.squad_automod.models import (
    PunishPlayer,
    NoLeaderConfig,
    PunitionsToApply,
    ActionMethod,
)
from rcon.squad_automod.no_leader import NoLeaderAutomod

LEADER_WATCH_RESET_SECS = 120
AUTOMOD_USERNAME = "NoLeaderWatch"

logger = logging.getLogger(__name__)


def get_punitions_to_apply(rcon, moderators) -> PunitionsToApply:
    logger.debug("Getting team info")
    team_view = rcon.get_team_view_fast()
    punitions_to_apply = PunitionsToApply()

    for team in ["allies", "axis"]:
        if not team_view.get(team):
            continue

        for squad_name, squad in team_view[team]["squads"].items():
            for mod in moderators:
                punitions_to_apply.merge(mod.punitions_to_apply(team_view, squad_name, team, squad))

    return punitions_to_apply


def _do_punitions(
        rcon: RecordedRcon,
        method: ActionMethod,
        players: List[PunishPlayer],
        mods,
):
    for aplayer in players:
        try:
            if method == ActionMethod.MESSAGE:
                if not aplayer.details.dry_run:
                    rcon.do_message_player(
                        aplayer.name, aplayer.steam_id_64, aplayer.details.message, by=aplayer.details.author
                    )
                audit(aplayer.details.discord_audit_url, f"-> WARNING: {aplayer}", aplayer.details.author)

            if method == ActionMethod.PUNISH:
                if not aplayer.details.dry_run:
                    rcon.do_punish(aplayer.name, aplayer.details.message, by=aplayer.details.author)
                audit(aplayer.details.discord_audit_url, f"--> PUNISHING: {aplayer}", aplayer.details.author)

            if method == ActionMethod.KICK:
                if not aplayer.details.dry_run:
                    rcon.do_kick(aplayer.name, aplayer.details.message, by=aplayer.details.author)
                audit(aplayer.details.discord_audit_url, f"---> KICKING <---: {aplayer}", aplayer.details.author)
        except (CommandFailedError, HLLServerError):
            logger.exception("Failed to %s %s", repr(method), repr(aplayer))
            if method == ActionMethod.PUNISH:
                audit(aplayer.details.discord_audit_url, f"--> PUNISH FAILED, will retry: {aplayer}",
                      aplayer.details.author)
                for m in mods:
                    m.player_punish_failed(aplayer)
            elif method == ActionMethod.KICK:
                audit(aplayer.details.discord_audit_url, f"---> KICK FAILED, will retry <---: {aplayer}",
                      aplayer.details.author)


def punish_squads(rcon: RecordedRcon):
    red = get_redis_client()
    try:
        config = get_config()
        no_leader_config = NoLeaderConfig(**config["NOLEADER_AUTO_MOD"])
    except Exception as e:
        logger.exception("Invalid automod config, check your config/config.yml", e)
        raise

    enabled_moderators = list(filter(lambda m: m.enabled(), [
        NoLeaderAutomod(no_leader_config, red)
    ]))
    if len(enabled_moderators) == 0:
        logger.debug("No automod is enabled")
        return

    punitions_to_apply = get_punitions_to_apply(rcon, enabled_moderators)
    if punitions_to_apply:
        logger.info(
            "Automod will apply the following punitions %s",
            repr(punitions_to_apply),
        )
    else:
        logger.debug("Automod did not suggest any punitions")

    _do_punitions(rcon, ActionMethod.MESSAGE, punitions_to_apply.warning, enabled_moderators)

    _do_punitions(rcon, ActionMethod.PUNISH, punitions_to_apply.punish, enabled_moderators)

    _do_punitions(rcon, ActionMethod.KICK, punitions_to_apply.kick, enabled_moderators)


def audit(discord_webhook_url: str, msg: str, author: str):
    if discord_webhook_url is not None and discord_webhook_url != "":
        send_to_discord_audit(msg, by=author, webhookurl=discord_webhook_url, silent=False)


def run():
    rcon = RecordedRcon(SERVER_INFO)

    while True:
        try:
            punish_squads(rcon)
            time.sleep(5)
        except Exception:
            logger.exception("Squad automod: Something unexpected happened")
            raise

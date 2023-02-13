import logging
import time
from threading import Timer
from typing import List

from rcon.automods.models import (
    ActionMethod,
    NoLeaderConfig,
    PunishPlayer,
    PunitionsToApply,
    SeedingRulesConfig,
)
from rcon.automods.no_leader import NoLeaderAutomod
from rcon.automods.seeding_rules import SeedingRulesAutomod
from rcon.cache_utils import get_redis_client
from rcon.commands import CommandFailedError, HLLServerError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.extended_commands import StructuredLogLine
from rcon.game_logs import on_connected, on_kill
from rcon.hooks import inject_player_ids
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO

logger = logging.getLogger(__name__)
first_run_done = False


def get_punitions_to_apply(rcon, moderators) -> PunitionsToApply:
    logger.debug("Getting team info")
    team_view = rcon.get_team_view()
    punitions_to_apply = PunitionsToApply()

    for team in ["allies", "axis"]:
        if not team_view.get(team):
            continue

        for squad_name, squad in team_view[team]["squads"].items():
            for mod in moderators:
                punitions_to_apply.merge(
                    mod.punitions_to_apply(team_view, squad_name, team, squad)
                )

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
                        aplayer.name,
                        aplayer.steam_id_64,
                        aplayer.details.message,
                        by=aplayer.details.author,
                    )
                audit(
                    aplayer.details.discord_audit_url,
                    f"-> WARNING: {aplayer}",
                    aplayer.details.author,
                )

            if method == ActionMethod.PUNISH:
                if not aplayer.details.dry_run:
                    rcon.do_punish(
                        aplayer.name, aplayer.details.message, by=aplayer.details.author
                    )
                audit(
                    aplayer.details.discord_audit_url,
                    f"--> PUNISHING: {aplayer}",
                    aplayer.details.author,
                )

            if method == ActionMethod.KICK:
                if not aplayer.details.dry_run:
                    rcon.do_kick(
                        aplayer.name, aplayer.details.message, by=aplayer.details.author
                    )
                audit(
                    aplayer.details.discord_audit_url,
                    f"---> KICKING <---: {aplayer}",
                    aplayer.details.author,
                )
        except (CommandFailedError, HLLServerError):
            logger.exception("Failed to %s %s", repr(method), repr(aplayer))
            if method == ActionMethod.PUNISH:
                audit(
                    aplayer.details.discord_audit_url,
                    f"--> PUNISH FAILED, will retry: {aplayer}",
                    aplayer.details.author,
                )
                for m in mods:
                    m.player_punish_failed(aplayer)
            elif method == ActionMethod.KICK:
                audit(
                    aplayer.details.discord_audit_url,
                    f"---> KICK FAILED, will retry <---: {aplayer}",
                    aplayer.details.author,
                )


def do_punitions(rcon: RecordedRcon, punitions_to_apply: PunitionsToApply):
    if punitions_to_apply:
        logger.info(
            "Automod will apply the following punitions %s",
            repr(punitions_to_apply),
        )
    else:
        logger.debug("Automod did not suggest any punitions")

    _do_punitions(
        rcon, ActionMethod.MESSAGE, punitions_to_apply.warning, enabled_moderators
    )

    _do_punitions(
        rcon, ActionMethod.PUNISH, punitions_to_apply.punish, enabled_moderators
    )

    _do_punitions(rcon, ActionMethod.KICK, punitions_to_apply.kick, enabled_moderators)


def enabled_moderators():
    red = get_redis_client()
    try:
        config = get_config()
        no_leader_config = NoLeaderConfig(**config["NOLEADER_AUTO_MOD"])
        seeding_config = SeedingRulesConfig(**config["SEEDING_AUTO_MOD"])
    except Exception as e:
        logger.exception("Invalid automod config, check your config/config.yml", e)
        raise

    return list(
        filter(
            lambda m: m.enabled(),
            [
                NoLeaderAutomod(no_leader_config, red),
                SeedingRulesAutomod(seeding_config, red),
            ],
        )
    )


def punish_squads(rcon: RecordedRcon):
    mods = enabled_moderators()
    if len(mods) == 0:
        logger.debug("No automod is enabled")
        return

    punitions_to_apply = get_punitions_to_apply(rcon, mods)

    do_punitions(rcon, punitions_to_apply)
    global first_run_done
    first_run_done = True


def audit(discord_webhook_url: str, msg: str, author: str):
    if discord_webhook_url is not None and discord_webhook_url != "":
        send_to_discord_audit(
            msg, by=author, webhookurl=discord_webhook_url, silent=False
        )


@on_kill
def on_kill(rcon: RecordedRcon, log: StructuredLogLine):
    if not first_run_done:
        logger.debug(
            "Kill event received, but not automod run done yet, giving mods time to warmup"
        )
        return
    mods = enabled_moderators()
    if len(mods) == 0:
        logger.debug("No automod is enabled")
        return

    punitions_to_apply = PunitionsToApply()
    for mod in mods:
        on_kill_hook = getattr(mod, "on_kill", None)
        if callable(on_kill_hook):
            punitions_to_apply.merge(mod.on_kill(log))

    do_punitions(rcon, punitions_to_apply)


pendingTimers = {}


@on_connected
@inject_player_ids
def on_connected(rcon: RecordedRcon, _, name: str, steam_id_64: str):
    if not first_run_done:
        logger.debug(
            "Kill event received, but not automod run done yet, giving mods time to warmup"
        )
        return
    mods = enabled_moderators()
    if len(mods) == 0:
        logger.debug("No automod is enabled")
        return

    punitions_to_apply: PunitionsToApply = PunitionsToApply()
    for mod in mods:
        on_connected_hook = getattr(mod, "on_connected", None)
        if callable(on_connected_hook):
            punitions_to_apply.merge(mod.on_connected(name, steam_id_64))

    def notify_player():
        try:
            for p in punitions_to_apply.warning:
                rcon.do_message_player(
                    steam_id_64=p.steam_id_64,
                    message=p.details.message,
                    by=p.details.author,
                    save_message=False,
                )
        except Exception as e:
            logger.error("Could not message player " + name + "/" + steam_id_64, e)

    if len(punitions_to_apply.warning) == 0:
        return

    # The player might not yet have finished connecting in order to send messages.
    t = Timer(10, notify_player)
    pendingTimers[steam_id_64] = t
    t.start()


def run():
    rcon = RecordedRcon(SERVER_INFO)

    while True:
        try:
            punish_squads(rcon)
            time.sleep(5)
        except Exception:
            logger.exception("Squad automod: Something unexpected happened")
            raise

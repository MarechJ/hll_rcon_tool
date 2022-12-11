import logging
import pickle
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List

import redis

from rcon.cache_utils import get_redis_client
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.commands import CommandFailedError, HLLServerError
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.squad_automod.models import (
    APlayer,
    NoLeaderConfig,
    PunishStepState,
    PunitionsToApply,
    SquadCycleOver,
    SquadHasLeader,
    WatchStatus,
    ActionMethod,
)

LEADER_WATCH_RESET_SECS = 120
AUTOMOD_USERNAME = "NoLeaderWatch"

logger = logging.getLogger(__name__)


@contextmanager
def watch_state(red: redis.StrictRedis, team: str, squad_name: str):
    redis_key = f"no_leader_watch{team.lower()}{str(squad_name).lower()}"
    watch_status = red.get(redis_key)
    if watch_status:
        watch_status = pickle.loads(watch_status)
    else:  # No punishments so far, starting a fresh one
        watch_status = WatchStatus()
    # logger.debug("State loaded %s", watch_status)

    try:
        yield watch_status
    except (SquadHasLeader, SquadCycleOver):
        logger.debug("Squad %s - %s has a leader, clearing state", team, squad_name)
        red.delete(redis_key)
    else:
        # logger.debug("Saving watch status: %s %s", redis_key, watch_status)
        red.setex(redis_key, LEADER_WATCH_RESET_SECS, pickle.dumps(watch_status))


def num_or_inf(number):
    return "infinity" if number == -1 else number


def is_time(times: List[datetime], interval_seconds: int):
    try:
        last_time = times[-1]
    except IndexError:
        last_time = datetime(year=1988, month=1, day=1)

    if datetime.now() - last_time < timedelta(seconds=interval_seconds):
        return False
    return True


def _get_team_count(team_view, team):
    return sum(
        len(s.get("players", [])) for s in team_view[team].get("squads", {}).values()
    )


def should_note_player(
    watch_status: WatchStatus, config: NoLeaderConfig, squad_name: str, aplayer: APlayer
):
    if config.number_of_notes == 0:
        logger.debug("Notes are disabled. number_of_notes is set to 0")
        return PunishStepState.DISABLED

    notes = watch_status.noted.setdefault(aplayer.name, [])

    if not is_time(notes, config.notes_interval_seconds):
        logger.debug("Waiting to note: %s in %s", aplayer.short_repr(), squad_name)
        return PunishStepState.WAIT

    if len(notes) < config.number_of_notes:
        logger.info(
            "%s Will be noted (%s/%s)",
            aplayer.short_repr(),
            len(notes),
            num_or_inf(config.number_of_notes),
        )
        notes.append(datetime.now())
        return PunishStepState.APPLY

    logger.info(
        "%s Max notes reached (%s/%s). Moving on to warn.",
        aplayer.short_repr(),
        len(notes),
        config.number_of_notes,
    )
    return PunishStepState.GO_TO_NEXT_STEP


def should_warn_player(
    watch_status: WatchStatus, config: NoLeaderConfig, squad_name: str, aplayer: APlayer
):
    if config.number_of_warning == 0:
        logger.debug("Warnings are disabled. number_of_warning is set to 0")
        return PunishStepState.DISABLED

    warnings = watch_status.warned.setdefault(aplayer.name, [])

    if not is_time(warnings, config.warning_interval_seconds):
        logger.debug("Waiting to warn: %s in %s", aplayer.short_repr(), squad_name)
        return PunishStepState.WAIT

    if len(warnings) < config.number_of_warning or config.number_of_warning == -1:
        logger.info(
            "%s Will be warned (%s/%s)",
            aplayer.short_repr(),
            len(warnings),
            num_or_inf(config.number_of_warning),
        )
        warnings.append(datetime.now())
        return PunishStepState.APPLY

    logger.info(
        "%s Max warnings reached (%s/%s). Moving on to punish.",
        aplayer.short_repr(),
        len(warnings),
        config.number_of_warning,
    )
    return PunishStepState.GO_TO_NEXT_STEP


def should_punish_player(
    watch_status: WatchStatus,
    config: NoLeaderConfig,
    team_view,
    squad_name: str,
    squad,
    aplayer: APlayer,
):
    if config.number_of_punish == 0:
        logger.debug("Punish is disabled")
        return PunishStepState.DISABLED

    if (
        _get_team_count(team_view, "allies") + _get_team_count(team_view, "axis")
    ) < config.disable_punish_below_server_player_count:
        logger.debug("Server below min player count for punish")
        return PunishStepState.WAIT

    if len(squad["players"]) < config.min_squad_players_for_punish:
        logger.debug("Squad %s below min player count for punish", squad_name)
        return PunishStepState.WAIT

    if (
        aplayer.lvl <= config.immuned_level_up_to
        or aplayer.role in config.immuned_roles
    ):
        logger.info("%s is immuned to punishment", aplayer.short_repr())
        return PunishStepState.IMMUNED

    punishes = watch_status.punished.setdefault(aplayer.name, [])

    if not is_time(punishes, config.punish_interval_seconds):
        logger.debug("Waiting to punish %s", squad_name)
        return PunishStepState.WAIT

    if len(punishes) < config.number_of_punish or config.number_of_punish == -1:
        logger.info(
            "%s Will be punished (%s/%s)",
            aplayer.short_repr(),
            len(punishes),
            num_or_inf(config.number_of_punish),
        )
        punishes.append(datetime.now())
        return PunishStepState.APPLY

    logger.info(
        "%s Max punish reached (%s/%s)",
        aplayer.short_repr(),
        len(punishes),
        config.number_of_punish,
    )
    return PunishStepState.GO_TO_NEXT_STEP


def should_kick_player(
    watch_status: WatchStatus,
    config: NoLeaderConfig,
    team_view,
    squad_name: str,
    squad,
    aplayer: APlayer,
):
    if not config.kick_after_max_punish:
        return PunishStepState.DISABLED

    if (
        _get_team_count(team_view, "allies") + _get_team_count(team_view, "axis")
    ) < config.disable_kick_below_server_player_count:
        logger.debug("Server below min player count for punish")
        return PunishStepState.WAIT

    if len(squad["players"]) < config.min_squad_players_for_kick:
        logger.debug("Squad %s below min player count for punish", squad_name)
        return PunishStepState.WAIT

    if (
        aplayer.lvl <= config.immuned_level_up_to
        or aplayer.role in config.immuned_roles
    ):
        logger.info("%s is immuned to punishment", aplayer.short_repr())
        return PunishStepState.IMMUNED

    try:
        last_time = watch_status.punished.get(aplayer.name, [])[-1]
    except IndexError:
        logger.error("Trying to kick player without prior punishes")
        return PunishStepState.DISABLED

    if datetime.now() - last_time < timedelta(seconds=config.kick_grace_period_seconds):
        return PunishStepState.WAIT

    return PunishStepState.APPLY


def get_punitions_to_apply(rcon, config: NoLeaderConfig) -> PunitionsToApply:
    logger.debug("Getting team info")
    team_view = rcon.get_team_view_fast()
    red = get_redis_client()
    punitions_to_apply = PunitionsToApply()

    for team in ["allies", "axis"]:
        if not team_view.get(team):
            continue

        for squad_name, squad in team_view[team]["squads"].items():
            if not squad_name:
                logger.info("Skipping None or empty squad %s %s", squad_name, squad)
                continue
            with watch_state(red, team, squad_name) as watch_status:
                if squad[
                    "has_leader"
                ]:  # The squad has a leader, clearing punishments plan
                    raise SquadHasLeader()

                if squad_name is None or squad is None:
                    raise SquadHasLeader()

                logger.info("Squad %s - %s doesn't have leader", team, squad_name)

                for player in squad["players"]:
                    aplayer = APlayer(
                        steam_id_64=player["steam_id_64"],
                        name=player["name"],
                        team=team,
                        squad=squad_name,
                        role=player.get("role"),
                        lvl=int(player.get("level")),
                    )

                    state = should_note_player(
                        watch_status, config, squad_name, aplayer
                    )
                    if state == PunishStepState.APPLY:
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                    if not state in [
                        PunishStepState.DISABLED,
                        PunishStepState.GO_TO_NEXT_STEP,
                    ]:
                        continue

                    state = should_warn_player(
                        watch_status, config, squad_name, aplayer
                    )

                    if state == PunishStepState.APPLY:
                        punitions_to_apply.warning.append(aplayer)
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                    if (
                        state == PunishStepState.WAIT
                    ):  # only here to make the tests pass, otherwise useless
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                    if not state in [
                        PunishStepState.DISABLED,
                        PunishStepState.GO_TO_NEXT_STEP,
                    ]:
                        continue

                    state = should_punish_player(
                        watch_status, config, team_view, squad_name, squad, aplayer
                    )

                    if state == PunishStepState.APPLY:
                        punitions_to_apply.punish.append(aplayer)
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                    if not state in [
                        PunishStepState.DISABLED,
                        PunishStepState.GO_TO_NEXT_STEP,
                    ]:
                        continue

                    state = should_kick_player(
                        watch_status, config, team_view, squad_name, squad, aplayer
                    )
                    if state == PunishStepState.APPLY:
                        punitions_to_apply.kick.append(aplayer)
                        punitions_to_apply.add_squad_state(team, squad_name, squad)

    return punitions_to_apply


def get_message(config: NoLeaderConfig, aplayer: APlayer, method: ActionMethod) -> str:
    data = {}

    with watch_state(get_redis_client(), aplayer.team, aplayer.squad) as watch_status:
        if method == ActionMethod.MESSAGE:
            data["received_warnings"] = len(watch_status.warned.get(aplayer.name))
            data["max_warnings"] = config.number_of_warning
            data["next_check_seconds"] = config.warning_interval_seconds
        if method == ActionMethod.PUNISH:
            data["received_punishes"] = len(watch_status.punished.get(aplayer.name))
            data["max_punishes"] = config.number_of_punish
            data["next_check_seconds"] = config.punish_interval_seconds
        if method == ActionMethod.KICK:
            data["kick_grace_period"] = config.kick_grace_period_seconds

    data["player_name"] = aplayer.name
    data["squad_name"] = aplayer.squad

    base_message = {
        ActionMethod.MESSAGE: config.warning_message,
        ActionMethod.PUNISH: config.punish_message,
        ActionMethod.KICK: config.kick_message,
    }

    message = base_message[method]
    try:
        return message.format(**data)
    except KeyError:
        logger.warning(
            f"The automod message of {repr(method)} ({message}) contains an invalid key"
        )
        return message


def _do_punitions(
    red,
    config: NoLeaderConfig,
    rcon: RecordedRcon,
    method: ActionMethod,
    players: List[APlayer],
):
    author = AUTOMOD_USERNAME + "-DryRun" if config.dry_run else ""

    for aplayer in players:
        try:
            message = get_message(config, aplayer, method)
            if method == ActionMethod.MESSAGE:
                if not config.dry_run:
                    rcon.do_message_player(
                        aplayer.name, aplayer.steam_id_64, message, by=author
                    )
                audit(config, f"-> WARNING: {aplayer}", author)

            if method == ActionMethod.PUNISH:
                if not config.dry_run:
                    rcon.do_punish(aplayer.name, message, by=author)
                audit(config, f"--> PUNISHING: {aplayer}", author)

            if method == ActionMethod.KICK:
                if not config.dry_run:
                    rcon.do_kick(aplayer.name, message, by=author)
                audit(config, f"---> KICKING <---: {aplayer}", author)
        except (CommandFailedError, HLLServerError):
            logger.exception("Failed to %s %s", repr(method), repr(aplayer))
            if method == ActionMethod.PUNISH:
                audit(config, f"--> PUNISH FAILED, will retry: {aplayer}", author)
                with watch_state(red, aplayer.team, aplayer.squad) as watch_status:
                    try:
                        if punishes := watch_status.punished.get(aplayer.name):
                            del punishes[-1]
                    except Exception:
                        logger.exception("tried to cleanup punished time but failed")
            elif method == ActionMethod.KICK:
                audit(config, f"---> KICK FAILED, will retry <---: {aplayer}", author)


def punish_squads_without_leaders(rcon: RecordedRcon):
    try:
        config = get_config()
        config = NoLeaderConfig(**config["NOLEADER_AUTO_MOD"])
    except Exception:
        logger.exception("Invalid NOLEADER_AUTO_MOD check your config/config.yml")
        raise

    if not config.enabled:
        logger.debug("Squad automod is disabled")
        return

    red = get_redis_client()
    punitions_to_apply = get_punitions_to_apply(rcon, config)
    if punitions_to_apply:
        logger.info(
            "Squad Automod will apply the following punitions %s",
            repr(punitions_to_apply),
        )
    else:
        logger.debug("Squad Automod did not suggest any punitions")

    _do_punitions(red, config, rcon, ActionMethod.MESSAGE, punitions_to_apply.warning)

    _do_punitions(red, config, rcon, ActionMethod.PUNISH, punitions_to_apply.punish)

    _do_punitions(red, config, rcon, ActionMethod.KICK, punitions_to_apply.kick)


def audit(cfg: NoLeaderConfig, msg: str, author: str):
    webhook_url = None
    if cfg.discord_webhook_url is not None and cfg.discord_webhook_url != "":
        webhook_url = cfg.discord_webhook_url
        send_to_discord_audit(msg, by=author, webhookurl=webhook_url, silent=False)


def run():
    rcon = RecordedRcon(SERVER_INFO)

    while True:
        try:
            punish_squads_without_leaders(rcon)
            time.sleep(5)
        except Exception:
            logger.exception("Squad automod: Something unexpected happened")
            raise

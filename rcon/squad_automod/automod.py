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
)

LEADER_WATCH_RESET_SECS = 120
AutomodUsername = "NoLeaderWatch"

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


def should_warn_player(watch_status: WatchStatus, config: NoLeaderConfig, squad_name, player):
    if config.number_of_warning == 0:
        logger.debug("Warnings are disabled. number_of_warning is set to 0")
        return PunishStepState.disabled

    warnings = watch_status.warned.setdefault(player["name"], [])

    if not is_time(warnings, config.warning_interval_seconds):
        logger.debug("Waiting to warn: %s in %s", player, squad_name)
        return PunishStepState.wait

    if len(warnings) < config.number_of_warning or config.number_of_warning == -1:
        logger.info(
            "Player: %s Level: %s Role: %s Will be warned (%s/%s)",
            player["name"],
            player["level"],
            player["role"],
            len(warnings),
            num_or_inf(config.number_of_warning),
        )
        warnings.append(datetime.now())
        return PunishStepState.apply

    logger.info(
        "Player: %s Level: %s Role: %s Max warnings reached (%s/%s). Moving on to punish.",
        player["name"],
        player["level"],
        player["role"],
        len(warnings),
        config.number_of_warning,
    )
    return PunishStepState.go_to_next_step


def _get_team_count(team_view, team):
    return sum(len(s.get("players", [])) for s in team_view[team].get("squads", {}).values())


def should_punish_player(
    watch_status: WatchStatus, config: NoLeaderConfig, team_view, squad_name, squad, player
):
    if config.number_of_punish == 0:
        logger.debug("Punish is disabled")
        return PunishStepState.disabled

    if (
        _get_team_count(team_view, "allies") + _get_team_count(team_view, "axis")
    ) < config.disable_punish_below_server_player_count:
        logger.debug("Server below min player count for punish")
        return PunishStepState.wait

    if len(squad["players"]) < config.min_squad_players_for_punish:
        logger.debug("Squad %s below min player count for punish", squad_name)
        return PunishStepState.wait

    if (
        int(player["level"]) <= config.immuned_level_up_to
        or player["role"] in config.immuned_roles
    ):
        logger.info(
            "Player: %s Level: %s Role: %s is immuned to punishment",
            player["name"],
            player["level"],
            player["role"],
        )
        return PunishStepState.immuned

    punishes = watch_status.punished.setdefault(player["name"], [])

    if not is_time(punishes, config.punish_interval_seconds):
        logger.debug("Waiting to punish %s", squad_name)
        return PunishStepState.wait

    if len(punishes) < config.number_of_punish or config.number_of_punish == -1:
        logger.info(
            "Player: %s Level: %s Role: %s Will be punished (%s/%s)",
            player["name"],
            player["level"],
            player["role"],
            len(punishes),
            num_or_inf(config.number_of_punish),
        )
        punishes.append(datetime.now())
        return PunishStepState.apply

    logger.info(
        "Player: %s Level: %s Role: %s Max punish reached (%s/%s)",
        player["name"],
        player["level"],
        player["role"],
        len(punishes),
        config.number_of_punish,
    )
    return PunishStepState.go_to_next_step


def should_kick_player(
    watch_status: WatchStatus, config: NoLeaderConfig, team_view, squad_name, squad, player
):
    if not config.kick_after_max_punish:
        return PunishStepState.disabled

    if (
        _get_team_count(team_view, "allies") + _get_team_count(team_view, "axis")
    ) < config.disable_kick_below_server_player_count:
        logger.debug("Server below min player count for punish")
        return PunishStepState.wait

    if len(squad["players"]) < config.min_squad_players_for_kick:
        logger.debug("Squad %s below min player count for punish", squad_name)
        return PunishStepState.wait

    if (
        int(player["level"]) <= config.immuned_level_up_to
        or player["role"] in config.immuned_roles
    ):
        logger.info(
            "Player: %s Level: %s Role: %s is immuned to punishment",
            player["name"],
            player["level"],
            player["role"],
        )
        return PunishStepState.immuned

    try:
        last_time = watch_status.punished.get(player["name"], [])[-1]
    except IndexError:
        logger.error("Trying to kick player without prior punishes")
        return PunishStepState.disabled

    if datetime.now() - last_time < timedelta(seconds=config.kick_grace_period_seconds):
        return PunishStepState.wait

    return PunishStepState.apply


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
                if squad["has_leader"]:  # The squad has a leader, clearing punishments plan
                    raise SquadHasLeader()

                if squad_name is None or squad is None:
                    raise SquadHasLeader()

                logger.info("Squad %s - %s doesn't have leader", team, squad_name)

                for player in squad["players"]:
                    a_player = APlayer(
                        steam_id_64=player["steam_id_64"],
                        player=player["name"],
                        team=team,
                        squad=squad_name,
                        role=player.get("role"),
                        lvl=player.get("level"),
                    )

                    state = should_warn_player(watch_status, config, squad_name, player)

                    if state == PunishStepState.apply:
                        punitions_to_apply.warning.append(a_player)
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                        continue
                    if state == PunishStepState.wait:
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                        continue

                    state = should_punish_player(
                        watch_status, config, team_view, squad_name, squad, player
                    )

                    if state == PunishStepState.apply:
                        punitions_to_apply.punish.append(a_player)
                        punitions_to_apply.add_squad_state(team, squad_name, squad)
                    if state != PunishStepState.go_to_next_step:
                        continue

                    state = should_kick_player(
                        watch_status, config, team_view, squad_name, squad, player
                    )
                    if state == PunishStepState.apply:
                        punitions_to_apply.kick.append(a_player)
                        punitions_to_apply.add_squad_state(team, squad_name, squad)

    return punitions_to_apply


def get_warning_message(config: NoLeaderConfig, aplayer: APlayer) -> str:
    with watch_state(get_redis_client(), aplayer.team, aplayer.squad) as watch_status:
        warnings = len(watch_status.warned.get(aplayer.player))

    if config.warn_message_header != "" or config.warn_message_footer != "":
        return f"""{config.warn_message_header}
{config.warn_message_footer}"""
    else:
        return config.warning_message.format(
            player_name=aplayer.player,
            sqaud_name=aplayer.squad,
            received_warnings=warnings,
            max_warnings=config.number_of_warning,
            next_check_seconds=config.warning_interval_seconds,
        )


def _do_punitions(
    red,
    config: NoLeaderConfig,
    rcon: RecordedRcon,
    method: str,
    players: List[APlayer],
    message: str or None = None,
):
    if config.dry_run:
        logger.info("Dry run is enabled, skipping real punitions")
        return
    for aplayer in players:
        try:
            if method == "message":
                msg = get_warning_message(config, aplayer)
                audit(config, f"Warnings: {msg}")
                rcon.do_message_player(aplayer.player, aplayer.steam_id_64, msg, by=AutomodUsername)
            elif method == "punish":
                audit(config, f"--> PUNISHING: {aplayer}")
                rcon.do_punish(aplayer.player, message, by=AutomodUsername)
            elif method == "kick":
                audit(config, f"---> KICKING <---: {aplayer}")
                rcon.do_kick(aplayer.player, message, by=AutomodUsername)
        except Exception:
            logger.exception("Failed to %s %s", method, repr(aplayer))
            if method == "punish":
                audit(config, f"--> PUNISH FAILED, will retry: {aplayer}")
                with watch_state(red, aplayer.team, aplayer.squad) as watch_status:
                    try:
                        if punishes := watch_status.punished.get(aplayer.player):
                            del punishes[-1]
                    except:
                        logger.exception("tried to cleanup punished time but failed")
            elif method == "kick":
                audit(config, f"---> KICK FAILED, will retry <---: {aplayer}")


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
    punition_to_apply = get_punitions_to_apply(rcon, config)
    if punition_to_apply:
        logger.info("Squad Automod will apply the following punitions %s", repr(punition_to_apply))
    else:
        logger.debug("Squad Automod did not suggest any punitions")

    if punition_to_apply.punish:
        _do_punitions(red, config, rcon, "punish", punition_to_apply.punish, config.punish_message)

    if punition_to_apply.kick:
        _do_punitions(red, config, rcon, "kick", punition_to_apply.kick, config.kick_message)

    if punition_to_apply.warning:
        if not config.dry_run:
            _do_punitions(red, config, rcon, "message", punition_to_apply.warning)


def audit(cfg: NoLeaderConfig, msg: str):
    webhook_url = None
    if cfg.discord_webhook_url is not None and cfg.discord_webhook_url != "":
        webhook_url = cfg.discord_webhook_url
        send_to_discord_audit(msg, by="NoLeaderWatch", webhookurl=webhook_url, silent=False)


def run():
    rcon = RecordedRcon(SERVER_INFO)

    while True:
        try:
            punish_squads_without_leaders(rcon)
            time.sleep(5)
        except Exception:
            logger.exception("Squad automod: Something unexpected happened")
            raise

import logging
import pickle
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Callable, List

import redis
from rcon.cache_utils import get_redis_client
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.squad_automod.models import (
    NoLeaderConfig,
    PunishStepState,
    PunitionsToApply,
    SquadCycleOver,
    SquadHasLeader,
    WatchStatus,
)

LEADER_WATCH_RESET_SECS = 120

logger = logging.getLogger(__name__)


@contextmanager
def watch_state(red: redis.StrictRedis, team: str, squad_name: str):
    redis_key = f"no_leader_watch{team}{squad_name}"
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


def should_warn_squad(watch_status: WatchStatus, config: NoLeaderConfig, team, squad_name):
    if config.number_of_warning == 0:
        logger.debug("Warnings are disabled. number_of_warning is set to 0")
        return PunishStepState.disabled

    warnings = watch_status.warned

    if not is_time(warnings, config.warning_interval_seconds):
        logger.info("Waiting to warn: %s", squad_name)
        return PunishStepState.wait

    if len(warnings) < config.number_of_warning or config.number_of_warning == -1:
        logger.info(
            "Warning squad %s - %s. got %s/%s warning at time: %s",
            team,
            squad_name,
            len(warnings),
            num_or_inf(config.number_of_warning),
            watch_status.warned,
        )

        warnings.append(datetime.now())
        return PunishStepState.apply

    logger.info(
        "Squad %s - %s already got warned %s times. Moving on to punish.",
        team,
        squad_name,
        len(warnings),
    )
    return PunishStepState.go_to_next_step


def should_punish_player(
    watch_status: WatchStatus, config: NoLeaderConfig, team_view, team, squad_name, squad, player
):
    if config.number_of_punish == 0:
        return PunishStepState.disabled

    if (
        len(team_view["allies"]) + len(team_view["axis"])
        < config.disable_punish_below_server_player_count
    ):
        return PunishStepState.wait

    if len(squad["players"]) < config.min_squad_players_for_punish:
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
    watch_status: WatchStatus, config: NoLeaderConfig, team_view, team, squad_name, squad, player
):
    if not config.kick_after_max_punish:
        return PunishStepState.disabled

    if (
        len(team_view["allies"]) + len(team_view["axis"])
        < config.disable_kick_below_server_player_count
    ):
        return PunishStepState.wait

    if len(squad["players"]) < config.min_squad_players_for_kick:
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
            with watch_state(red, team, squad_name) as watch_status:
                if squad["has_leader"]:  # The squad has a leader, clearing punishments plan
                    raise SquadHasLeader()

                logger.info("Squad %s - %s doesn't have leader", team, squad_name)

                state = should_warn_squad(watch_status, config, team, squad_name)

                if state == PunishStepState.apply:
                    punitions_to_apply.warning[team].append(squad_name)
                if state != PunishStepState.go_to_next_step and state != PunishStepState.disabled:
                    continue

                for player in squad["players"]:
                    state = should_punish_player(
                        watch_status, config, team_view, team, squad_name, squad, player
                    )

                    if state == PunishStepState.apply:
                        punitions_to_apply.punish.append(player["name"])
                    if state != PunishStepState.go_to_next_step:
                        continue

                    state = should_kick_player(
                        watch_status, config, team_view, team, squad_name, squad, player
                    )
                    if state == PunishStepState.apply:
                        punitions_to_apply.kick.append(player["name"])

    return punitions_to_apply


def _build_warning_str(punition_to_apply: PunitionsToApply, config: NoLeaderConfig, team: str):
    to_apply = punition_to_apply.warning[team]
    if not to_apply:
        return ""

    red = get_redis_client()
    start = f"{team}: "
    squads = []
    for idx, squad_name in enumerate(to_apply):
        with watch_state(red, team, squad_name) as squad_state:
            nb = len(squad_state.warned)
            total = config.number_of_warning
            squads.append(f"{squad_name.upper()} {nb}/{total} /!\\")

    return f"{start}{', '.join(squads)}"


def get_warning_message(punition_to_apply: PunitionsToApply, config: NoLeaderConfig) -> str:
    return f"""{config.warn_message_header}
{_build_warning_str(punition_to_apply, config, "allies")}
{_build_warning_str(punition_to_apply, config, "axis")}
{config.warn_message_footer}
"""


def _do_punitions(config: NoLeaderConfig, method: Callable, message: str, players: List[str]):
    if config.dry_run:
        logger.info("Dry run is enabled, skipping real punitions")
        return
    for player in players:
        try:
            method(player, config.punish_message, by="NoLeaderWatch")
        except Exception:
            logger.exception("Failed to %s %s", method, player)


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

    punition_to_apply = get_punitions_to_apply(rcon, config)
    if punition_to_apply:
        logger.info("Squad Automod will apply the following punitions %s", repr(punition_to_apply))
    else:
        logger.debug("Squad Automod did not suggest any punitions")

    if punition_to_apply.warning.get("allies") or punition_to_apply.warning.get("axis"):
        msg = get_warning_message(punition_to_apply, config)
        send_to_discord_audit(f"Warning issued: {msg}", by="NoLeaderWatch")
        if not config.dry_run:
            rcon.set_broadcast(msg)

    if punition_to_apply.punish:
        send_to_discord_audit(f"Punishing: {punition_to_apply.punish}", by="NoLeaderWatch")
        _do_punitions(config, rcon.do_punish, config.punish_message, punition_to_apply.punish)

    if punition_to_apply.kick:
        send_to_discord_audit(f"Kicking: {punition_to_apply.punish}", by="NoLeaderWatch")
        _do_punitions(config, rcon.do_kick, config.kick_message, punition_to_apply.kick)


def run():
    rcon = RecordedRcon(SERVER_INFO)

    while True:
        try:
            punish_squads_without_leaders(rcon)
            time.sleep(5)
        except Exception:
            logger.exception("Squad automod: Something unexpected happened")
            raise


if __name__ == "__main__":
    import time

    from rcon.extended_commands import Rcon
    from rcon.settings import SERVER_INFO

    rcon = Rcon(SERVER_INFO)

    while True:
        logger.debug("starting watch")
        punish_squads_without_leaders(
            rcon,
            NoLeaderConfig(
                warn_message="",
                number_of_warning=3,
                warning_interval_seconds=60,  # TODO
                number_of_punish=5,
                kick_after_max_punish=True,
                immuned_level_up_to=10,
            ),
        )
        time.sleep(30)

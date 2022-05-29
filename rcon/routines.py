import logging
import pickle
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Mapping

import redis

from rcon.audit import ingame_mods, online_mods
from rcon.cache_utils import get_redis_client
from rcon.extended_commands import CommandFailedError
from rcon.map_recorder import MapsRecorder
from rcon.recorded_commands import RecordedRcon
from rcon.user_config import AutoVoteKickConfig

logger = logging.getLogger(__name__)


def toggle_votekick(rcon: RecordedRcon):
    config = AutoVoteKickConfig()

    if not config.is_enabled():
        return

    condition_type = config.get_condition_type().upper()
    min_online = config.get_min_online_mods()
    min_ingame = config.get_min_ingame_mods()
    condition = all if condition_type == "AND" else any
    online_mods_ = online_mods()
    ingame_mods_ = ingame_mods(rcon)

    ok_online = len(online_mods_) >= min_online
    ok_ingame = len(ingame_mods_) >= min_ingame

    if condition([ok_ingame, ok_online]):
        logger.debug(
            f"Turning votekick off {condition_type=} {min_online=} {min_ingame=} {ok_online=} {ok_ingame=} {online_mods_=} {ingame_mods_=}"
        )
        rcon.set_votekick_enabled(False)
    else:
        logger.debug(
            f"Turning votekick on {condition_type=} {min_online=} {min_ingame=} {ok_online=} {ok_ingame=} {online_mods_=} {ingame_mods_=}"
        )
        rcon.set_votekick_enabled(True)

@dataclass
class WatchStatus:
    warned: List[datetime] = field(default_factory=list)
    punished: Mapping[str, List[datetime]] = field(default_factory=dict)

from enum import Enum, auto


class PunishStepState(Enum):
    wait = auto()
    immuned = auto()
    disabled = auto()
    apply = auto()
    go_to_next_step = auto()


@dataclass
class NoLeaderConfig:
    warn_message: str = "TODO"
    # Set to 0 to disable, -1 for infinite warnings (will never go to punishes)
    number_of_warning: int = 2
    warning_interval_seconds: int = 60

    # Set to 0 to disable, -1 for infinite punish (will never go to kicks)
    number_of_punish: int = 0
    punish_interval_seconds: int = 60
    min_squad_players_for_punish: int = 3
    disable_punish_below_server_player_count: int = 60

    kick_after_max_punish: bool = False
    disable_kick_below_server_player_count: int = 60
    min_squad_players_for_kick: int = 3
    kick_grace_period_seconds: int = 120
    # roles: 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner', 'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
    immuned_roles: List[str] = field(default_factory=lambda: ["support", "sniper"])
    immuned_level_up_to: int = 15


class SquadHasLeader(Exception):
    pass

class SquadCycleOver(Exception):
    pass


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

@dataclass
class PunitionsToApply:
    warning: Mapping[str, List[str]] = field(default_factory=lambda: {"allies": [], "axis": []})
    punish: List[str] = field(default_factory=list)
    kick: List[str] = field(default_factory=list)


def punish_squads_without_leaders(rcon, config: NoLeaderConfig):
    logger.debug("Getting team info")
    team_view = rcon.get_team_view_fast()
    red = get_redis_client()
    punitions_to_apply = PunitionsToApply()

    logger.debug("Started watch round")
    for team in ["allies", "axis"]:
        for squad_name, squad in team_view[team]["squads"].items():
            with watch_state(red, team, squad_name) as watch_status:
                if squad["has_leader"]:  # The squad has a leader, clearing punishments plan
                    raise SquadHasLeader()

                logger.info("Squad %s - %s doesn't have leader", team, squad_name)

                state = should_warn_squad(watch_status, config, team, squad_name)

                if state == PunishStepState.apply:
                    punitions_to_apply.warning[team].append(squad_name)
                if state != PunishStepState.go_to_next_step:
                    continue

                for player in squad["players"]:
                    state = should_punish_player(watch_status, config, team_view, team, squad_name, squad, player)

                    if state == PunishStepState.apply:
                        punitions_to_apply.punish.append(player["name"])
                    if state != PunishStepState.go_to_next_step:
                        continue

                    state = should_kick_player(watch_status, config, team_view, team, squad_name, squad, player)
                    if state == PunishStepState.apply:
                        punitions_to_apply.kick.append(player["name"])               
                

    return punitions_to_apply


LEADER_WATCH_RESET_SECS = 60 * 10


def run():
    max_fails = 5
    from rcon.settings import SERVER_INFO

    rcon = RecordedRcon(SERVER_INFO)
    recorder = MapsRecorder(rcon)

    while True:
        try:
            recorder.detect_map_change()
            toggle_votekick(rcon)
        except CommandFailedError:
            max_fails -= 1
            if max_fails <= 0:
                logger.exception("Routines 5 failures in a row. Stopping")
                raise
        time.sleep(30)


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

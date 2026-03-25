import datetime
import logging
import time

from rcon.audit import ingame_mods, online_mods
from rcon.perf_statistics import PerformanceStatistics
from rcon.rcon import HLLCommandFailedError, Rcon, get_rcon
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.vote_map import VoteMap
from rcon.workers import get_scheduler

logger = logging.getLogger(__name__)


def toggle_votekick(rcon: Rcon):
    config = AutoVoteKickUserConfig.load_from_db()

    if not config.enabled:
        return

    condition_type = config.condition.upper()
    min_online = config.minimum_online_mods
    min_ingame = config.minimum_ingame_mods
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


def dump_rcon_performance_stats():
    pl = PerformanceStatistics('rcon', True)
    d = pl.dump()
    for k, v in d.items():
        logger.info(f"{k}: {v}")


def run():
    max_fails = 5
    rcon = get_rcon()

    if rcon.performance_stats_interval() > 0:
        get_scheduler().schedule(
            scheduled_time=datetime.datetime.now(datetime.UTC),
            func=dump_rcon_performance_stats,
            interval=rcon.performance_stats_interval(),
            id='dump_performance_logs',
        )

    while True:
        try:
            toggle_votekick(rcon)
            VoteMap().vote_map_reminder(rcon)
        except HLLCommandFailedError:
            max_fails -= 1
            if max_fails <= 0:
                logger.exception("Routines 5 failures in a row. Stopping")
                raise
        time.sleep(30)

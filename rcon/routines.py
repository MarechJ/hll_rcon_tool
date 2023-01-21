import asyncio
import logging
import os

from rcon import broadcast
from rcon.audit import ingame_mods, online_mods
from rcon.commands import CommandFailedError
from rcon.expiring_vips import service
from rcon.recorded_commands import RecordedRcon
from rcon.user_config import AutoVoteKickConfig
from rcon.vote_map import VoteMap

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


async def scheduled_routines(rcon: RecordedRcon):
    max_fails = 5
    while True:
        try:
            toggle_votekick(rcon)
            VoteMap().vote_map_reminder(rcon)
        except CommandFailedError:
            max_fails -= 1
            if max_fails <= 0:
                logger.exception("scheduled routines 5 failures in a row. Stopping")
                raise
        await asyncio.sleep(30)


async def auto_broadcast(log: logging.Logger, rcon: RecordedRcon):
    log.debug("Starting broadcasts")
    await broadcast.run(log, rcon)


async def expire_vips(log: logging.Logger, rcon: RecordedRcon):
    log.debug("Starting expiring vips")
    await service.run(rcon)


def component_logger(name: str, server_number: str) -> logging.Logger:
    filename = f"{name}_{server_number}.log"
    handler = logging.FileHandler(filename)

    log = logging.getLogger(name)
    level = os.getenv("LOGGING_LEVEL")
    if level is not None:
        log.setLevel(level)
    log.addHandler(handler)

    return log


async def run():
    from rcon.settings import SERVER_INFO
    rcon = RecordedRcon(SERVER_INFO)
    server_number = os.getenv("SERVER_NUMBER")

    tasks = asyncio.gather(
        scheduled_routines(rcon),
        auto_broadcast(component_logger("broadcasts", server_number), rcon),
        expire_vips(component_logger("expiring_vips", server_number), rcon),
    )
    try:
        await tasks
    except Exception as e:
        logger.exception("Routines failed", e)
        tasks.cancel()
        exit(1)

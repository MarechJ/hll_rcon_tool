import asyncio
import logging
import time

from rcon import broadcast
from rcon.audit import ingame_mods, online_mods
from rcon.commands import CommandFailedError
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


async def auto_broadcast(rcon: RecordedRcon):
    logger.debug("Starting broadcasts")
    await broadcast.run(rcon)


async def run():
    from rcon.settings import SERVER_INFO
    rcon = RecordedRcon(SERVER_INFO)

    tasks = asyncio.gather(
        scheduled_routines(rcon),
        auto_broadcast(rcon)
    )
    try:
        await tasks
    except Exception as e:
        logger.exception("Routines failed", e)
        tasks.cancel()
        exit(1)

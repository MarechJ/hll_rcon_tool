import logging
import time

from rcon.audit import ingame_mods, online_mods
from rcon.commands import CommandFailedError
from rcon.rcon import CommandFailedError, Rcon
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.vote_map import VoteMap

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


def run():
    max_fails = 5
    from rcon.settings import SERVER_INFO

    rcon = Rcon(SERVER_INFO)

    while True:
        try:
            toggle_votekick(rcon)
            VoteMap().vote_map_reminder(rcon)
        except CommandFailedError:
            max_fails -= 1
            if max_fails <= 0:
                logger.exception("Routines 5 failures in a row. Stopping")
                raise
        time.sleep(30)

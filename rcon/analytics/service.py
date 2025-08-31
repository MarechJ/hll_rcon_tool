from logging import getLogger
import time

from rcon.analytics.system_usage import get_system_usage
from rcon.audit import ingame_mods
from rcon.models import AnalyticsServerStatus, AnalyticsSystemUsage
from rcon.rcon import get_rcon
from rcon.utils import get_server_number

logger = getLogger(__name__)

FIVE_MINUTES = 5 * 60


def run():
    while True:
        rcon = get_rcon()
        server_number = int(get_server_number())
        players = list(rcon.get_detailed_players()["players"].values())
        mods = ingame_mods(rcon)

        try:
            AnalyticsServerStatus.save(
                server_number=server_number, players=players, ingame_mods=mods
            )

            AnalyticsSystemUsage.save(
                system_usage=get_system_usage(1), interval_sec=FIVE_MINUTES
            )
        except Exception as e:
            logger.exception(e)

        time.sleep(FIVE_MINUTES)

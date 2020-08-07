import os
import time
import logging
import random

from rcon.settings import SERVER_INFO
from rcon.user_config import AutoBroadcasts
from rcon.message_formatter import format_message
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 20

def run():
    # avoid circular import

    ctl = Rcon(
        SERVER_INFO
    )

    config = AutoBroadcasts()

    while True: 
        msgs = config.get_messages()

        if not config.get_enabled() or not msgs:
            logger.debug("Auto broadcasts are disabled. Sleeping %s seconds", CHECK_INTERVAL)
            time.sleep(CHECK_INTERVAL)
            continue
     
        if config.get_randomize():
            logger.debug("Auto broadcasts. Radomizing")
            random.shuffle(msgs)

        for time_sec, msg in msgs:
            start_time = time.time_ns()
            formatted = format_message(ctl, msg)
            logger.debug("Broadcasting for %s seconds: %s", time_sec, formatted)
            ctl.set_broadcast(formatted) 
            end_time = time.time_ns()
            time.sleep(int(time_sec) - (end_time - start_time) / (10 ** 9) ) 



if __name__ == "__main__":
    run()

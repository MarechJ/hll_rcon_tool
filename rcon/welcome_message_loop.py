import time
import logging
from threading import Thread

from rcon.commands import HLLServerError
from rcon.settings import SERVER_INFO
from rcon.user_config import WelcomeMessage
from rcon.message_formatter import format_message
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)

def publish_welcome_message(rcon, welcome_func):
    welcome_message = format_message(rcon, welcome_func())
    logger.debug("Setting welcome message %s", welcome_message)
    if welcome_message is not None and len(welcome_message) > 0:
        rcon.set_welcome_message(welcome_message)

class OnMapChange(Thread):
    def __init__(self, rcon, welcome_func):
        super().__init__()
        self.rcon = rcon
        self.running = False
        self.started = False
        self.welcome_func = welcome_func

    def run(self):
        self.started = True
        self.running = True
        cached_map = None
        sleep_time = 10
        while True:
            if not self.running:
                time.sleep(10)
            start_time = time.time_ns()
            try:
                current_map = self.rcon.get_map()
                if cached_map != current_map:
                    publish_welcome_message(self.rcon, self.welcome_func)
                    cached_map = current_map
                else:
                    logger.info("No map change detected")
            except:
                logger.warning("Failed to set welcome message on map change, will retry in %s seconds", sleep_time)

            end_time = time.time_ns()
            time.sleep(sleep_time - (end_time - start_time) / (10 ** 9) ) 


class OnInterval(Thread):
    def __init__(self, rcon, welcome_func):
        super().__init__()
        self.rcon = rcon
        self.interval = None
        self.running = False
        self.started = False
        self.welcome_func = welcome_func

    def run(self):
        self.started = True
        self.running = True
        if self.interval is None:
            logger.exception("OnInterval thread was started without configuring interval")
            return
        while True:
            if not self.running:
                time.sleep(10)
                continue
            start_time = time.time_ns()
            
            try:
                publish_welcome_message(self.rcon, self.welcome_func)
            except:
                logger.warning("Failed to set welcome message on interval, will retry in %s seconds", self.interval)

            end_time = time.time_ns()
            time.sleep(self.interval - (end_time - start_time) / (10 ** 9) ) 


def run():
    rcon = Rcon(
        SERVER_INFO
    )

    config = WelcomeMessage()

    welcome_func = lambda: config.get_welcome()

    on_map_change_thread = OnMapChange(rcon, welcome_func)
    on_interval_thread = OnInterval(rcon, welcome_func)

    while True:
        start_time = time.time_ns()
        sleep_time = 10
        on_map_change = config.get_on_map_change()
        on_interval_switch = config.get_on_interval_switch()
        on_interval_period = int(config.get_on_interval_period())
        on_interval_unit = config.get_on_interval_unit()

        interval_period_mod = 1
        if on_interval_unit == "minutes":
            interval_period_mod = 60
        elif on_interval_unit == "hours":
            interval_period_mod = 3600

        interval = on_interval_period * interval_period_mod

        if on_map_change:
            if not on_map_change_thread.started:
                on_map_change_thread.start()
            elif not on_map_change_thread.running:
                on_map_change_thread.running = True
        else:
            on_map_change_thread.running = False

        if on_interval_switch:
            on_interval_thread.interval = interval
            if not on_interval_thread.started:
                on_interval_thread.start()
            elif not on_interval_thread.running:
                on_interval_thread.running = True
        elif not on_interval_switch:
            on_interval_thread.running = False

        end_time = time.time_ns()
        time.sleep(sleep_time - (end_time - start_time) / (10**9))

        
if __name__ == "__main__":
    run()

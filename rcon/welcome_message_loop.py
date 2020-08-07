import time
import logging
from threading import Thread

from rcon.settings import SERVER_INFO
from rcon.user_config import WelcomeMessage
from rcon.message_formatter import format_message
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)

def publish_welcome_message(rcon, welcome_func):
    welcome_message = format_message(rcon, welcome_func())
    rcon.set_welcome_message(welcome_message)

class OnMapChange(Thread):
    def __init__(self, rcon, welcome_func):
        super().__init__()
        self.rcon = rcon
        self.running = False
        self.welcome_func = welcome_func

    def run(self):
        self.running = True
        cached_map = None
        while self.running:
            start_time = time.time_ns()
            current_map = self.rcon.get_map()
            if cached_map is not current_map:
                cached_map = current_map

            publish_welcome_message(self.rcon, self.welcome_func)

            end_time = time.time_ns()
            time.sleep(int(10) - (end_time - start_time) / (10 ** 9) ) 


class OnInterval(Thread):
    def __init__(self, rcon, interval, welcome_func):
        super().__init__()
        self.rcon = rcon
        self.interval = int(interval)
        self.running = False
        self.welcome_func = welcome_func

    def run(self):
        self.running = True
        while self.running:
            start_time = time.time_ns()
            
            publish_welcome_message(self.rcon, self.welcome_func)

            end_time = time.time_ns()
            time.sleep(self.interval - (end_time - start_time) / (10 ** 9) ) 


def run():
    rcon = Rcon(
        SERVER_INFO
    )

    config = WelcomeMessage()

    while True:
        start_time = time.time_ns()
        sleep_time = 60
        on_map_change = config.get_on_map_change()
        on_interval_switch = config.get_on_interval_switch()
        on_interval_period = int(config.get_on_interval_period())
        on_interval_unit = config.get_on_interval_unit()
        welcome_func = lambda: config.get_welcome()

        interval_period_mod = 1
        if on_interval_unit == "minutes":
            interval_period_mod = 60
        elif on_interval_unit == "hours":
            interval_period_mod = 3600

        interval = on_interval_period * interval_period_mod

        on_map_change_thread = OnMapChange(rcon, welcome_func)
        if not on_map_change_thread.running:
            if on_map_change:
                on_map_change_thread.start()
        elif not on_map_change:
            on_map_change_thread.running = False

        on_interval_thread = OnInterval(rcon, interval, welcome_func)
        if not on_interval_thread.running:
            if on_interval_switch:
                on_interval_thread.start()
        elif not on_interval_switch:
            on_interval_thread.running = False

        end_time = time.time_ns()
        time.sleep(sleep_time - (end_time - start_time) / (10**9))

        
if __name__ == "__main__":
    run()

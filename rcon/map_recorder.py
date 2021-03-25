import time
from datetime import datetime, timedelta
import logging
from threading import Thread
import os
import redis

from rcon.discord import send_to_discord_audit, dict_to_discord
from rcon.recorded_commands import RecordedRcon
from rcon.extended_commands import CommandFailedError
from rcon.utils import (
    categorize_maps,
    numbered_maps,
    FixedLenList,
    map_name,
    get_current_selection, 
    get_map_side,
    MapsHistory,
    ALL_MAPS
)
from rcon.cache_utils import get_redis_pool


logger = logging.getLogger(__name__)


class MapsRecorder:
    def __init__(self, rcon: RecordedRcon):
        self.rcon = rcon
        self.red = redis.Redis(connection_pool=get_redis_pool())
        self.maps_history = MapsHistory()
        self.prev_map = None
        self._restore_state()

    def _restore_state(self):
        current_map = self.rcon.get_map()
        try:
            last = self.maps_history[0]
        except IndexError:
            logger.warning("Map history is empty, can't restore state")
            return

        started_time = datetime.fromtimestamp(last.get("start"))
        elapsed_time = datetime.now() - started_time

        if last.get("name") == current_map and elapsed_time < timedelta(hours=2):
            logging.info("State recovered successfully")
            self.prev_map = current_map
        else:
            logging.warning("The map recorder was offline for too long, the maps history will have gaps")


    def detect_map_change(self):
        try:
            current_map = self.rcon.get_map()
        except CommandFailedError:
            logger.info("Faied to get current map. Skipping")
            return 
        #logger.debug("Checking for map change current: %s prev: %s", current_map, self.prev_map)
        if self.prev_map != current_map:
            if self.prev_map and self.prev_map.replace('_RESTART', '') in ALL_MAPS:
                self.maps_history.save_map_end(self.prev_map.replace('_RESTART', ''))
            if current_map and current_map.replace('_RESTART', '') in ALL_MAPS:
                self.maps_history.save_new_map(current_map.replace('_RESTART', ''))
            logger.info(
                "Map change detected updating state. Prev map %s New Map %s",
                self.prev_map,
                current_map,
            )
            if not os.getenv('SILENT_MAP_RECORDER', None):
                send_to_discord_audit(f"map change detected {dict_to_discord(dict(previous=self.prev_map, new=current_map))}", by="MAP_RECORDER", silent=False)
            self.prev_map = current_map
            self.last_map_change_time = datetime.now()
            return True

        return False


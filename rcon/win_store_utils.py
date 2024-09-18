import re
from logging import getLogger
from typing import Final
from rcon.steam_utils import is_steam_id_64

logger = getLogger(__name__)

def is_windows_store_id(player_id: str) -> bool:
    return not is_steam_id_64(player_id=player_id)
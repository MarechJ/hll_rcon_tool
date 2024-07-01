import re
from logging import getLogger
from typing import Final

logger = getLogger(__name__)

WIN_STORE_PLAYER_ID_REGEX: Final = (
    "^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)
win_store_regexp = re.compile(WIN_STORE_PLAYER_ID_REGEX)


def is_windows_store_id(player_id: str) -> bool:
    if win_store_regexp.match(player_id):
        return True
    return False

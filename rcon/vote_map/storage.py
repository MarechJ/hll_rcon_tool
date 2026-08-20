"""Redis storage contract shared by votemap runtime code and migrations."""

from typing import Final


VOTEMAP_SCHEMA_VERSION: Final = 1


class VotemapKeys:
    VERSION: Final = "votemap:version"
    LATEST_REMINDER: Final = "votemap:reminder"
    MAP_WHITELIST: Final = "votemap:whitelist"
    MAP_SELECTION: Final = "votemap:selection"
    VOTES: Final = "votemap:votes"
    ADMIN_NEXT_MAP: Final = "votemap:admin-next-map"
    PLAYER_CHOICE: Final = "votemap:player-choice"
    NEXT_MAP: Final = "votemap:next-map"
    RESULT_HISTORY: Final = "votemap:result-history"

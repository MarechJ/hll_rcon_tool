"""Helpers for classifying player IDs used by HLL gameservers."""

import re

from rcon.steam_utils import is_steam_id_64

NETWORK_PLAYER_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{32}$")


def is_network_player_id(player_id: str) -> bool:
    """Return whether an ID is a 32-character gameserver network ID."""
    return bool(
        isinstance(player_id, str) and NETWORK_PLAYER_ID_PATTERN.fullmatch(player_id)
    )


def is_supported_player_id(player_id: str) -> bool:
    """Return whether an ID can be used for a new VIP record."""
    return bool(
        isinstance(player_id, str)
        and (is_steam_id_64(player_id) or is_network_player_id(player_id))
    )

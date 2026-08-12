from __future__ import annotations

from enum import Enum

from rcon.game.base import GameProfile
from rcon.game.hll.profile import HLL_PROFILE
from rcon.game.hllv.profile import HLLV_PROFILE

GAME_PROFILES: dict[str, GameProfile] = {
    HLL_PROFILE.key: HLL_PROFILE,
    HLLV_PROFILE.key: HLLV_PROFILE,
}


def get_game_profile(game: str | Enum | None) -> GameProfile:
    """Return the profile for a ServerInfo game value.

    Accepting both strings and enums keeps this module independent from
    ``rcon.types`` and avoids coupling the game data back to API response types.
    """

    key = getattr(game, "value", game) or HLL_PROFILE.key
    try:
        return GAME_PROFILES[str(key)]
    except KeyError as exc:
        supported = ", ".join(sorted(GAME_PROFILES))
        raise ValueError(f"Unknown game {key!r}; expected one of: {supported}") from exc

from __future__ import annotations

import os
from typing import TypeVar, assert_never

from rcon.game.base import GameProfile
from rcon.game.hll.profile import HLL_PROFILE
from rcon.game.hllv.profile import HLLV_PROFILE
from rcon.types import GameEnum, GameIntEnum

T = TypeVar("T")

GAME_PROFILES: dict[GameEnum, GameProfile] = {
    profile.game: profile for profile in (HLL_PROFILE, HLLV_PROFILE)
}

try:
    GAME_ID = GameEnum(os.getenv("HLL_GAME", "hll")).to_int()
except:
    GAME_ID = GameEnum.HLL_WW2.to_int()

def get_game_profile(game: str | GameEnum | None) -> GameProfile:
    """Return the profile for a ServerInfo game value.

    Accepting both strings and enums keeps this module independent from
    ``rcon.types`` and avoids coupling the game data back to API response types.
    """
    supported = ", ".join(sorted(GAME_PROFILES))

    if game is None:
        raise ValueError("No game specified; expected one of: " + supported)

    try:
        game = GameEnum(game)
    except NameError:
        raise ValueError(f"Unknown game {game!r}; expected one of: {supported}")
    
    profile = GAME_PROFILES.get(game)
    if profile is None:
        raise ValueError(f"No profile is known for {game!r}; expected one of: {supported}")

    return profile

def game_switch(game: GameEnum, hll_value: T, hllv_value: T) -> T:
    """Return the appropriate value for the given game."""
    match game:
        case GameEnum.HLL_WW2:
            return hll_value
        case GameEnum.HLL_VIETNAM:
            return hllv_value
        case _:
            assert_never(game)

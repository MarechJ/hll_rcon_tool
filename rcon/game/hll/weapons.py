"""HLL/WW2 weapon catalog compatibility exports."""

from rcon.weapons import ALL_WEAPONS, WEAPON_SIDE_MAP

HLL_WEAPONS = ALL_WEAPONS
HLL_WEAPON_SIDES = WEAPON_SIDE_MAP

__all__ = ["HLL_WEAPONS", "HLL_WEAPON_SIDES"]

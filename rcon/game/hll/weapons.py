"""HLL/WW2 weapon catalog compatibility exports."""

import hllrcon

from rcon.weapons import ALL_WEAPONS, WEAPON_SIDE_MAP

HLL_WEAPON_IDS = frozenset(
    {*ALL_WEAPONS, *(weapon.id for weapon in hllrcon.HLLWeapon.all())}
)
HLL_WEAPONS = ALL_WEAPONS
HLL_WEAPON_SIDES = WEAPON_SIDE_MAP

__all__ = ["HLL_WEAPON_IDS", "HLL_WEAPONS", "HLL_WEAPON_SIDES"]

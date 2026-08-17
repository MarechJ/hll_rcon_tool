"""HLL Vietnam raw weapon classifications and team associations."""

import hllrcon

from rcon.maps import Team
from rcon.weapons import WeaponType

HLLV_WEAPON_IDS = frozenset(weapon.id for weapon in hllrcon.HLLVWeapon.all())
HLLV_WEAPONS: dict[str, WeaponType] = {}
HLLV_WEAPON_SIDES: dict[str, Team] = {}

__all__ = ["HLLV_WEAPON_IDS", "HLLV_WEAPONS", "HLLV_WEAPON_SIDES"]

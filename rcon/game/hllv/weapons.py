"""HLL Vietnam raw weapon classifications and team associations."""

from rcon.maps import Team
from rcon.weapons import WeaponType

HLLV_WEAPONS: dict[str, WeaponType] = {}
HLLV_WEAPON_SIDES: dict[str, Team] = {}

__all__ = ["HLLV_WEAPONS", "HLLV_WEAPON_SIDES"]

from rcon.game.base import GameProfile
from rcon.game.hllv.maps import HLLV_LAYERS, HLLV_MAPS, parse_layer
from rcon.game.hllv.roles import HLLV_ROLE_LABELS, HLLV_ROLES
from rcon.game.hllv.weapons import HLLV_WEAPON_SIDES, HLLV_WEAPONS
from rcon.maps import GameMode

HLLV_PROFILE = GameProfile(
    key="hllv",
    maps=HLLV_MAPS,
    layers=HLLV_LAYERS,
    layer_parser=parse_layer,
    roles=HLLV_ROLES,
    role_labels=HLLV_ROLE_LABELS,
    weapons=HLLV_WEAPONS,
    weapon_sides=HLLV_WEAPON_SIDES,
    supported_game_modes=frozenset(
        {
            GameMode.WARFARE,
            GameMode.OFFENSIVE,
            GameMode.CONQUEST,
            GameMode.DOMINATION,
        }
    ),
)

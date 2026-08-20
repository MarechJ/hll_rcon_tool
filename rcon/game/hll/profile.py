from rcon.game.base import GameProfile
from rcon.game.hll.maps import HLL_LAYERS, HLL_MAPS, parse_layer
from rcon.game.hll.roles import HLL_ROLE_IDS, HLL_ROLE_LABELS, HLL_ROLES
from rcon.game.hll.weapons import HLL_WEAPON_IDS, HLL_WEAPON_SIDES, HLL_WEAPONS
from rcon.maps import GameMode
from rcon.types import GameEnum

HLL_PROFILE = GameProfile(
    game=GameEnum.HLL_WW2,
    maps=HLL_MAPS,
    layers=HLL_LAYERS,
    layer_parser=parse_layer,
    roles=HLL_ROLES,
    role_labels=HLL_ROLE_LABELS,
    role_ids=HLL_ROLE_IDS,
    weapons=HLL_WEAPONS,
    weapon_ids=HLL_WEAPON_IDS,
    weapon_sides=HLL_WEAPON_SIDES,
    supported_game_modes=frozenset(
        {
            GameMode.WARFARE,
            GameMode.OFFENSIVE,
            GameMode.CONQUEST,
            GameMode.SKIRMISH,
            GameMode.PHASED,
            GameMode.MAJORITY,
        }
    ),
)

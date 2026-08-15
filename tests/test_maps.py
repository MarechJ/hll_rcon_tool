import os
from logging import getLogger
from pathlib import Path

import pytest

from rcon.maps import (
    LAYERS,
    MAPS,
    UNKNOWN_MAP_NAME,
    Environment,
    GameMode,
    Layer,
    Team,
    get_opposite_side,
    get_theoretical_match_time,
    is_server_loading_map,
    numbered_maps,
    parse_layer,
    parse_map_string,
    parse_map_string_attacker,
    _parse_legacy_layer,
)

logger = getLogger(__name__)


@pytest.mark.parametrize(
    ("game_mode", "server_match_time", "expected"),
    (
        (GameMode.OFFENSIVE, 10 * 60, 50 * 60),
        (GameMode.OFFENSIVE, 30 * 60, 5 * 30 * 60),
        (GameMode.OFFENSIVE, 60 * 60, 5 * 60 * 60),
        # The server incorrectly reports Warfare's default when the Offensive
        # timer has not been customized.
        (GameMode.OFFENSIVE, 90 * 60, 5 * 30 * 60),
        (GameMode.WARFARE, 90 * 60, 90 * 60),
        (GameMode.SKIRMISH, 30 * 60, 30 * 60),
    ),
)
def test_get_theoretical_match_time(game_mode, server_match_time, expected):
    assert get_theoretical_match_time(game_mode, server_match_time) == expected


@pytest.mark.parametrize(
    ("log_line", "expected"),
    (
        (
            "MATCH START CAM RANH PORT NVA OFFENSIVE",
            ("CAM RANH PORT", None, GameMode.OFFENSIVE),
        ),
        (
            "MATCH START CAM RANH PORT DAY US OFFENSIVE",
            ("CAM RANH PORT", Environment.DAY, GameMode.OFFENSIVE),
        ),
        (
            "MATCH ENDED `CAM RANH PORT USA OFFENSIVE` SOUTH (5 - 0) NORTH",
            ("CAM RANH PORT", None, GameMode.OFFENSIVE),
        ),
        (
            "MATCH START CAM RANH PORT DOMINATION",
            ("CAM RANH PORT", None, GameMode.DOMINATION),
        ),
        (
            "MATCH START THANH HÒA BRIDGE NVA Offensive",
            ("THANH HÒA BRIDGE", None, GameMode.OFFENSIVE),
        ),
    ),
)
def test_parse_map_string_accepts_optional_attacker_before_mode(log_line, expected):
    assert parse_map_string(log_line) == expected


@pytest.mark.parametrize(
    ("attacker", "expected"),
    (("NVA", Team.AXIS), ("US", Team.ALLIES), ("USA", Team.ALLIES)),
)
def test_parse_map_string_attacker_uses_logical_sides(attacker, expected):
    assert (
        parse_map_string_attacker(
            f"MATCH START THANH HÒA BRIDGE {attacker} OFFENSIVE"
        )
        is expected
    )

MOR_WARFARE_DAY = Layer(
    id="mortain_warfare_day", map=MAPS["mortain"], game_mode=GameMode.WARFARE
)

MOR_WARFARE_OVERCAST = Layer(
    id="mortain_warfare_overcast",
    map=MAPS["mortain"],
    game_mode=GameMode.WARFARE,
    environment=Environment.OVERCAST,
)

MOR_US_OFFENSIVE_DAY = Layer(
    id="mortain_offensiveUS_day",
    map=MAPS["mortain"],
    game_mode=GameMode.OFFENSIVE,
    attackers=Team.ALLIES,
)

MOR_US_OFFENSIVE_OVERCAST = Layer(
    id="mortain_offensiveUS_overcast",
    map=MAPS["mortain"],
    game_mode=GameMode.OFFENSIVE,
    attackers=Team.ALLIES,
)

MOR_GER_OFFENSIVE_DAY = Layer(
    id="mortain_offensiveger_day",
    map=MAPS["mortain"],
    game_mode=GameMode.OFFENSIVE,
    attackers=Team.AXIS,
)

MOR_GER_OFFENSIVE_OVERCAST = Layer(
    id="mortain_offensiveger_overcast",
    map=MAPS["mortain"],
    game_mode=GameMode.OFFENSIVE,
    attackers=Team.AXIS,
    environment=Environment.OVERCAST,
)

MOR_CONTROL_DAY = Layer(
    id="mortain_skirmish_day",
    map=MAPS["mortain"],
    game_mode=GameMode.SKIRMISH,
)
MOR_CONTROL_OVERCAST = Layer(
    id="mortain_skirmish_overcast",
    map=MAPS["mortain"],
    game_mode=GameMode.SKIRMISH,
    environment=Environment.OVERCAST,
)


SMDM_WARFARE = Layer(
    id="stmariedumont_warfare",
    map=MAPS["stmariedumont"],
    game_mode=GameMode.WARFARE,
)

SMDM_WARFARE_NIGHT = Layer(
    id="stmariedumont_warfare_night",
    map=MAPS["stmariedumont"],
    game_mode=GameMode.WARFARE,
    environment=Environment.NIGHT,
)

SME_WARFARE = Layer(
    id="stmereeglise_warfare",
    map=MAPS["stmereeglise"],
    game_mode=GameMode.WARFARE,
)

SMDM_SKIRMISH_DAY = Layer(
    id="SMDM_S_1944_Day_P_Skirmish",
    map=MAPS["stmariedumont"],
    game_mode=GameMode.SKIRMISH,
)

SMDM_SKIRMISH_NIGHT = Layer(
    id="SMDM_S_1944_Night_P_Skirmish",
    map=MAPS["stmariedumont"],
    game_mode=GameMode.SKIRMISH,
    environment=Environment.NIGHT,
)

SMDM_SKIRMISH_RAIN = Layer(
    id="SMDM_S_1944_Rain_P_Skirmish",
    map=MAPS["stmariedumont"],
    game_mode=GameMode.SKIRMISH,
    environment=Environment.RAIN,
)

UNKNOWN_MAP = LAYERS[UNKNOWN_MAP_NAME]


@pytest.mark.parametrize(
    "maps, expected",
    [
        ([SMDM_WARFARE, SME_WARFARE], {"0": SMDM_WARFARE, "1": SME_WARFARE}),
    ],
)
def test_numbered_maps(maps, expected):
    assert numbered_maps(maps=maps) == expected


@pytest.mark.parametrize(
    "layer_name, expected",
    [
        ("unknown", UNKNOWN_MAP),
        ("Untitled_46", UNKNOWN_MAP),
        ("mortain_warfare_day", MOR_WARFARE_DAY),
        ("mortain_warfare_overcast", MOR_WARFARE_OVERCAST),
        ("mortain_offensiveUS_day", MOR_US_OFFENSIVE_DAY),
        ("mortain_offensiveUS_overcast", MOR_US_OFFENSIVE_OVERCAST),
        ("mortain_offensiveger_day", MOR_GER_OFFENSIVE_DAY),
        ("mortain_offensiveger_overcast", MOR_GER_OFFENSIVE_OVERCAST),
        ("mortain_skirmish_day", MOR_CONTROL_DAY),
        ("mortain_skirmish_overcast", MOR_CONTROL_OVERCAST),
        ("stmariedumont_warfare_night", SMDM_WARFARE_NIGHT),
        ("SMDM_S_1944_Day_P_Skirmish", SMDM_SKIRMISH_DAY),
        ("SMDM_S_1944_Night_P_Skirmish", SMDM_SKIRMISH_NIGHT),
        ("SMDM_S_1944_Rain_P_Skirmish", SMDM_SKIRMISH_RAIN),
    ],
)
def test_parse_layer(layer_name, expected):
    assert parse_layer(layer_name=layer_name) == expected

@pytest.mark.parametrize(
    "layer_name, expected",
    [
        (
            "elalamein_offensive_CW",
            Layer(
                id="elalamein_offensive_CW",
                map=MAPS["elalamein"],
                game_mode=GameMode.OFFENSIVE,
                attackers=Team.ALLIES,
            ),
        ),
        (
            "hill400_offensive_US",
            Layer(
                id="hill400_offensive_US",
                map=MAPS["hill400"],
                game_mode=GameMode.OFFENSIVE,
                attackers=Team.ALLIES,
            ),
        ),
        (
            "hill400_offensive_us",
            Layer(
                id="hill400_offensive_us",
                map=MAPS["hill400"],
                game_mode=GameMode.OFFENSIVE,
                attackers=Team.ALLIES,
            ),
        ),
    ],
)
def test_parse_legacy_layer(layer_name, expected):
    assert _parse_legacy_layer(layer_name) == expected


@pytest.mark.parametrize(
    "map_name, expected", [("Untitled_46", True), ("carentan_warfare", False)]
)
def test_is_server_loading_map(map_name, expected):
    assert is_server_loading_map(map_name=map_name) == expected


def test_all_map_images_exist():
    ALL_MAP_IMAGES = [f for f in os.listdir(Path("./assets/images/maps"))]
    ALL_MAP_ICONS = [f for f in os.listdir(Path("./assets/images/maps/icons"))]

    for l in LAYERS.values():
        assert l.image_name in ALL_MAP_IMAGES
        assert l.image_name in ALL_MAP_ICONS

@pytest.mark.parametrize(
    "team, expected",
    [
        (Team.ALLIES, Team.AXIS),
        (Team.AXIS, Team.ALLIES),
    ],
)
def test_get_opposite_side(team, expected):
    assert get_opposite_side(team) == expected

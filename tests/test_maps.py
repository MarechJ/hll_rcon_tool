import pytest

from rcon.maps import (
    LAYERS,
    MAPS,
    UNKNOWN_MAP_NAME,
    Environment,
    Gamemode,
    Layer,
    Team,
    is_server_loading_map,
    numbered_maps,
    parse_layer,
)

MOR_WARFARE_DAY = Layer(
    id="mortain_warfare_day", map=MAPS["mortain"], gamemode=Gamemode.WARFARE
)

MOR_WARFARE_OVERCAST = Layer(
    id="mortain_warfare_overcast",
    map=MAPS["mortain"],
    gamemode=Gamemode.WARFARE,
    environment=Environment.OVERCAST,
)

MOR_US_OFFENSIVE_DAY = Layer(
    id="mortain_offensiveUS_day",
    map=MAPS["mortain"],
    gamemode=Gamemode.OFFENSIVE,
    attackers=Team.ALLIES,
)

MOR_US_OFFENSIVE_OVERCAST = Layer(
    id="mortain_offensiveUS_overcast",
    map=MAPS["mortain"],
    gamemode=Gamemode.OFFENSIVE,
    attackers=Team.ALLIES,
)

MOR_GER_OFFENSIVE_DAY = Layer(
    id="mortain_offensiveger_day",
    map=MAPS["mortain"],
    gamemode=Gamemode.OFFENSIVE,
    attackers=Team.AXIS,
)

MOR_GER_OFFENSIVE_OVERCAST = Layer(
    id="mortain_offensiveger_overcast",
    map=MAPS["mortain"],
    gamemode=Gamemode.OFFENSIVE,
    attackers=Team.AXIS,
    environment=Environment.OVERCAST,
)

MOR_CONTROL_DAY = Layer(
    id="mortain_skirmish_day",
    map=MAPS["mortain"],
    gamemode=Gamemode.CONTROL,
)
MOR_CONTROL_OVERCAST = Layer(
    id="mortain_skirmish_overcast",
    map=MAPS["mortain"],
    gamemode=Gamemode.CONTROL,
    environment=Environment.OVERCAST,
)


SMDM_WARFARE = Layer(
    id="stmariedumont_warfare",
    map=MAPS["stmariedumont"],
    gamemode=Gamemode.WARFARE,
)

SMDM_WARFARE_NIGHT = Layer(
    id="stmariedumont_warfare_night",
    map=MAPS["stmariedumont"],
    gamemode=Gamemode.WARFARE,
    environment=Environment.NIGHT,
)

SME_WARFARE = Layer(
    id="stmereeglise_warfare",
    map=MAPS["stmereeglise"],
    gamemode=Gamemode.WARFARE,
)

SMDM_SKIRMISH_DAY = Layer(
    id="SMDM_S_1944_Day_P_Skirmish",
    map=MAPS["stmariedumont"],
    gamemode=Gamemode.CONTROL,
)

SMDM_SKIRMISH_NIGHT = Layer(
    id="SMDM_S_1944_Night_P_Skirmish",
    map=MAPS["stmariedumont"],
    gamemode=Gamemode.CONTROL,
    environment=Environment.NIGHT,
)

SMDM_SKIRMISH_RAIN = Layer(
    id="SMDM_S_1944_Rain_P_Skirmish",
    map=MAPS["stmariedumont"],
    gamemode=Gamemode.CONTROL,
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
    "map_name, expected", [("Untitled_46", True), ("carentan_warfare", False)]
)
def test_is_server_loading_map(map_name, expected):
    assert is_server_loading_map(map_name=map_name) == expected

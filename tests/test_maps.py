import pytest

from rcon.maps import (
    MAPS,
    UNKNOWN_MAP_NAME,
    Gamemode,
    Layer,
    numbered_maps,
    parse_layer,
)

SMDM_WARFARE = Layer(
    id="stmariedumont_warfare",
    map=MAPS["stmariedumont"],
    gamemode=Gamemode.WARFARE,
)

SME_WARFARE = Layer(
    id="stmereeglise_warfare",
    map=MAPS["stmereeglise"],
    gamemode=Gamemode.WARFARE,
)


@pytest.mark.parametrize(
    "maps, expected",
    [
        ([SMDM_WARFARE, SME_WARFARE], {"0": SMDM_WARFARE, "1": SME_WARFARE}),
    ],
)
def test_numbered_maps(maps, expected):
    assert numbered_maps(maps=maps) == expected


def test_parse_layer():
    assert parse_layer(layer_name="unknown").id == UNKNOWN_MAP_NAME

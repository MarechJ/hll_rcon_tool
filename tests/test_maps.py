import pytest
from rcon.maps import Layer, MAPS, Gamemode, numbered_maps

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

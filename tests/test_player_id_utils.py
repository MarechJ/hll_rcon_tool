import pytest

from rcon.player_id_utils import (
    is_network_player_id,
    is_supported_player_id,
)


@pytest.mark.parametrize(
    ("player_id", "expected"),
    [
        pytest.param(
            "00025182eb1149fabc454d25847b690e",
            True,
            id="hllv-eos-lowercase",
        ),
        pytest.param(
            "ABCDEF0123456789ABCDEF0123456789",
            True,
            id="network-uppercase",
        ),
        pytest.param(
            "00025182eb1149fabc454d25847b690",
            False,
            id="network-too-short",
        ),
        pytest.param(
            "00025182eb1149fabc454d25847b690eg",
            False,
            id="network-invalid-character",
        ),
        pytest.param("", False, id="empty"),
        pytest.param(
            "88d99bf432e8de4f58c43d1c2d22",
            False,
            id="legacy-28-character-id",
        ),
    ],
)
def test_is_network_player_id(player_id, expected):
    assert is_network_player_id(player_id) is expected


@pytest.mark.parametrize(
    ("player_id", "expected"),
    [
        pytest.param("76561198080212634", True, id="hll-steam64"),
        pytest.param(
            "00025182eb1149fabc454d25847b690e",
            True,
            id="hllv-network-id",
        ),
        pytest.param("", False, id="empty"),
        pytest.param("player-id", False, id="arbitrary-text"),
        pytest.param("7656119808021263", False, id="steam64-too-short"),
        pytest.param(
            "88d99bf432e8de4f58c43d1c2d22",
            False,
            id="legacy-28-character-id",
        ),
    ],
)
def test_is_supported_player_id(player_id, expected):
    assert is_supported_player_id(player_id) is expected

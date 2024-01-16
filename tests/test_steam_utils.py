import pytest

from rcon.steam_utils import is_steam_id_64


@pytest.mark.parametrize(
    "id_, expected",
    [
        ("1", False),
        ("", False),
        ("a21af8b5-59df-5vbr-88gf-ab4239r4g6f4", False),
        ("76561198080212634", True),
    ],
)
def test_is_steam_id_64(id_, expected):
    assert is_steam_id_64(id_) == expected

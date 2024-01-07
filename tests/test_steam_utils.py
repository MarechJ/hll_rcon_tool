import pytest

from rcon.steam_utils import filter_steam_id, filter_steam_ids, is_steam_id_64


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


@filter_steam_id()
def should_filter_single_id_without_parameter_name(steamd_id: str):
    return steamd_id


@filter_steam_ids()
def should_filter_multiple_ids_without_parameter_name(steamd_ids: list[str]):
    return steamd_ids


@pytest.mark.parametrize(
    "steamd_id, expected",
    [
        ("76561198080212634", "76561198080212634"),
        ("a21af8b5-59df-5vbr-88gf-ab4239r4g6f4", None),
    ],
)
def test_steam_id_filter(steamd_id, expected):
    assert should_filter_single_id_without_parameter_name(steamd_id) == expected


@pytest.mark.parametrize(
    "steamd_ids, expected",
    [
        (["76561198080212634"], ["76561198080212634"]),
        ([], []),
        (
            ["76561198080212634", "a21af8b5-59df-5vbr-88gf-ab4239r4g6f4"],
            ["76561198080212634"],
        ),
    ],
)
def test_steam_ids_filter(steamd_ids, expected):
    assert should_filter_multiple_ids_without_parameter_name(steamd_ids) == expected

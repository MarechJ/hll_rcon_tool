import pytest

from rcon.commands import convert_tabs_to_spaces
from rcon.types import GetDetailedPlayer
from rcon.utils import (
    exception_in_chain,
    is_invalid_name_pineapple,
    is_invalid_name_whitespace,
    parse_raw_player_info,
)


class TestException(Exception):
    pass


class ChainedException(Exception):
    pass


class DeepChainedException(Exception):
    pass


def test_direct_exception():
    assert exception_in_chain(TestException(), TestException)


def test_no_match():
    assert exception_in_chain(ValueError(), TestException) is False


def test_explicit_chained():
    e = ValueError()
    e.__cause__ = TestException()

    assert exception_in_chain(e, TestException)


def test_implicit_chained():
    e = ValueError()
    e.__context__ = TestException()

    assert exception_in_chain(e, TestException)


def test_deeply_chained_explicit():
    e = ValueError()
    e.__cause__ = TestException()
    e.__cause__.__context__ = ChainedException()
    e.__cause__.__context__.__cause__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)


def test_deeply_chained_implicit():
    e = ValueError()
    e.__context__ = TestException()
    e.__context__.__cause__ = ChainedException()
    e.__context__.__cause__.__context__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("some\tcontaining\twords", "some containing words"),
        ("", ""),
        ("\t", " "),
        ("no tabs", "no tabs"),
    ],
)
def test_convert_tabs_to_spaces(value, expected):
    assert convert_tabs_to_spaces(value) == expected


@pytest.mark.parametrize(
    "name, expected",
    [("1234567890", False), ("1234567890 ", True), ("1234567890123456789 ", True)],
)
def test_is_invalid_name_whitespace(name, expected):
    assert is_invalid_name_whitespace(name) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("12345678901234567890", False),
        ("123456789012345?", False),
        ("1234567890123456789?", True),
    ],
)
def test_is_invalid_name_pineapple(name, expected):
    assert is_invalid_name_pineapple(name) == expected


def mock_get_detailed_player(
    name="",
    player_id="0",
    team="",
    role="",
    unit_id=0,
    unit_name="",
    loadout="",
    kills=0,
    deaths=0,
    combat=0,
    defense=0,
    offense=0,
    support=0,
    level=1,
    is_vip=False,
    profile=None,
) -> GetDetailedPlayer:
    return {
        "name": name,
        "player_id": player_id,
        "team": team,
        "role": role,
        "unit_id": unit_id,
        "unit_name": unit_name,
        "combat": combat,
        "deaths": deaths,
        "kills": kills,
        "defense": defense,
        "level": level,
        "loadout": loadout,
        "offense": offense,
        "support": support,
        "is_vip": is_vip,
        "profile": profile,
    }


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            """Name: MasterShake
steamID64: 76561199502921234
Team: Axis
Role: Support
Unit: 9 - JIG
Loadout: Standard Issue
Kills: 11 - Deaths: 9
Score: C 72, O 100, D 220, S 65
Level: 16
""",
            mock_get_detailed_player(
                name="",
                player_id="76561199502921234",
                team="axis",
                role="support",
                unit_id=9,
                unit_name="jig",
                loadout="standard issue",
                kills=11,
                deaths=9,
                combat=72,
                offense=100,
                defense=220,
                support=65,
                level=16,
            ),
        ),
        (
            """Name: MasterShake
steamID64: a21af8b5-59df-5vbr-88gf-ab4239r4g6f4
Team: Axis
Role: Support
Unit: 9 - JIG
Loadout: Standard Issue
Kills: 11 - Deaths: 9
Score: C 72, O 100, D 220, S 65
Level: 16
""",
            mock_get_detailed_player(
                name="",
                player_id="a21af8b5-59df-5vbr-88gf-ab4239r4g6f4",
                team="axis",
                role="support",
                unit_id=9,
                unit_name="jig",
                loadout="standard issue",
                kills=11,
                deaths=9,
                combat=72,
                offense=100,
                defense=220,
                support=65,
                level=16,
            ),
        ),
    ],
)
def test_parse_raw_player_info(raw, expected):
    assert parse_raw_player_info(raw=raw, player="") == expected

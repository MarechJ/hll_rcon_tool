import pytest

from rcon.commands import convert_tabs_to_spaces
from rcon.types import GetDetailedPlayer
from rcon.utils import (
    exception_in_chain,
    parse_raw_player_info,
)


class FakeException(Exception):
    pass


class ChainedException(Exception):
    pass


class DeepChainedException(Exception):
    pass


def test_direct_exception():
    assert exception_in_chain(FakeException(), FakeException)


def test_no_match():
    assert exception_in_chain(ValueError(), FakeException) is False


def test_explicit_chained():
    e = ValueError()
    e.__cause__ = FakeException()

    assert exception_in_chain(e, FakeException)


def test_implicit_chained():
    e = ValueError()
    e.__context__ = FakeException()

    assert exception_in_chain(e, FakeException)


def test_deeply_chained_explicit():
    e = ValueError()
    e.__cause__ = FakeException()
    e.__cause__.__context__ = ChainedException()
    e.__cause__.__context__.__cause__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)


def test_deeply_chained_implicit():
    e = ValueError()
    e.__context__ = FakeException()
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

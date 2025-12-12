import pytest

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


def mock_get_detailed_player(
    name="",
    clan_tag="GH",
    eos_id="",
    platform="steam",
    world_position={},
    player_id="0",
    team="",
    role="",
    unit_id=0,
    unit_name="",
    loadout="",
    kills=0,
    deaths=0,
    team_kills=0,
    vehicle_kills=0,
    vehicles_destroyed=0,
    combat=0,
    defense=0,
    offense=0,
    support=0,
    level=1,
    is_vip=False,
    profile=None,
    map_playtime_seconds=0,
) -> GetDetailedPlayer:
    return {
        "name": name,
        "clan_tag": clan_tag,
        "eos_id": eos_id,
        "platform": platform,
        "world_position": world_position,
        "player_id": player_id,
        "team": team,
        "role": role,
        "unit_id": unit_id,
        "unit_name": unit_name,
        "combat": combat,
        "deaths": deaths,
        "kills": kills,
        "team_kills": team_kills,
        "vehicle_kills": vehicle_kills,
        "vehicles_destroyed": vehicles_destroyed,
        "defense": defense,
        "level": level,
        "loadout": loadout,
        "offense": offense,
        "support": support,
        "is_vip": is_vip,
        "profile": profile,
        "map_playtime_seconds": map_playtime_seconds,
    }


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            {
                "iD": "76561199502921234",
                "team": 0,
                "role": 5,
                "level": "16",
                "loadout": "Standard Issue",
                "name": "MasterShake",
                "platoon": "JIG",
                "scoreData": {
                    "cOMBAT": 72,
                    "offense": 100,
                    "defense": 220,
                    "support": 65,
                },
                "stats": {
                    "teamKills": 1,
                    "vehicleKills": 2,
                    "vehiclesDestroyed": 3,
                    "infantryKills": 11,
                    "deaths": 9,
                },
                "platform": "steam",
                "clanTag": "GH",
                "eosId": "",
                "worldPosition": {},
            },
            mock_get_detailed_player(
                name="MasterShake",
                clan_tag="GH",
                eos_id="",
                platform="steam",
                world_position={},
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
                team_kills=1,
                vehicle_kills=2,
                vehicles_destroyed=3,
            ),
        ),
        (
            {
                "iD": "a21af8b5-59df-5vbr-88gf-ab4239r4g6f4",
                "team": 1,
                "role": 0,
                "level": "16",
                "loadout": "Standard Issue",
                "name": "MasterShake",
                "platoon": "ABLE",
                "scoreData": {
                    "cOMBAT": 72,
                    "offense": 100,
                    "defense": 220,
                    "support": 65,
                },
                "stats": {
                    "teamKills": 1,
                    "vehicleKills": 2,
                    "vehiclesDestroyed": 3,
                    "infantryKills": 11,
                    "deaths": 9,
                },
                "platform": "steam",
                "clanTag": "GH",
                "eosId": "",
                "worldPosition": {},
            },
            mock_get_detailed_player(
                name="MasterShake",
                clan_tag="GH",
                eos_id="",
                platform="steam",
                world_position={},
                player_id="a21af8b5-59df-5vbr-88gf-ab4239r4g6f4",
                team="allies",
                role="rifleman",
                unit_id=0,
                unit_name="able",
                loadout="standard issue",
                kills=11,
                deaths=9,
                combat=72,
                offense=100,
                defense=220,
                support=65,
                level=16,
                team_kills=1,
                vehicle_kills=2,
                vehicles_destroyed=3,
            ),
        ),
    ],
)
def test_parse_raw_player_info(raw, expected):
    assert parse_raw_player_info(raw=raw) == expected

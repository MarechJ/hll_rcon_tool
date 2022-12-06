import time
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

from pytest import fixture

from rcon.config import get_config
from rcon.squad_automod.automod import (
    get_punitions_to_apply,
    should_kick_player,
    should_punish_player,
    should_warn_player,
)
from rcon.squad_automod.models import (
    APlayer,
    ASquad,
    NoLeaderConfig,
    PunishStepState,
    PunitionsToApply,
    SquadCycleOver,
    SquadHasLeader,
    WatchStatus,
)


@fixture
def team_view():
    return {
        "allies": {
            "combat": 1353,
            "commander": {
                "combat": 17,
                "country": "",
                "deaths": 1,
                "defense": 340,
                "is_vip": False,
                "kills": 1,
                "level": 109,
                "loadout": "veteran",
                "name": "Bio",
                "offense": 20,
                "profile": None,
                "role": "armycommander",
                "steam_bans": None,
                "steam_id_64": "76561198192586863",
                "support": 792,
                "team": "allies",
                "unit_id": 0,
                "unit_name": None,
            },
            "count": 46,
            "deaths": 154,
            "defense": 7920,
            "kills": 143,
            "offense": 2520,
            "squads": {
                "able": {
                    "combat": 563,
                    "deaths": 61,
                    "defense": 2740,
                    "has_leader": True,
                    "kills": 53,
                    "offense": 620,
                    "players": [
                        {
                            "combat": 136,
                            "country": "US",
                            "deaths": 14,
                            "defense": 600,
                            "is_vip": False,
                            "kills": 7,
                            "level": 20,
                            "loadout": "standard issue",
                            "name": "xRONINx6",
                            "offense": 100,
                            "profile": None,
                            "role": "antitank",
                            "steam_bans": None,
                            "steam_id_64": "76561198041932445",
                            "steaminfo": None,
                            "support": 1539,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 137,
                            "country": "",
                            "deaths": 12,
                            "defense": 420,
                            "is_vip": False,
                            "kills": 16,
                            "level": 218,
                            "loadout": "standard issue",
                            "name": "-SHAKA-",
                            "offense": 260,
                            "profile": None,
                            "role": "support",
                            "steam_bans": None,
                            "steam_id_64": "76561198033248786",
                            "steaminfo": None,
                            "support": 135,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 68,
                            "country": "",
                            "deaths": 13,
                            "defense": 740,
                            "is_vip": False,
                            "kills": 8,
                            "level": 70,
                            "loadout": "standard issue",
                            "name": "ByteSized",
                            "offense": 80,
                            "profile": None,
                            "role": "officer",
                            "steam_bans": None,
                            "steam_id_64": "76561198109929335",
                            "steaminfo": None,
                            "support": 1992,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 113,
                            "country": "",
                            "deaths": 11,
                            "defense": 360,
                            "is_vip": False,
                            "kills": 13,
                            "level": 70,
                            "loadout": "standard issue",
                            "name": "WarDaddy",
                            "offense": 160,
                            "profile": None,
                            "role": "assault",
                            "steam_bans": None,
                            "steam_id_64": "76561197970119908",
                            "steaminfo": None,
                            "support": 55,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 74,
                            "country": "VA",
                            "deaths": 11,
                            "defense": 380,
                            "is_vip": False,
                            "kills": 9,
                            "level": 16,
                            "loadout": "standard issue",
                            "name": "Space Toker",
                            "offense": 20,
                            "profile": None,
                            "role": "medic",
                            "steam_bans": None,
                            "steam_id_64": "76561198103085637",
                            "steaminfo": None,
                            "support": 550,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 35,
                            "country": "US",
                            "deaths": 0,
                            "defense": 240,
                            "is_vip": False,
                            "kills": 0,
                            "level": 99,
                            "loadout": "standard issue",
                            "name": "Jimmy",
                            "offense": 0,
                            "profile": None,
                            "role": "engineer",
                            "steam_bans": None,
                            "steam_id_64": "76561198087754443",
                            "steaminfo": None,
                            "support": 556,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                    ],
                    "support": 4827,
                    "type": "infantry",
                },
                "baker": {
                    "combat": 85,
                    "deaths": 22,
                    "defense": 1400,
                    "has_leader": False,
                    "kills": 11,
                    "offense": 220,
                    "players": [
                        {
                            "combat": 21,
                            "country": "",
                            "deaths": 9,
                            "defense": 560,
                            "is_vip": False,
                            "kills": 3,
                            "level": 88,
                            "loadout": "standard issue",
                            "name": "Lawless",
                            "offense": 40,
                            "profile": None,
                            "role": "heavymachinegunner",
                            "steam_bans": None,
                            "steam_id_64": "76561198055458575",
                            "steaminfo": None,
                            "support": 270,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                        {
                            "combat": 25,
                            "country": "",
                            "deaths": 5,
                            "defense": 320,
                            "is_vip": False,
                            "kills": 2,
                            "level": 82,
                            "loadout": "point man",
                            "name": "Major_Winters",
                            "offense": 180,
                            "profile": None,
                            "role": "rifleman",
                            "steam_bans": None,
                            "steam_id_64": "76561198985998769",
                            "steaminfo": None,
                            "support": 290,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                        {
                            "combat": 39,
                            "country": "",
                            "deaths": 7,
                            "defense": 340,
                            "is_vip": False,
                            "kills": 6,
                            "level": 69,
                            "loadout": "grenadier",
                            "name": "Toomz",
                            "offense": 0,
                            "profile": None,
                            "role": "assault",
                            "steam_bans": None,
                            "steam_id_64": "76561198393093210",
                            "steaminfo": None,
                            "support": 30,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                        {
                            "combat": 0,
                            "country": "BE",
                            "deaths": 0,
                            "defense": 140,
                            "is_vip": False,
                            "kills": 0,
                            "level": 59,
                            "loadout": "standard issue",
                            "name": "Zones (BEL)",
                            "offense": 0,
                            "profile": None,
                            "role": "engineer",
                            "steam_bans": None,
                            "steam_id_64": "76561198026310990",
                            "steaminfo": None,
                            "support": 524,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                        {
                            "combat": 0,
                            "country": "",
                            "deaths": 1,
                            "defense": 20,
                            "is_vip": False,
                            "kills": 0,
                            "level": 71,
                            "loadout": "standard issue",
                            "name": "Pavooloni",
                            "offense": 0,
                            "profile": None,
                            "role": "antitank",
                            "steam_bans": None,
                            "steam_id_64": "76561198198563101",
                            "steaminfo": None,
                            "support": 0,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                        {
                            "combat": 0,
                            "country": "private",
                            "deaths": 0,
                            "defense": 20,
                            "is_vip": False,
                            "kills": 0,
                            "level": 102,
                            "loadout": "standard issue",
                            "name": "Kjjuj",
                            "offense": 0,
                            "profile": None,
                            "role": "rifleman",
                            "steam_bans": None,
                            "steam_id_64": "76561198028236925",
                            "steaminfo": None,
                            "support": 0,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                    ],
                    "support": 1114,
                    "type": "infantry",
                },
            },
            "support": 8217,
        },
        "axis": {
            "combat": 1361,
            "commander": {
                "combat": 94,
                "country": "",
                "deaths": 10,
                "defense": 440,
                "is_vip": False,
                "kills": 12,
                "level": 102,
                "loadout": "veteran",
                "name": "Chevron",
                "offense": 60,
                "profile": {},
                "role": "armycommander",
                "steam_bans": {
                    "CommunityBanned": False,
                    "DaysSinceLastBan": 0,
                    "EconomyBan": "none",
                    "NumberOfGameBans": 0,
                    "NumberOfVACBans": 0,
                    "VACBanned": False,
                    "has_bans": False,
                },
                "steam_id_64": "76561199229309017",
                "support": 874,
                "team": "axis",
                "unit_id": 0,
                "unit_name": None,
            },
            "count": 48,
            "deaths": 204,
            "defense": 6420,
            "kills": 151,
            "offense": 5800,
            "squads": {
                "able": {
                    "combat": 304,
                    "deaths": 60,
                    "defense": 1780,
                    "has_leader": False,
                    "kills": 33,
                    "offense": 780,
                    "players": [
                        {
                            "combat": 63,
                            "country": "US",
                            "deaths": 18,
                            "defense": 380,
                            "is_vip": False,
                            "kills": 9,
                            "level": 110,
                            "loadout": "veteran",
                            "name": "emfoor",
                            "offense": 220,
                            "profile": None,
                            "role": "assault",
                            "steam_bans": None,
                            "steam_id_64": "76561198979089668",
                            "support": 125,
                            "team": "axis",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 68,
                            "country": "NL",
                            "deaths": 14,
                            "defense": 800,
                            "is_vip": True,
                            "kills": 5,
                            "level": 43,
                            "loadout": "standard issue",
                            "name": "Makaj",
                            "offense": 140,
                            "profile": None,
                            "role": "officer",
                            "steam_bans": None,
                            "steam_id_64": "76561198041823654",
                            "support": 2181,
                            "team": "axis",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 64,
                            "country": "",
                            "deaths": 12,
                            "defense": 140,
                            "is_vip": False,
                            "kills": 4,
                            "level": 170,
                            "loadout": "pionier",
                            "name": "tinner2115",
                            "offense": 300,
                            "profile": None,
                            "role": "engineer",
                            "steam_bans": None,
                            "steam_id_64": "76561198892700816",
                            "support": 0,
                            "team": "axis",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 58,
                            "country": "",
                            "deaths": 4,
                            "defense": 220,
                            "is_vip": False,
                            "kills": 6,
                            "level": 129,
                            "loadout": "ambusher",
                            "name": "Cuervo",
                            "offense": 40,
                            "profile": None,
                            "role": "antitank",
                            "steam_bans": None,
                            "steam_id_64": "76561198354354474",
                            "support": 0,
                            "team": "axis",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 27,
                            "country": "",
                            "deaths": 6,
                            "defense": 200,
                            "is_vip": False,
                            "kills": 5,
                            "level": 67,
                            "loadout": "veteran",
                            "name": "capitanodrew",
                            "offense": 40,
                            "profile": None,
                            "role": "heavymachinegunner",
                            "steam_bans": None,
                            "steam_id_64": "76561198046677517",
                            "support": 0,
                            "team": "axis",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                        {
                            "combat": 24,
                            "country": "",
                            "deaths": 6,
                            "defense": 40,
                            "is_vip": False,
                            "kills": 4,
                            "level": 10,
                            "loadout": "standard issue",
                            "name": "Dr.FishShitz",
                            "offense": 40,
                            "profile": None,
                            "role": "automaticrifleman",
                            "steam_bans": None,
                            "steam_id_64": "76561199027409370",
                            "support": 0,
                            "team": "axis",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                    ],
                    "support": 2306,
                    "type": "infantry",
                },
                "baker": {
                    "combat": 135,
                    "deaths": 10,
                    "defense": 600,
                    "has_leader": False,
                    "kills": 12,
                    "offense": 960,
                    "players": [
                        {
                            "combat": 50,
                            "country": "",
                            "deaths": 6,
                            "defense": 500,
                            "is_vip": False,
                            "kills": 6,
                            "level": 123,
                            "loadout": "ammo carrier",
                            "name": "WilliePeter",
                            "offense": 480,
                            "profile": None,
                            "role": "spotter",
                            "steam_bans": None,
                            "steam_id_64": "76561198206929555",
                            "support": 264,
                            "team": "axis",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                        {
                            "combat": 85,
                            "country": "US",
                            "deaths": 4,
                            "defense": 100,
                            "is_vip": True,
                            "kills": 6,
                            "level": 184,
                            "loadout": "veteran",
                            "name": "DarkVisionary",
                            "offense": 480,
                            "profile": None,
                            "role": "sniper",
                            "steam_bans": None,
                            "steam_id_64": "76561199166765040",
                            "support": 0,
                            "team": "axis",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                    ],
                    "support": 264,
                    "type": "recon",
                },
            },
            "support": 7323,
        },
    }


def test_should_warn_first_time(team_view):
    config = NoLeaderConfig(
        number_of_warning=2,
        warning_interval_seconds=60,
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]

    assert PunishStepState.apply == should_warn_player(
        watch_status, config, "able", player
    )
    assert PunishStepState.wait == should_warn_player(
        watch_status, config, "able", player
    )


def test_should_not_warn(team_view):
    config = NoLeaderConfig(
        number_of_warning=0,
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]

    assert PunishStepState.disabled == should_warn_player(
        watch_status, config, "able", player
    )
    assert PunishStepState.disabled == should_warn_player(
        watch_status, config, "able", player
    )
    assert WatchStatus() == watch_status


def test_should_warn_twice(team_view):
    config = NoLeaderConfig(
        number_of_warning=2,
        warning_interval_seconds=1,
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]

    assert PunishStepState.apply == should_warn_player(
        watch_status, config, "able", player
    )
    assert PunishStepState.wait == should_warn_player(
        watch_status, config, "able", player
    )
    time.sleep(config.warning_interval_seconds)
    assert PunishStepState.apply == should_warn_player(
        watch_status, config, "able", player
    )
    assert PunishStepState.wait == should_warn_player(
        watch_status, config, "able", player
    )
    time.sleep(config.warning_interval_seconds)
    assert PunishStepState.go_to_next_step == should_warn_player(
        watch_status, config, "able", player
    )


def test_should_warn_infinite(team_view):
    config = NoLeaderConfig(
        number_of_warning=-1,
        warning_interval_seconds=0,
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]

    for _ in range(100):
        assert PunishStepState.apply == should_warn_player(
            watch_status, config, "able", player
        )


def test_should_punish(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=10,
        immuned_roles=["support"],
    )

    watch_status = WatchStatus()
    assert PunishStepState.apply == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_wait(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=60,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )

    watch_status = WatchStatus()
    assert PunishStepState.apply == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )
    assert PunishStepState.wait == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_twice(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=1,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )

    watch_status = WatchStatus()
    assert PunishStepState.apply == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )
    assert PunishStepState.wait == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )
    time.sleep(config.punish_interval_seconds)
    assert PunishStepState.apply == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )
    time.sleep(config.punish_interval_seconds)
    assert PunishStepState.go_to_next_step == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_too_little_players(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=60,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=60,
        immuned_level_up_to=10,
        immuned_roles=[],
    )

    watch_status = WatchStatus()
    assert PunishStepState.wait == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_small_squad(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=60,
        min_squad_players_for_punish=7,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )

    watch_status = WatchStatus()
    assert PunishStepState.wait == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_disabled(team_view):
    config = NoLeaderConfig(
        number_of_punish=0,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )

    watch_status = WatchStatus()
    assert PunishStepState.disabled == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_immuned_role(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=["antitank"],
    )

    watch_status = WatchStatus()
    assert PunishStepState.immuned == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )

    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=["antitank", "support"],
    )

    watch_status = WatchStatus()
    assert PunishStepState.immuned == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_punish_immuned_lvl(team_view):
    config = NoLeaderConfig(
        number_of_punish=2,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        immuned_level_up_to=50,
        immuned_roles=[],
    )

    watch_status = WatchStatus()
    assert PunishStepState.immuned == should_punish_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        team_view["allies"]["squads"]["able"]["players"][0],
    )


def test_shouldnt_kick_without_punish(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=["support"],
    )

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    assert PunishStepState.disabled == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())
    assert PunishStepState.apply == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_shouldnt_kick_immuned(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=["antitank"],
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.immuned == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_shouldnt_kick_immuned_lvl(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=50,
        immuned_roles=[],
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.immuned == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_shouldnt_kick_small_squad(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=7,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.wait == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_shouldnt_kick_small_game(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=50,
        immuned_level_up_to=10,
        immuned_roles=[],
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.wait == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_shouldnt_kick_disabled(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=False,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.disabled == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_should_wait_kick(team_view):
    config = NoLeaderConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.wait == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )
    assert PunishStepState.wait == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )
    time.sleep(1)
    assert PunishStepState.apply == should_kick_player(
        watch_status,
        config,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        player,
    )


def test_watcher(team_view):
    config = NoLeaderConfig(
        number_of_warning=1,
        warning_interval_seconds=3,
        number_of_punish=2,
        punish_interval_seconds=4,
        min_squad_players_for_punish=0,
        disable_punish_below_server_player_count=0,
        kick_after_max_punish=True,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=0,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=10,
        immuned_roles=[],
    )

    state = {}

    @contextmanager
    def fake_state(red, team, squad_name):
        try:
            yield state.setdefault(f"{team}{squad_name}", WatchStatus())
        except (SquadCycleOver, SquadHasLeader):
            del state[f"{team}{squad_name}"]

    with mock.patch(
        "rcon.squad_automod.automod.watch_state", wraps=fake_state
    ), mock.patch("rcon.squad_automod.automod.get_redis_client"):
        rcon = mock.MagicMock()
        rcon.get_team_view_fast.return_value = team_view
        expected_warned_players = [
            APlayer(
                steam_id_64="76561198055458575",
                player="Lawless",
                squad="baker",
                team="allies",
                role="heavymachinegunner",
                lvl=88,
            ),
            APlayer(
                steam_id_64="76561198985998769",
                player="Major_Winters",
                squad="baker",
                team="allies",
                role="rifleman",
                lvl=82,
            ),
            APlayer(
                steam_id_64="76561198393093210",
                player="Toomz",
                squad="baker",
                team="allies",
                role="assault",
                lvl=69,
            ),
            APlayer(
                steam_id_64="76561198026310990",
                player="Zones (BEL)",
                squad="baker",
                team="allies",
                role="engineer",
                lvl=59,
            ),
            APlayer(
                steam_id_64="76561198198563101",
                player="Pavooloni",
                squad="baker",
                team="allies",
                role="antitank",
                lvl=71,
            ),
            APlayer(
                steam_id_64="76561198028236925",
                player="Kjjuj",
                squad="baker",
                team="allies",
                role="rifleman",
                lvl=102,
            ),
            APlayer(
                steam_id_64="76561198979089668",
                player="emfoor",
                squad="able",
                team="axis",
                role="assault",
                lvl=110,
            ),
            APlayer(
                steam_id_64="76561198041823654",
                player="Makaj",
                squad="able",
                team="axis",
                role="officer",
                lvl=43,
            ),
            APlayer(
                steam_id_64="76561198892700816",
                player="tinner2115",
                squad="able",
                team="axis",
                role="engineer",
                lvl=170,
            ),
            APlayer(
                steam_id_64="76561198354354474",
                player="Cuervo",
                squad="able",
                team="axis",
                role="antitank",
                lvl=129,
            ),
            APlayer(
                steam_id_64="76561198046677517",
                player="capitanodrew",
                squad="able",
                team="axis",
                role="heavymachinegunner",
                lvl=67,
            ),
            APlayer(
                steam_id_64="76561199027409370",
                player="Dr.FishShitz",
                squad="able",
                team="axis",
                role="automaticrifleman",
                lvl=10,
            ),
            APlayer(
                steam_id_64="76561198206929555",
                player="WilliePeter",
                squad="baker",
                team="axis",
                role="spotter",
                lvl=123,
            ),
            APlayer(
                steam_id_64="76561199166765040",
                player="DarkVisionary",
                squad="baker",
                team="axis",
                role="sniper",
                lvl=184,
            ),
        ]
        expected_punished_players = list(
            filter(lambda p: p.lvl > 10, expected_warned_players)
        )

        # 1st warning
        to_apply = get_punitions_to_apply(rcon, config)
        assert expected_warned_players == to_apply.warning

        expected_squad_state = [
            ASquad(
                team="allies",
                name="baker",
                players=[
                    APlayer(
                        steam_id_64="76561198055458575",
                        player="Lawless",
                        squad="baker",
                        team="allies",
                        role="heavymachinegunner",
                        lvl=88,
                    ),
                    APlayer(
                        steam_id_64="76561198985998769",
                        player="Major_Winters",
                        squad="baker",
                        team="allies",
                        role="rifleman",
                        lvl=82,
                    ),
                    APlayer(
                        steam_id_64="76561198393093210",
                        player="Toomz",
                        squad="baker",
                        team="allies",
                        role="assault",
                        lvl=69,
                    ),
                    APlayer(
                        steam_id_64="76561198026310990",
                        player="Zones (BEL)",
                        squad="baker",
                        team="allies",
                        role="engineer",
                        lvl=59,
                    ),
                    APlayer(
                        steam_id_64="76561198198563101",
                        player="Pavooloni",
                        squad="baker",
                        team="allies",
                        role="antitank",
                        lvl=71,
                    ),
                    APlayer(
                        steam_id_64="76561198028236925",
                        player="Kjjuj",
                        squad="baker",
                        team="allies",
                        role="rifleman",
                        lvl=102,
                    ),
                ],
            ),
            ASquad(
                team="axis",
                name="able",
                players=[
                    APlayer(
                        steam_id_64="76561198979089668",
                        player="emfoor",
                        squad="able",
                        team="axis",
                        role="assault",
                        lvl=110,
                    ),
                    APlayer(
                        steam_id_64="76561198041823654",
                        player="Makaj",
                        squad="able",
                        team="axis",
                        role="officer",
                        lvl=43,
                    ),
                    APlayer(
                        steam_id_64="76561198892700816",
                        player="tinner2115",
                        squad="able",
                        team="axis",
                        role="engineer",
                        lvl=170,
                    ),
                    APlayer(
                        steam_id_64="76561198354354474",
                        player="Cuervo",
                        squad="able",
                        team="axis",
                        role="antitank",
                        lvl=129,
                    ),
                    APlayer(
                        steam_id_64="76561198046677517",
                        player="capitanodrew",
                        squad="able",
                        team="axis",
                        role="heavymachinegunner",
                        lvl=67,
                    ),
                    APlayer(
                        steam_id_64="76561199027409370",
                        player="Dr.FishShitz",
                        squad="able",
                        team="axis",
                        role="automaticrifleman",
                        lvl=10,
                    ),
                ],
            ),
            ASquad(
                team="axis",
                name="baker",
                players=[
                    APlayer(
                        steam_id_64="76561198206929555",
                        player="WilliePeter",
                        squad="baker",
                        team="axis",
                        role="spotter",
                        lvl=123,
                    ),
                    APlayer(
                        steam_id_64="76561199166765040",
                        player="DarkVisionary",
                        squad="baker",
                        team="axis",
                        role="sniper",
                        lvl=184,
                    ),
                ],
            ),
        ]

        assert PunitionsToApply(
            warning=[], punish=[], kick=[], squads_state=expected_squad_state
        ) == get_punitions_to_apply(rcon, config)
        time.sleep(config.warning_interval_seconds)

        # 1st punish
        assert expected_punished_players == get_punitions_to_apply(rcon, config).punish
        assert PunitionsToApply(
            warning=[], punish=[], kick=[], squads_state=[]
        ) == get_punitions_to_apply(rcon, config)
        time.sleep(config.punish_interval_seconds)

        # 2nd punish
        assert expected_punished_players == get_punitions_to_apply(rcon, config).punish
        assert PunitionsToApply(
            warning=[], punish=[], kick=[], squads_state=[]
        ) == get_punitions_to_apply(rcon, config)
        time.sleep(config.punish_interval_seconds)

        # kick, final
        assert expected_punished_players == get_punitions_to_apply(rcon, config).kick


def test_watcher_no_kick(team_view):
    config = NoLeaderConfig(
        number_of_warning=1,
        warning_interval_seconds=3,
        number_of_punish=2,
        punish_interval_seconds=4,
        min_squad_players_for_punish=3,
        disable_punish_below_server_player_count=0,
        kick_after_max_punish=False,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=3,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=1,
        immuned_roles=[],
    )

    state = {}

    @contextmanager
    def fake_state(red, team, squad_name):
        try:
            yield state.setdefault(f"{team}{squad_name}", WatchStatus())
        except (SquadCycleOver, SquadHasLeader):
            del state[f"{team}{squad_name}"]

    with mock.patch(
        "rcon.squad_automod.automod.watch_state", wraps=fake_state
    ), mock.patch("rcon.squad_automod.automod.get_redis_client"):
        rcon = mock.MagicMock()
        rcon.get_team_view_fast.return_value = team_view
        expected_warned_players = [
            APlayer(
                steam_id_64="76561198055458575",
                player="Lawless",
                squad="baker",
                team="allies",
                role="heavymachinegunner",
                lvl=88,
            ),
            APlayer(
                steam_id_64="76561198985998769",
                player="Major_Winters",
                squad="baker",
                team="allies",
                role="rifleman",
                lvl=82,
            ),
            APlayer(
                steam_id_64="76561198393093210",
                player="Toomz",
                squad="baker",
                team="allies",
                role="assault",
                lvl=69,
            ),
            APlayer(
                steam_id_64="76561198026310990",
                player="Zones (BEL)",
                squad="baker",
                team="allies",
                role="engineer",
                lvl=59,
            ),
            APlayer(
                steam_id_64="76561198198563101",
                player="Pavooloni",
                squad="baker",
                team="allies",
                role="antitank",
                lvl=71,
            ),
            APlayer(
                steam_id_64="76561198028236925",
                player="Kjjuj",
                squad="baker",
                team="allies",
                role="rifleman",
                lvl=102,
            ),
            APlayer(
                steam_id_64="76561198979089668",
                player="emfoor",
                squad="able",
                team="axis",
                role="assault",
                lvl=110,
            ),
            APlayer(
                steam_id_64="76561198041823654",
                player="Makaj",
                squad="able",
                team="axis",
                role="officer",
                lvl=43,
            ),
            APlayer(
                steam_id_64="76561198892700816",
                player="tinner2115",
                squad="able",
                team="axis",
                role="engineer",
                lvl=170,
            ),
            APlayer(
                steam_id_64="76561198354354474",
                player="Cuervo",
                squad="able",
                team="axis",
                role="antitank",
                lvl=129,
            ),
            APlayer(
                steam_id_64="76561198046677517",
                player="capitanodrew",
                squad="able",
                team="axis",
                role="heavymachinegunner",
                lvl=67,
            ),
            APlayer(
                steam_id_64="76561199027409370",
                player="Dr.FishShitz",
                squad="able",
                team="axis",
                role="automaticrifleman",
                lvl=10,
            ),
            APlayer(
                steam_id_64="76561198206929555",
                player="WilliePeter",
                squad="baker",
                team="axis",
                role="spotter",
                lvl=123,
            ),
            APlayer(
                steam_id_64="76561199166765040",
                player="DarkVisionary",
                squad="baker",
                team="axis",
                role="sniper",
                lvl=184,
            ),
        ]
        expected_punished_players = list(
            filter(
                lambda p: p.squad != "baker" or p.team != "axis",
                expected_warned_players,
            )
        )

        # 1st warning
        assert expected_warned_players == get_punitions_to_apply(rcon, config).warning
        assert [] == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning
        time.sleep(config.warning_interval_seconds)

        # 1st punish
        assert expected_punished_players == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning
        time.sleep(config.punish_interval_seconds)

        # 2nd punish
        assert expected_punished_players == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning
        time.sleep(config.punish_interval_seconds)

        # no kick, final
        assert [] == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning


def test_watcher_resets(team_view):
    config = NoLeaderConfig(
        number_of_warning=0,
        warning_interval_seconds=3,
        number_of_punish=1,
        punish_interval_seconds=4,
        min_squad_players_for_punish=3,
        disable_punish_below_server_player_count=0,
        kick_after_max_punish=False,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=3,
        disable_kick_below_server_player_count=0,
        immuned_level_up_to=1,
        immuned_roles=[],
    )

    state = {}

    @contextmanager
    def fake_state(red, team, squad_name):
        try:
            yield state.setdefault(f"{team}{squad_name}", WatchStatus())
        except (SquadCycleOver, SquadHasLeader):
            del state[f"{team}{squad_name}"]

    with mock.patch(
        "rcon.squad_automod.automod.watch_state", wraps=fake_state
    ), mock.patch("rcon.squad_automod.automod.get_redis_client"):
        rcon = mock.MagicMock()
        rcon.get_team_view_fast.return_value = team_view
        expected_players = [
            APlayer(
                steam_id_64="76561198055458575",
                player="Lawless",
                squad="baker",
                team="allies",
                role="heavymachinegunner",
                lvl=88,
            ),
            APlayer(
                steam_id_64="76561198985998769",
                player="Major_Winters",
                squad="baker",
                team="allies",
                role="rifleman",
                lvl=82,
            ),
            APlayer(
                steam_id_64="76561198393093210",
                player="Toomz",
                squad="baker",
                team="allies",
                role="assault",
                lvl=69,
            ),
            APlayer(
                steam_id_64="76561198026310990",
                player="Zones (BEL)",
                squad="baker",
                team="allies",
                role="engineer",
                lvl=59,
            ),
            APlayer(
                steam_id_64="76561198198563101",
                player="Pavooloni",
                squad="baker",
                team="allies",
                role="antitank",
                lvl=71,
            ),
            APlayer(
                steam_id_64="76561198028236925",
                player="Kjjuj",
                squad="baker",
                team="allies",
                role="rifleman",
                lvl=102,
            ),
            APlayer(
                steam_id_64="76561198979089668",
                player="emfoor",
                squad="able",
                team="axis",
                role="assault",
                lvl=110,
            ),
            APlayer(
                steam_id_64="76561198041823654",
                player="Makaj",
                squad="able",
                team="axis",
                role="officer",
                lvl=43,
            ),
            APlayer(
                steam_id_64="76561198892700816",
                player="tinner2115",
                squad="able",
                team="axis",
                role="engineer",
                lvl=170,
            ),
            APlayer(
                steam_id_64="76561198354354474",
                player="Cuervo",
                squad="able",
                team="axis",
                role="antitank",
                lvl=129,
            ),
            APlayer(
                steam_id_64="76561198046677517",
                player="capitanodrew",
                squad="able",
                team="axis",
                role="heavymachinegunner",
                lvl=67,
            ),
            APlayer(
                steam_id_64="76561199027409370",
                player="Dr.FishShitz",
                squad="able",
                team="axis",
                role="automaticrifleman",
                lvl=10,
            ),
            # APlayer(player="WilliePeter",
            # APlayer(player="DarkVisionary",
        ]

        # 1st punish
        assert expected_players == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning
        time.sleep(config.punish_interval_seconds)

        # Nothing should happen
        assert [] == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning

        assert "alliesbaker" in state
        team_view["allies"]["squads"]["baker"]["has_leader"] = True
        team_view["axis"]["squads"]["able"]["has_leader"] = True
        team_view["axis"]["squads"]["baker"]["has_leader"] = True
        assert [] == get_punitions_to_apply(rcon, config).punish
        assert [] == get_punitions_to_apply(rcon, config).kick
        assert [] == get_punitions_to_apply(rcon, config).warning
        # state should be reset now
        assert "alliesbaker" not in state
        team_view["allies"]["squads"]["baker"]["has_leader"] = False
        team_view["axis"]["squads"]["able"]["has_leader"] = False
        team_view["axis"]["squads"]["baker"]["has_leader"] = False
        # punish again
        assert expected_players == get_punitions_to_apply(rcon, config).punish


def test_default_config():
    config = get_config()
    config = NoLeaderConfig(**config["NOLEADER_AUTO_MOD"])

    assert config.enabled == False

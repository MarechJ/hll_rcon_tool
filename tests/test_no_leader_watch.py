import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest import mock

from pytest import fixture

from rcon.automods.automod import get_punitions_to_apply
from rcon.automods.models import (
    ASquad,
    NoLeaderConfig,
    PunishDetails,
    PunishPlayer,
    PunishStepState,
    PunitionsToApply,
    SquadCycleOver,
    SquadHasLeader,
    WatchStatus,
)
from rcon.automods.no_leader import NoLeaderAutomod
from rcon.typedefs import GameState, Roles
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig


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
                "unit_id": -1,
                "unit_name": "Commander",
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


game_state: GameState = {
    "allied_score": 3,
    "axis_score": 2,
    "current_map": "",
    "next_map": "",
    "num_allied_players": 30,
    "num_axis_players": 30,
    "time_remaining": timedelta(10),
}


def construct_aplayer(
    player_dict: dict, team_name: str = "allies", squad_name: str = "able"
):
    return PunishPlayer(
        steam_id_64=player_dict["steam_id_64"],
        name=player_dict["name"],
        team=team_name,
        squad=squad_name,
        role=player_dict.get("role"),
        lvl=int(player_dict.get("level")),
    )


def test_should_not_note(team_view):
    mod = NoLeaderAutomod(
        NoLeaderConfig(
            number_of_notes=0,
        ),
        None,
    )
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_note_player(
        watch_status, "able", aplayer
    )
    assert PunishStepState.DISABLED == mod.should_note_player(
        watch_status, "able", aplayer
    )
    assert WatchStatus() == watch_status


def test_should_note_twice(team_view):
    config = AutoModNoLeaderUserConfig(number_of_notes=2, notes_interval_seconds=1)
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_note_player(
        watch_status, "able", aplayer
    )
    assert PunishStepState.WAIT == mod.should_note_player(watch_status, "able", aplayer)
    time.sleep(config.notes_interval_seconds)
    assert PunishStepState.APPLY == mod.should_note_player(
        watch_status, "able", aplayer
    )
    assert PunishStepState.WAIT == mod.should_note_player(watch_status, "able", aplayer)
    time.sleep(config.notes_interval_seconds)
    assert PunishStepState.GO_TO_NEXT_STEP == mod.should_note_player(
        watch_status, "able", aplayer
    )


def test_should_not_warn(team_view):
    config = AutoModNoLeaderUserConfig(number_of_warnings=0)
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_warn_player(
        watch_status, "able", aplayer
    )
    assert PunishStepState.DISABLED == mod.should_warn_player(
        watch_status, "able", aplayer
    )
    assert WatchStatus() == watch_status


def test_should_warn_twice(team_view):
    config = AutoModNoLeaderUserConfig(number_of_warnings=2, warning_interval_seconds=1)
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_warn_player(
        watch_status, "able", aplayer
    )
    assert PunishStepState.WAIT == mod.should_warn_player(watch_status, "able", aplayer)
    time.sleep(config.warning_interval_seconds)
    assert PunishStepState.APPLY == mod.should_warn_player(
        watch_status, "able", aplayer
    )
    assert PunishStepState.WAIT == mod.should_warn_player(watch_status, "able", aplayer)
    time.sleep(config.warning_interval_seconds)
    assert PunishStepState.GO_TO_NEXT_STEP == mod.should_warn_player(
        watch_status, "able", aplayer
    )


def test_should_warn_infinite(team_view):
    config = AutoModNoLeaderUserConfig(number_of_warnings=1, warning_interval_seconds=0)
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    for _ in range(100):
        assert PunishStepState.APPLY == mod.should_warn_player(
            watch_status, "able", aplayer
        )


def test_should_punish(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=10,
        immune_roles=[Roles("support")],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_wait(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=60,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_twice(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=1,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    time.sleep(config.punish_interval_seconds)
    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    time.sleep(config.punish_interval_seconds)
    assert PunishStepState.GO_TO_NEXT_STEP == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_too_little_players(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=60,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=60,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_small_squad(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=60,
        min_squad_players_for_punish=7,
        min_server_players_for_punish=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_disabled(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=0,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_immuned_role(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        immune_player_level=10,
        immune_roles=[Roles.anti_tank],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.IMMUNED == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )

    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        immune_player_level=10,
        immune_roles=[Roles.anti_tank, Roles.support],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    assert PunishStepState.IMMUNED == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_punish_immuned_lvl(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=0,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        immune_player_level=50,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.IMMUNED == mod.should_punish_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_shouldnt_kick_without_punish(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[Roles.support],
    )
    mod = NoLeaderAutomod(config, None)

    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())
    assert PunishStepState.APPLY == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_shouldnt_kick_immuned(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[Roles.anti_tank],
    )
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.IMMUNED == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_shouldnt_kick_immuned_lvl(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=50,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.IMMUNED == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_shouldnt_kick_small_squad(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=7,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.WAIT == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_shouldnt_kick_small_game(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=50,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.WAIT == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_shouldnt_kick_disabled(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=False,
        kick_grace_period_seconds=0,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.DISABLED == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_should_wait_kick(team_view):
    config = AutoModNoLeaderUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[],
    )
    mod = NoLeaderAutomod(config, None)
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.WAIT == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    assert PunishStepState.WAIT == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )
    time.sleep(1)
    assert PunishStepState.APPLY == mod.should_kick_player(
        watch_status,
        team_view,
        "able",
        team_view["allies"]["squads"]["able"],
        aplayer,
    )


def test_ignores_commander(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_notes=0,
        number_of_warnings=1,
        warning_interval_seconds=3,
        number_of_punishments=2,
        punish_interval_seconds=4,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        kick_after_max_punish=True,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[],
        warning_message="",
        punish_message="",
        kick_message="",
    )
    mod = NoLeaderAutomod(config, None)
    to_apply = mod.punitions_to_apply(
        team_view,
        "Commander",
        "allies",
        {"players": [team_view["allies"]["commander"]]},
        game_state,
    )

    assert to_apply.warning == []


def test_watcher(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_notes=0,
        number_of_warnings=1,
        warning_interval_seconds=3,
        number_of_punishments=2,
        punish_interval_seconds=4,
        min_squad_players_for_punish=0,
        min_server_players_for_punish=0,
        kick_after_max_punish=True,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=0,
        min_server_players_for_kick=0,
        immune_player_level=10,
        immune_roles=[],
        warning_message="",
        punish_message="",
        kick_message="",
    )

    state = {}

    @contextmanager
    def fake_state(team, squad_name):
        try:
            yield state.setdefault(f"{team}{squad_name}", WatchStatus())
        except (SquadCycleOver, SquadHasLeader):
            del state[f"{team}{squad_name}"]

    rcon = mock.MagicMock()
    rcon.get_team_view.return_value = team_view
    expected_warned_players = [
        PunishPlayer(
            steam_id_64="76561198055458575",
            name="Lawless",
            squad="baker",
            team="allies",
            role="heavymachinegunner",
            lvl=88,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198985998769",
            name="Major_Winters",
            squad="baker",
            team="allies",
            role="rifleman",
            lvl=82,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198393093210",
            name="Toomz",
            squad="baker",
            team="allies",
            role="assault",
            lvl=69,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198026310990",
            name="Zones (BEL)",
            squad="baker",
            team="allies",
            role="engineer",
            lvl=59,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198198563101",
            name="Pavooloni",
            squad="baker",
            team="allies",
            role="antitank",
            lvl=71,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198028236925",
            name="Kjjuj",
            squad="baker",
            team="allies",
            role="rifleman",
            lvl=102,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198979089668",
            name="emfoor",
            squad="able",
            team="axis",
            role="assault",
            lvl=110,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198041823654",
            name="Makaj",
            squad="able",
            team="axis",
            role="officer",
            lvl=43,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198892700816",
            name="tinner2115",
            squad="able",
            team="axis",
            role="engineer",
            lvl=170,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198354354474",
            name="Cuervo",
            squad="able",
            team="axis",
            role="antitank",
            lvl=129,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198046677517",
            name="capitanodrew",
            squad="able",
            team="axis",
            role="heavymachinegunner",
            lvl=67,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198206929555",
            name="WilliePeter",
            squad="baker",
            team="axis",
            role="spotter",
            lvl=123,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561199166765040",
            name="DarkVisionary",
            squad="baker",
            team="axis",
            role="sniper",
            lvl=184,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
    ]
    expected_punished_players = list(
        filter(lambda p: p.lvl > 10, expected_warned_players)
    )

    # 1st warning
    mod = NoLeaderAutomod(config, None)
    mod.watch_state = fake_state
    to_apply = get_punitions_to_apply(rcon, [mod])
    assert expected_warned_players == to_apply.warning

    expected_squad_state = [
        ASquad(
            team="allies",
            name="baker",
            players=[
                PunishPlayer(
                    steam_id_64="76561198055458575",
                    name="Lawless",
                    squad="baker",
                    team="allies",
                    role="heavymachinegunner",
                    lvl=88,
                ),
                PunishPlayer(
                    steam_id_64="76561198985998769",
                    name="Major_Winters",
                    squad="baker",
                    team="allies",
                    role="rifleman",
                    lvl=82,
                ),
                PunishPlayer(
                    steam_id_64="76561198393093210",
                    name="Toomz",
                    squad="baker",
                    team="allies",
                    role="assault",
                    lvl=69,
                ),
                PunishPlayer(
                    steam_id_64="76561198026310990",
                    name="Zones (BEL)",
                    squad="baker",
                    team="allies",
                    role="engineer",
                    lvl=59,
                ),
                PunishPlayer(
                    steam_id_64="76561198198563101",
                    name="Pavooloni",
                    squad="baker",
                    team="allies",
                    role="antitank",
                    lvl=71,
                ),
                PunishPlayer(
                    steam_id_64="76561198028236925",
                    name="Kjjuj",
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
                PunishPlayer(
                    steam_id_64="76561198979089668",
                    name="emfoor",
                    squad="able",
                    team="axis",
                    role="assault",
                    lvl=110,
                ),
                PunishPlayer(
                    steam_id_64="76561198041823654",
                    name="Makaj",
                    squad="able",
                    team="axis",
                    role="officer",
                    lvl=43,
                ),
                PunishPlayer(
                    steam_id_64="76561198892700816",
                    name="tinner2115",
                    squad="able",
                    team="axis",
                    role="engineer",
                    lvl=170,
                ),
                PunishPlayer(
                    steam_id_64="76561198354354474",
                    name="Cuervo",
                    squad="able",
                    team="axis",
                    role="antitank",
                    lvl=129,
                ),
                PunishPlayer(
                    steam_id_64="76561198046677517",
                    name="capitanodrew",
                    squad="able",
                    team="axis",
                    role="heavymachinegunner",
                    lvl=67,
                ),
                PunishPlayer(
                    steam_id_64="76561199027409370",
                    name="Dr.FishShitz",
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
                PunishPlayer(
                    steam_id_64="76561198206929555",
                    name="WilliePeter",
                    squad="baker",
                    team="axis",
                    role="spotter",
                    lvl=123,
                ),
                PunishPlayer(
                    steam_id_64="76561199166765040",
                    name="DarkVisionary",
                    squad="baker",
                    team="axis",
                    role="sniper",
                    lvl=184,
                ),
            ],
        ),
    ]

    mod = NoLeaderAutomod(config, None)
    mod.watch_state = fake_state
    assert PunitionsToApply(
        warning=[], punish=[], kick=[], squads_state=expected_squad_state
    ) == get_punitions_to_apply(rcon, [mod])
    time.sleep(config.warning_interval_seconds)

    # 1st punish
    assert expected_punished_players == get_punitions_to_apply(rcon, [mod]).punish
    assert PunitionsToApply(
        warning=[], punish=[], kick=[], squads_state=[]
    ) == get_punitions_to_apply(rcon, [mod])
    time.sleep(config.punish_interval_seconds)

    # 2nd punish
    assert expected_punished_players == get_punitions_to_apply(rcon, [mod]).punish
    assert PunitionsToApply(
        warning=[], punish=[], kick=[], squads_state=[]
    ) == get_punitions_to_apply(rcon, [mod])
    time.sleep(config.punish_interval_seconds)

    # kick, final
    assert expected_punished_players == get_punitions_to_apply(rcon, [mod]).kick


def test_watcher_no_kick(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_notes=0,
        number_of_warnings=1,
        warning_interval_seconds=3,
        number_of_punishments=2,
        punish_interval_seconds=4,
        min_squad_players_for_punish=3,
        min_server_players_for_punish=0,
        kick_after_max_punish=False,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=3,
        min_server_players_for_kick=0,
        immune_player_level=1,
        immune_roles=[],
        warning_message="",
        punish_message="",
        kick_message="",
    )
    state = {}

    @contextmanager
    def fake_state(team, squad_name):
        try:
            yield state.setdefault(f"{team}{squad_name}", WatchStatus())
        except (SquadCycleOver, SquadHasLeader):
            del state[f"{team}{squad_name}"]

    rcon = mock.MagicMock()
    rcon.get_team_view.return_value = team_view
    expected_warned_players = [
        PunishPlayer(
            steam_id_64="76561198055458575",
            name="Lawless",
            squad="baker",
            team="allies",
            role="heavymachinegunner",
            lvl=88,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198985998769",
            name="Major_Winters",
            squad="baker",
            team="allies",
            role="rifleman",
            lvl=82,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198393093210",
            name="Toomz",
            squad="baker",
            team="allies",
            role="assault",
            lvl=69,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198026310990",
            name="Zones (BEL)",
            squad="baker",
            team="allies",
            role="engineer",
            lvl=59,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198198563101",
            name="Pavooloni",
            squad="baker",
            team="allies",
            role="antitank",
            lvl=71,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198028236925",
            name="Kjjuj",
            squad="baker",
            team="allies",
            role="rifleman",
            lvl=102,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198979089668",
            name="emfoor",
            squad="able",
            team="axis",
            role="assault",
            lvl=110,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198041823654",
            name="Makaj",
            squad="able",
            team="axis",
            role="officer",
            lvl=43,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198892700816",
            name="tinner2115",
            squad="able",
            team="axis",
            role="engineer",
            lvl=170,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198354354474",
            name="Cuervo",
            squad="able",
            team="axis",
            role="antitank",
            lvl=129,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198046677517",
            name="capitanodrew",
            squad="able",
            team="axis",
            role="heavymachinegunner",
            lvl=67,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561199027409370",
            name="Dr.FishShitz",
            squad="able",
            team="axis",
            role="automaticrifleman",
            lvl=10,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198206929555",
            name="WilliePeter",
            squad="baker",
            team="axis",
            role="spotter",
            lvl=123,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561199166765040",
            name="DarkVisionary",
            squad="baker",
            team="axis",
            role="sniper",
            lvl=184,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
    ]
    expected_punished_players = list(
        filter(
            lambda p: p.squad != "baker" or p.team != "axis",
            expected_warned_players,
        )
    )

    mod = NoLeaderAutomod(config, None)
    mod.watch_state = fake_state
    # 1st warning
    assert expected_warned_players == get_punitions_to_apply(rcon, [mod]).warning
    assert [] == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning
    time.sleep(config.warning_interval_seconds)

    # 1st punish
    assert expected_punished_players == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning
    time.sleep(config.punish_interval_seconds)

    # 2nd punish
    assert expected_punished_players == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning
    time.sleep(config.punish_interval_seconds)

    # no kick, final
    assert [] == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning


def test_watcher_resets(team_view):
    config = AutoModNoLeaderUserConfig(
        number_of_notes=0,
        number_of_warnings=0,
        warning_interval_seconds=3,
        number_of_punishments=1,
        punish_interval_seconds=4,
        min_squad_players_for_punish=3,
        min_server_players_for_punish=0,
        kick_after_max_punish=False,
        kick_grace_period_seconds=1,
        min_squad_players_for_kick=3,
        min_server_players_for_kick=0,
        immune_player_level=1,
        immune_roles=[],
        warning_message="",
        punish_message="",
        kick_message="",
    )
    state = {}

    @contextmanager
    def fake_state(team, squad_name):
        try:
            yield state.setdefault(f"{team}{squad_name}", WatchStatus())
        except (SquadCycleOver, SquadHasLeader):
            del state[f"{team}{squad_name}"]

    rcon = mock.MagicMock()
    rcon.get_team_view.return_value = team_view
    expected_players = [
        PunishPlayer(
            steam_id_64="76561198055458575",
            name="Lawless",
            squad="baker",
            team="allies",
            role="heavymachinegunner",
            lvl=88,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198985998769",
            name="Major_Winters",
            squad="baker",
            team="allies",
            role="rifleman",
            lvl=82,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198393093210",
            name="Toomz",
            squad="baker",
            team="allies",
            role="assault",
            lvl=69,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198026310990",
            name="Zones (BEL)",
            squad="baker",
            team="allies",
            role="engineer",
            lvl=59,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198198563101",
            name="Pavooloni",
            squad="baker",
            team="allies",
            role="antitank",
            lvl=71,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198028236925",
            name="Kjjuj",
            squad="baker",
            team="allies",
            role="rifleman",
            lvl=102,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198979089668",
            name="emfoor",
            squad="able",
            team="axis",
            role="assault",
            lvl=110,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198041823654",
            name="Makaj",
            squad="able",
            team="axis",
            role="officer",
            lvl=43,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198892700816",
            name="tinner2115",
            squad="able",
            team="axis",
            role="engineer",
            lvl=170,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198354354474",
            name="Cuervo",
            squad="able",
            team="axis",
            role="antitank",
            lvl=129,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561198046677517",
            name="capitanodrew",
            squad="able",
            team="axis",
            role="heavymachinegunner",
            lvl=67,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        PunishPlayer(
            steam_id_64="76561199027409370",
            name="Dr.FishShitz",
            squad="able",
            team="axis",
            role="automaticrifleman",
            lvl=10,
            details=PunishDetails(
                author="NoLeaderWatch-DryRun",
                message="",
                discord_audit_url="",
                dry_run=True,
            ),
        ),
        # APlayer(name="WilliePeter",
        # APlayer(name="DarkVisionary",
    ]

    mod = NoLeaderAutomod(config, None)
    mod.watch_state = fake_state
    # 1st punish
    assert expected_players == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning
    time.sleep(config.punish_interval_seconds)

    # Nothing should happen
    assert [] == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning

    assert "alliesbaker" in state
    team_view["allies"]["squads"]["baker"]["has_leader"] = True
    team_view["axis"]["squads"]["able"]["has_leader"] = True
    team_view["axis"]["squads"]["baker"]["has_leader"] = True
    assert [] == get_punitions_to_apply(rcon, [mod]).punish
    assert [] == get_punitions_to_apply(rcon, [mod]).kick
    assert [] == get_punitions_to_apply(rcon, [mod]).warning
    # state should be reset now
    assert "alliesbaker" not in state
    team_view["allies"]["squads"]["baker"]["has_leader"] = False
    team_view["axis"]["squads"]["able"]["has_leader"] = False
    team_view["axis"]["squads"]["baker"]["has_leader"] = False
    # punish again
    assert expected_players == get_punitions_to_apply(rcon, [mod]).punish


def test_default_config():
    config = AutoModNoLeaderUserConfig.load_from_db()
    assert config.enabled == False

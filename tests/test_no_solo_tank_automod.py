import time
from datetime import datetime, timedelta

from pytest import fixture

from rcon.automods.models import PunishPlayer, PunishStepState, WatchStatus
from rcon.automods.no_solotank import NoSoloTankAutomod
from rcon.typedefs import GameState
from rcon.user_config.auto_mod_solo_tank import AutoModNoSoloTankUserConfig


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
                            "loadout": "mechanic",
                            "name": "xRONINx6",
                            "offense": 100,
                            "profile": None,
                            "role": "tankcommander",
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
                            "loadout": "mechanic",
                            "name": "-SHAKA-",
                            "offense": 260,
                            "profile": None,
                            "role": "crewman",
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
                            "loadout": "mechanic",
                            "name": "ByteSized",
                            "offense": 80,
                            "profile": None,
                            "role": "crewman",
                            "steam_bans": None,
                            "steam_id_64": "76561198109929335",
                            "steaminfo": None,
                            "support": 1992,
                            "team": "allies",
                            "unit_id": 0,
                            "unit_name": "able",
                        },
                    ],
                    "support": 4827,
                    "type": "armor",
                },
                "baker": {
                    "combat": 85,
                    "deaths": 22,
                    "defense": 1400,
                    "has_leader": True,
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
                            "loadout": "mechanic",
                            "name": "Lawless",
                            "offense": 40,
                            "profile": None,
                            "role": "tankcommander",
                            "steam_bans": None,
                            "steam_id_64": "76561198055458575",
                            "steaminfo": None,
                            "support": 270,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "baker",
                        },
                    ],
                    "support": 1114,
                    "type": "armor",
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


# TODO: when should it note?


def test_should_not_warn(team_view):
    config = AutoModNoSoloTankUserConfig(number_of_warnings=0)
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # able squad is a full tank squad
    player = team_view["allies"]["squads"]["able"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_warn_player(
        watch_status, "able", aplayer
    )

    assert WatchStatus() == watch_status


def test_should_warn_twice(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_warnings=2,
        warning_interval_seconds=1,
    )
    mod = NoSoloTankAutomod(config, None)
    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_warn_player(
        watch_status, "baker", aplayer
    )
    assert PunishStepState.WAIT == mod.should_warn_player(
        watch_status, "baker", aplayer
    )
    time.sleep(config.warning_interval_seconds)
    assert PunishStepState.APPLY == mod.should_warn_player(
        watch_status, "baker", aplayer
    )
    assert PunishStepState.WAIT == mod.should_warn_player(
        watch_status, "baker", aplayer
    )
    time.sleep(config.warning_interval_seconds)
    assert PunishStepState.GO_TO_NEXT_STEP == mod.should_warn_player(
        watch_status, "baker", aplayer
    )


def test_should_warn_infinite(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_warnings=-1, warning_interval_seconds=0
    )
    mod = NoSoloTankAutomod(config, None)
    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    for _ in range(100):
        assert PunishStepState.APPLY == mod.should_warn_player(
            watch_status, "able", aplayer
        )


def test_should_punish(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_punishments=2,
        min_server_players_for_punish=10,
    )
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_punish_wait(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=60,
        min_server_players_for_punish=0,
    )
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_punish_twice(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=1,
        min_server_players_for_punish=0,
    )
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    time.sleep(config.punish_interval_seconds)
    assert PunishStepState.APPLY == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    time.sleep(config.punish_interval_seconds)
    assert PunishStepState.GO_TO_NEXT_STEP == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_punish_too_little_players(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_punishments=2,
        punish_interval_seconds=60,
        min_server_players_for_punish=60,
    )
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.WAIT == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_punish_disabled(team_view):
    config = AutoModNoSoloTankUserConfig(
        number_of_punishments=0,
        punish_interval_seconds=0,
        min_server_players_for_punish=0,
    )
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_punish_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_shouldnt_kick_without_punish(team_view):
    config = AutoModNoSoloTankUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=0,
        min_server_players_for_kick=0,
    )
    mod = NoSoloTankAutomod(config, None)

    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)

    assert PunishStepState.DISABLED == mod.should_kick_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())
    assert PunishStepState.APPLY == mod.should_kick_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_shouldnt_kick_disabled(team_view):
    config = AutoModNoSoloTankUserConfig(
        kick_after_max_punish=False,
        kick_grace_period_seconds=0,
        min_server_players_for_kick=0,
    )
    mod = NoSoloTankAutomod(config, None)
    # baker squad is a solo tank squad, w/ SL
    watch_status = WatchStatus()
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.DISABLED == mod.should_kick_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_should_wait_kick(team_view):
    config = AutoModNoSoloTankUserConfig(
        kick_after_max_punish=True,
        kick_grace_period_seconds=1,
        min_server_players_for_kick=0,
    )
    mod = NoSoloTankAutomod(config, None)
    watch_status = WatchStatus()
    # baker squad is a solo tank squad, w/ SL
    player = team_view["allies"]["squads"]["baker"]["players"][0]
    aplayer = construct_aplayer(player)
    watch_status.punished.setdefault(player["name"], []).append(datetime.now())

    assert PunishStepState.WAIT == mod.should_kick_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    assert PunishStepState.WAIT == mod.should_kick_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )
    time.sleep(1)
    assert PunishStepState.APPLY == mod.should_kick_player(
        watch_status,
        team_view,
        "baker",
        team_view["allies"]["squads"]["baker"],
        aplayer,
    )


def test_default_config():
    config = AutoModNoSoloTankUserConfig.load_from_db()
    assert config.enabled == False

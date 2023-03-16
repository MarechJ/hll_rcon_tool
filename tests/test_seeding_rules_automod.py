import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from _pytest.fixtures import fixture

from rcon.automods.get_team_count import get_team_count
from rcon.automods.models import (
    AnnounceSeedingActiveConfig,
    DisallowedRolesConfig,
    DisallowedWeaponConfig,
    NoSeedingViolation,
    PunishDetails,
    PunishPlayer,
    PunitionsToApply,
    SeedingRulesConfig,
    WatchStatus, EnforceCapFightConfig,
)
from rcon.automods.seeding_rules import SeedingRulesAutomod
from rcon.types import StructuredLogLineType, GameState

state = {}
redis_store = {}


@fixture
def team_view():
    global state, redis_store
    state = {}
    redis_store = {}
    return {
        "allies": {
            "combat": 0,
            "commander": {
                "combat": 50,
                "country": "",
                "deaths": 6,
                "defense": 500,
                "is_vip": False,
                "kills": 6,
                "level": 123,
                "loadout": "standard issue",
                "name": "FamousCommander",
                "offense": 480,
                "profile": None,
                "role": "armycommander",
                "steam_bans": None,
                "steam_id_64": "76561198206929556",
                "support": 264,
                "team": "allies",
                "unit_id": -1,
                "unit_name": "Commander",
            },
            "count": 0,
            "deaths": 0,
            "defense": 0,
            "kills": 0,
            "offense": 0,
            "squads": {
                "able": {
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
                            "loadout": "standard issue",
                            "name": "WilliePeter",
                            "offense": 480,
                            "profile": None,
                            "role": "tankcommander",
                            "steam_bans": None,
                            "steam_id_64": "76561198206929555",
                            "support": 264,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "able",
                        },
                        {
                            "combat": 50,
                            "country": "",
                            "deaths": 6,
                            "defense": 500,
                            "is_vip": False,
                            "kills": 6,
                            "level": 123,
                            "loadout": "standard issue",
                            "name": "AnotherPeter",
                            "offense": 480,
                            "profile": None,
                            "role": "crewman",
                            "steam_bans": None,
                            "steam_id_64": "76561198206929556",
                            "support": 264,
                            "team": "allies",
                            "unit_id": 1,
                            "unit_name": "able",
                        },
                    ],
                    "support": 264,
                    "type": "armor",
                },
            },
            "support": 0,
        },
        "axis": {
            "combat": 0,
            "commander": {},
            "count": 0,
            "deaths": 0,
            "defense": 0,
            "kills": 0,
            "offense": 0,
            "squads": {
                "able": {
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
                    ],
                    "support": 264,
                    "type": "infantry",
                },
            },
            "support": 7323,
        },
    }


game_state: GameState = {
    'allied_score': 3,
    'axis_score': 2,
    'current_map': '',
    'next_map': '',
    'num_allied_players': 30,
    'num_axis_players': 30,
    'time_remaining': timedelta(10),
}

line = "[29:42 min (1606340690)] KILL: [CPC] [1.Fjg] FlorianSW(Allies/76561198012102485) -> Karadoc(Axis/76561198080212634) with MK2_Grenade"
lt = datetime.fromtimestamp(1606340690)
kill_event_log: StructuredLogLineType = {
    "version": 1,
    "timestamp_ms": int(lt.timestamp() * 1000),
    "relative_time_ms": (lt - datetime.now()).total_seconds() * 1000,
    "raw": line,
    "line_without_time": "",
    "action": "KILL",
    "player": "[1.Fjg] FlorianSW",
    "steam_id_64_1": "76561198012102485",
    "player2": "Karadoc",
    "steam_id_64_2": "76561198080212634",
    "weapon": "MP40",
    "message": "",
    "sub_content": "",
}

expected_warned_players = [
    PunishPlayer(
        steam_id_64="76561198206929555",
        name="WilliePeter",
        squad="able",
        team="allies",
        role="tankcommander",
        lvl=123,
        details=PunishDetails(
            author="SeedingRulesAutomod",
            message="",
            discord_audit_url="",
            dry_run=False,
        ),
    ),
    PunishPlayer(
        steam_id_64="76561198206929556",
        name="AnotherPeter",
        squad="able",
        team="allies",
        role="crewman",
        lvl=123,
        details=PunishDetails(
            author="SeedingRulesAutomod",
            message="",
            discord_audit_url="",
            dry_run=False,
        ),
    ),
]


@contextmanager
def fake_state(team, squad_name):
    try:
        yield state.setdefault(f"{team}{squad_name}", WatchStatus())
    except NoSeedingViolation:
        del state[f"{team}{squad_name}"]


def fake_setex(k, _, v):
    redis_store[k] = v


def fake_get(k):
    return redis_store.get(k)


def fake_exists(k):
    return redis_store.get(k, None) is not None


def fake_delete(ks: str):
    redis_store.pop(ks, None)


def mod_with_config(c: SeedingRulesConfig) -> SeedingRulesAutomod:
    mod = SeedingRulesAutomod(c, Mock())
    mod.red.setex = fake_setex
    mod.red.delete = fake_delete
    mod.red.get = fake_get
    mod.red.exists = fake_exists
    mod.watch_state = fake_state
    return mod


def test_does_nothing_when_enough_players(team_view):
    mod = mod_with_config(
        SeedingRulesConfig(
            disallowed_roles=DisallowedRolesConfig(
                roles={"tankcommander": "Tanks", "crewman": "Tanks"},
                max_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            - 1,
            ),
            disallowed_weapons=DisallowedWeaponConfig(
                weapons={"MP40": "MP40"},
                min_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            - 1,
            ),
        )
    )

    assert PunitionsToApply() == mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert PunitionsToApply() == mod.on_kill(kill_event_log)


def test_does_nothing_when_not_enough_players(team_view):
    mod = mod_with_config(
        SeedingRulesConfig(
            disallowed_roles=DisallowedRolesConfig(
                roles={"tankcommander": "Tanks", "crewman": "Tanks"},
                min_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            + 1,
            ),
            disallowed_weapons=DisallowedWeaponConfig(
                weapons={"MP40": "MP40"},
                min_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            + 1,
            ),
        )
    )

    assert PunitionsToApply() == mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert PunitionsToApply() == mod.on_kill(kill_event_log)


def test_cycles_warn_punish_kick_armor_players(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=True,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        disallowed_roles=DisallowedRolesConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        + 1,
            roles={"tankcommander": "Tanks", "crewman": "Tanks"},
        ),
    )
    mod = mod_with_config(config)

    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert expected_warned_players == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.warning_interval_seconds)

    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert expected_warned_players == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.kick_grace_period_seconds)

    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert expected_warned_players == punitions.kick


def test_cycles_warn_punish_kick_cap_fight_players(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=True,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        enforce_cap_fight=EnforceCapFightConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        + 1,
            min_players=0,
            max_caps=3,
        ),
    )
    mod = mod_with_config(config)
    mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state)

    team_view["allies"]["squads"]["able"]['players'][0]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [expected_warned_players[0]] == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.warning_interval_seconds)

    team_view["allies"]["squads"]["able"]['players'][0]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert [expected_warned_players[0]] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.kick_grace_period_seconds)

    team_view["allies"]["squads"]["able"]['players'][0]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert [expected_warned_players[0]] == punitions.kick


def test_punishes_commander_cap_fight(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=True,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        enforce_cap_fight=EnforceCapFightConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        + 1,
            min_players=0,
            max_caps=3,
        ),
    )
    mod = mod_with_config(config)
    mod.punitions_to_apply(team_view, "Commander", "allies", {
        "players": [team_view["allies"]["commander"]]
    }, game_state)

    team_view["allies"]["commander"]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "Commander", "allies", {
            "players": [team_view["allies"]["commander"]]
        }, game_state
    )

    assert [PunishPlayer(
        steam_id_64="76561198206929556",
        name="FamousCommander",
        squad="Commander",
        team="allies",
        role="armycommander",
        lvl=123,
        details=PunishDetails(
            author="SeedingRulesAutomod",
            message="",
            discord_audit_url="",
            dry_run=False,
        ),
    )] == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.warning_interval_seconds)


def test_skips_warning_when_disabled(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=True,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        enforce_cap_fight=EnforceCapFightConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        + 1,
            skip_warning=True,
            min_players=0,
            max_caps=3,
        ),
    )
    mod = mod_with_config(config)
    mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state)

    team_view["allies"]["squads"]["able"]['players'][0]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert [expected_warned_players[0]] == punitions.punish
    assert [] == punitions.kick


def test_does_nothing_when_cap_not_reached(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=True,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        enforce_cap_fight=EnforceCapFightConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        + 1,
            max_caps=game_state['allied_score'] + 1,
        ),
    )
    mod = mod_with_config(config)
    mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state)

    team_view["allies"]["squads"]["able"]['players'][0]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick


def test_stops_when_players_reached(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=True,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        enforce_cap_fight=EnforceCapFightConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        - 1,
            max_caps=3,
        ),
    )
    mod = mod_with_config(config)
    mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state)

    team_view["allies"]["squads"]["able"]['players'][0]['offense'] += 1
    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick


def test_stops_when_no_violations_anymore(team_view):
    config = SeedingRulesConfig(
        number_of_warning=1,
        warning_interval_seconds=1,
        number_of_punish=1,
        punish_interval_seconds=1,
        warning_message="",
        punish_message="",
        kick_after_max_punish=False,
        kick_message="",
        kick_grace_period_seconds=1,
        discord_webhook_url="",
        disallowed_roles=DisallowedRolesConfig(
            max_players=get_team_count(team_view, "allies")
                        + get_team_count(team_view, "axis")
                        + 1,
            roles={"tankcommander": "Tanks", "crewman": "Tanks"},
        ),
    )
    mod = mod_with_config(config)

    punitions = mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )
    assert expected_warned_players == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.warning_interval_seconds)

    able = team_view["allies"]["squads"]["able"]
    for p in able["players"]:
        p["role"] = "rifleman"
    punitions = mod.punitions_to_apply(team_view, "able", "allies", able, game_state)
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick


def test_punishes_when_weapon_disallowed(team_view):
    mod = mod_with_config(
        SeedingRulesConfig(
            disallowed_weapons=DisallowedWeaponConfig(
                weapons={"MP40": "MP40"},
                min_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            - 1,
                max_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            + 1,
            ),
        )
    )
    mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )

    punitions = mod.on_kill(kill_event_log)
    assert 1 == len(punitions.punish)


def test_does_not_punish_when_weapon_allowed(team_view):
    mod = mod_with_config(
        SeedingRulesConfig(
            disallowed_weapons=DisallowedWeaponConfig(
                weapons={"MK2_Grenade": "Grenade"},
                min_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            - 1,
                max_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            + 1,
            ),
        )
    )
    mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )

    punitions = mod.on_kill(kill_event_log)
    assert 0 == len(punitions.punish)


def test_announces_on_connect(team_view):
    mod = mod_with_config(
        SeedingRulesConfig(
            announce_seeding_active=AnnounceSeedingActiveConfig(
                enabled=True,
                message="",
            ),
            disallowed_weapons=DisallowedWeaponConfig(
                weapons={"MK2_Grenade": "Grenade"},
            ),
            disallowed_roles=DisallowedRolesConfig(
                roles={"tankcommander": "Tanks", "crewman": "Tanks"}
            ),
        )
    )

    punitions = mod.on_connected("A_NAME", "A_STEAM_ID")
    assert 1 == len(punitions.warning)


def test_does_not_announces_when_all_disabled(team_view):
    mod = mod_with_config(
        SeedingRulesConfig(
            announce_seeding_active=AnnounceSeedingActiveConfig(
                enabled=True,
                message="",
            ),
            disallowed_weapons=DisallowedWeaponConfig(
                weapons={"MK2_Grenade": "Grenade"},
                max_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            - 1,
            ),
            disallowed_roles=DisallowedRolesConfig(
                roles={"tankcommander": "Tanks", "crewman": "Tanks"},
                max_players=get_team_count(team_view, "allies")
                            + get_team_count(team_view, "axis")
                            - 1,
            ),
        )
    )
    mod.punitions_to_apply(
        team_view, "able", "allies", team_view["allies"]["squads"]["able"], game_state
    )

    punitions = mod.on_connected("A_NAME", "A_STEAM_ID")
    assert 0 == len(punitions.warning)


def test_non_existing_roles_raises():
    with pytest.raises(ValueError):
        SeedingRulesConfig(
            disallowed_roles=DisallowedRolesConfig(roles={"does_not_exist": ""}),
        )

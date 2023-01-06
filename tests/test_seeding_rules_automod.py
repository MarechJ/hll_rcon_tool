import time
from contextlib import contextmanager
from unittest.mock import Mock

import pytest
from _pytest.fixtures import fixture

from rcon.automods.get_team_count import get_team_count
from rcon.automods.models import SeedingRulesConfig, PunitionsToApply, DisallowedRolesConfig, PunishDetails, \
    PunishPlayer, NoSeedingViolation, WatchStatus
from rcon.automods.seeding_rules import SeedingRulesAutomod

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


expected_warned_players = [PunishPlayer(
    steam_id_64="76561198206929555",
    name="WilliePeter",
    squad="able",
    team="allies",
    role="tankcommander",
    lvl=123,
    details=PunishDetails(author='SeedingRulesAutomod', message='', discord_audit_url='', dry_run=False),
), PunishPlayer(
    steam_id_64="76561198206929556",
    name="AnotherPeter",
    squad="able",
    team="allies",
    role="crewman",
    lvl=123,
    details=PunishDetails(author='SeedingRulesAutomod', message='', discord_audit_url='', dry_run=False),
)]


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


def fake_delete(ks: list[str]):
    for k in ks:
        del redis_store[k]


def mod_with_config(c: SeedingRulesConfig) -> SeedingRulesAutomod:
    mod = SeedingRulesAutomod(c, Mock())
    mod.red.setex = fake_setex
    mod.red.delete = fake_delete
    mod.red.get = fake_get
    mod.watch_state = fake_state
    return mod


def test_does_nothing_when_enough_players(team_view):
    mod = mod_with_config(SeedingRulesConfig(
        disallowed_roles=DisallowedRolesConfig(
            roles={"tankcommander": "Tanks", "crewman": "Tanks"},
            max_players=get_team_count(team_view, "allies") + get_team_count(team_view, "axis") - 1,
        ),
    ))

    assert PunitionsToApply() == mod.punitions_to_apply(team_view, "able", "allies",
                                                        team_view["allies"]["squads"]["able"])


def test_does_nothing_when_not_enough_players(team_view):
    mod = mod_with_config(SeedingRulesConfig(
        disallowed_roles=DisallowedRolesConfig(
            roles={"tankcommander": "Tanks", "crewman": "Tanks"},
            min_players=get_team_count(team_view, "allies") + get_team_count(team_view, "axis") + 1,
        ),
    ))

    assert PunitionsToApply() == mod.punitions_to_apply(team_view, "able", "allies",
                                                        team_view["allies"]["squads"]["able"])


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
            max_players=get_team_count(team_view, "allies") + get_team_count(team_view, "axis") + 1,
            roles={"tankcommander": "Tanks", "crewman": "Tanks"}
        ),
    )
    mod = mod_with_config(config)

    punitions = mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"])
    assert expected_warned_players == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.warning_interval_seconds)

    punitions = mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"])
    assert [] == punitions.warning
    assert expected_warned_players == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.kick_grace_period_seconds)

    punitions = mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"])
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert expected_warned_players == punitions.kick


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
            max_players=get_team_count(team_view, "allies") + get_team_count(team_view, "axis") + 1,
            roles={"tankcommander": "Tanks", "crewman": "Tanks"}
        ),
    )
    mod = mod_with_config(config)

    punitions = mod.punitions_to_apply(team_view, "able", "allies", team_view["allies"]["squads"]["able"])
    assert expected_warned_players == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick
    time.sleep(config.warning_interval_seconds)

    able = team_view["allies"]["squads"]["able"]
    for p in able["players"]:
        p["role"] = "rifleman"
    punitions = mod.punitions_to_apply(team_view, "able", "allies", able)
    assert [] == punitions.warning
    assert [] == punitions.punish
    assert [] == punitions.kick


def test_non_existing_roles_raises():
    with pytest.raises(ValueError):
        SeedingRulesConfig(
            disallowed_roles=DisallowedRolesConfig(
                roles={"does_not_exist": ""}
            ),
        )

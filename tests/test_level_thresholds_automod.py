from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import Mock

from rcon.automods.level_thresholds import LevelThresholdsAutomod
from rcon.automods.models import NoLevelViolation, WatchStatus
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig, Role, Roles
from tests.test_utils import mock_get_detailed_player

state = {}
redis_store = {}


def raw_time_from_timedelta(td: timedelta) -> str:
    seconds = td.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


@contextmanager
def fake_state(team, squad_name):
    try:
        yield state.setdefault(f"{team}{squad_name}", WatchStatus())
    except NoLevelViolation:
        del state[f"{team}{squad_name}"]


def fake_setex(k, _, v):
    redis_store[k] = v


def fake_get(k):
    return redis_store.get(k)


def fake_exists(k):
    return redis_store.get(k, None) is not None


def fake_delete(ks: str):
    redis_store.pop(ks, None)


def mod_with_config(c: AutoModLevelUserConfig) -> LevelThresholdsAutomod:
    mod = LevelThresholdsAutomod(c, Mock())
    mod.red.setex = fake_setex
    mod.red.delete = fake_delete
    mod.red.get = fake_get
    mod.red.exists = fake_exists
    mod.watch_state = fake_state
    return mod


def test_announces_on_connect_disabled():
    mod = mod_with_config(
        AutoModLevelUserConfig(
            enabled=True,
            announcement_enabled=False,
            only_announce_impacted_players=False,
            announcement_message="foo\n{min_level_msg}{max_level_msg}{level_thresholds_msg}\nbar",
        )
    )

    player = mock_get_detailed_player(
        name="A_NAME",
        player_id="A_STEAM_ID",
        level=1,
    )
    punitions = mod.on_connected(player["name"], player["player_id"], player)
    print(punitions)
    assert 0 == len(punitions.warning)


def test_announces_on_connect():
    mod = mod_with_config(
        AutoModLevelUserConfig(
            enabled=True,
            announcement_enabled=True,
            only_announce_impacted_players=False,
            announcement_message="message\n{min_level_msg}{max_level_msg}{level_thresholds_msg}",
            min_level=10,
            min_level_message="min level is {level}",
            max_level=100,
            max_level_message="max level is {level}",
            violation_message="{role} needs level {level}",
            level_thresholds={
                Roles.spotter: dict(label="Spotter", min_players=0, min_level=10)
            },
        )
    )

    player = mock_get_detailed_player(
        name="A_NAME",
        player_id="A_STEAM_ID",
        level=100,
    )
    punitions = mod.on_connected(player["name"], player["player_id"], player)
    print(punitions)
    assert 1 == len(punitions.warning)
    assert (
        "message\nmin level is 10\nmax level is 100\nSpotter needs level 10\n"
        == punitions.warning[0].details.message
    )


def test_announces_on_connect_partially_impacted():
    mod = mod_with_config(
        AutoModLevelUserConfig(
            enabled=True,
            announcement_enabled=True,
            only_announce_impacted_players=True,
            announcement_message="message\n{min_level_msg}{max_level_msg}{level_thresholds_msg}",
            min_level=10,
            min_level_message="min level is {level}",
            max_level=100,
            max_level_message="max level is {level}",
            violation_message="{role} needs level {level}",
            level_thresholds={
                Roles.spotter: dict(label="Spotter", min_players=0, min_level=50)
            },
        )
    )

    player = mock_get_detailed_player(
        name="A_NAME",
        player_id="A_STEAM_ID",
        level=20,
    )
    punitions = mod.on_connected(player["name"], player["player_id"], player)
    print(punitions)
    assert 1 == len(punitions.warning)
    assert "message\nSpotter needs level 50\n" == punitions.warning[0].details.message


def test_announces_on_connect_not_impacted():
    mod = mod_with_config(
        AutoModLevelUserConfig(
            enabled=True,
            announcement_enabled=True,
            only_announce_impacted_players=True,
            announcement_message="message\n{min_level_msg}{max_level_msg}{level_thresholds_msg}",
            min_level=10,
            min_level_message="min level is {level}",
            max_level=100,
            max_level_message="max level is {level}",
            violation_message="{role} needs level {level}",
            level_thresholds={
                Roles.spotter: dict(label="Spotter", min_players=0, min_level=10)
            },
        )
    )

    player = mock_get_detailed_player(
        name="A_NAME",
        player_id="A_STEAM_ID",
        level=100,
    )
    punitions = mod.on_connected(player["name"], player["player_id"], player)
    print(punitions)
    assert 0 == len(punitions.warning)


def test_announces_on_connect_detailed_player_info_is_none():
    mod = mod_with_config(
        AutoModLevelUserConfig(
            enabled=True,
            announcement_enabled=True,
            only_announce_impacted_players=True,
            announcement_message="message\n{min_level_msg}{max_level_msg}{level_thresholds_msg}",
            min_level=10,
            min_level_message="min level is {level}",
            max_level=100,
            max_level_message="max level is {level}",
            violation_message="{role} needs level {level}",
            level_thresholds={
                Roles.spotter: dict(label="Spotter", min_players=0, min_level=10)
            },
        )
    )

    player = None

    punitions = mod.on_connected("A_NAME", "A_STEAM_ID", player)
    print(punitions)
    assert 1 == len(punitions.warning)
    assert (
        "message\nmin level is 10\nmax level is 100\nSpotter needs level 10\n"
        == punitions.warning[0].details.message
    )

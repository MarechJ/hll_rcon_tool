import os
from contextlib import nullcontext
from types import SimpleNamespace

import fakeredis
import orjson
import pytest

os.environ["HLL_MAINTENANCE_CONTAINER"] = "1"
from rcon.cache_migrations import maps_history as maps_history_migrations
from rcon.cache_migrations.maps_history import (
    MAPS_HISTORY_SCHEMA_VERSION,
    _decode_map_info,
    _populated_database_numbers,
    migrate_map_info,
    migrate_maps_history,
)
from rcon.types import MapInfo, PlayerStat

LEGACY_MAP_VALUE = {
    "name": "stmariedumont_off_us",
    "start": 1786038619,
    "end": None,
    "guessed": False,
    "player_stats": {
        "76561198178339671": {
            "combat": 10,
            "p_combat": 0,
            "offense": 120,
            "p_offense": 0,
            "defense": 620,
            "p_defense": 0,
            "support": 435,
            "p_support": 0,
            "level": 276,
        }
    },
    "game_layout": {},
}
LEGACY_MAP = orjson.dumps(LEGACY_MAP_VALUE)


def test_version_zero_map_is_normalized_to_current_schema():
    # temp.txt contains redis-cli output, where the JSON value is itself quoted.
    item = migrate_map_info(_decode_map_info(orjson.dumps(LEGACY_MAP.decode())))

    assert item["_schema_version"] == MAPS_HISTORY_SCHEMA_VERSION
    assert MapInfo.__required_keys__ <= item.keys()
    assert item["game_layout"] == {"requested": [], "set": []}
    assert item["cap_flips"] == []
    assert item["match_time"] == 0

    player_id = "76561198178339671"
    player = item["player_stats"][player_id]
    assert PlayerStat.__required_keys__ <= player.keys()
    assert player["combat"] == 10
    assert player["names"] == [player_id]
    assert player["status"] == "offline"
    assert player["p_unit"] == {
        "ts": 0,
        "team": -111,
        "squad": -111,
        "role": -111,
    }
    assert player["units"] == []


def test_map_normalization_is_idempotent():
    migrated = migrate_map_info(orjson.loads(LEGACY_MAP))

    assert migrate_map_info(migrated) == migrated
    assert migrate_map_info(orjson.loads(orjson.dumps(migrated))) == migrated


def test_newer_map_schema_is_rejected():
    with pytest.raises(ValueError, match="newer CRCON version"):
        migrate_map_info({"_schema_version": MAPS_HISTORY_SCHEMA_VERSION + 1})


def test_redis_migration_is_atomic_and_does_not_replace_backup_on_restart():
    client = fakeredis.FakeRedis()
    client.lock = lambda *args, **kwargs: nullcontext()
    raw_item = LEGACY_MAP
    client.rpush("maps_history", raw_item)
    history = SimpleNamespace(red=client, key="maps_history", max_len=500)

    assert migrate_maps_history(history) == 1
    assert orjson.loads(client.lindex("maps_history", 0))["_schema_version"] == 1
    backup = client.lrange("maps_history:backup_previous", 0, -1)
    assert backup == [raw_item]

    assert migrate_maps_history(history) == 0
    assert client.lrange("maps_history:backup_previous", 0, -1) == backup


def test_schema_marker_skips_reading_items_on_later_maintenance_runs():
    client = fakeredis.FakeRedis()
    client.lock = lambda *args, **kwargs: nullcontext()
    client.set("maps_history:schema_version", MAPS_HISTORY_SCHEMA_VERSION)
    client.rpush("maps_history", b"not json")
    history = SimpleNamespace(red=client, key="maps_history", max_len=500)

    assert migrate_maps_history(history) == 0


def test_populated_database_discovery_includes_all_server_databases():
    client = fakeredis.FakeRedis(db=3)
    client.info = lambda section: {
        "db1": {"keys": 2},
        "db7": {"keys": 4},
    }

    assert _populated_database_numbers(client) == [1, 3, 7]


def test_maintenance_migrates_maps_history_in_every_populated_database(monkeypatch):
    discovery_client = fakeredis.FakeRedis(db=0)
    discovery_client.info = lambda section: {
        "db1": {"keys": 1},
        "db7": {"keys": 1},
    }
    clients = {database: fakeredis.FakeRedis(db=database) for database in (0, 1, 7)}
    for database in (1, 7):
        clients[database].rpush("maps_history", LEGACY_MAP)
        clients[database].lock = lambda *args, **kwargs: nullcontext()

    monkeypatch.setattr(
        maps_history_migrations.redis.Redis,
        "from_url",
        lambda redis_url: discovery_client,
    )
    monkeypatch.setattr(
        maps_history_migrations,
        "_redis_client_for_database",
        lambda client, database: clients[database],
    )

    assert maps_history_migrations.migrate_all_maps_histories("redis://unused") == (
        2,
        2,
    )
    for database in (1, 7):
        assert (
            orjson.loads(clients[database].lindex("maps_history", 0))["_schema_version"]
            == MAPS_HISTORY_SCHEMA_VERSION
        )

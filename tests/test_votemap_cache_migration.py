import pickle
from contextlib import nullcontext
from unittest.mock import patch

import fakeredis
import pytest

from rcon.cache_migrations import votemap as votemap_migrations
from rcon.cache_migrations.votemap import (
    LEGACY_VOTEMAP_KEYS,
    VOTEMAP_TRANSIENT_KEYS,
    migrate_all_votemap_states,
    migrate_votemap_state,
)
from rcon.maps import LAYERS
from rcon.vote_map import VotemapState
from rcon.vote_map.storage import VOTEMAP_SCHEMA_VERSION, VotemapKeys


def _client(database: int = 0) -> fakeredis.FakeRedis:
    client = fakeredis.FakeRedis(db=database)
    client.lock = lambda *args, **kwargs: nullcontext()
    return client


def test_v0_migration_preserves_legacy_whitelist_and_clears_unused_keys():
    client = _client()
    layers = iter(LAYERS.values())
    first_layer = next(layers)
    second_layer = next(layers)
    whitelist = {first_layer.id, second_layer.id}
    client.set("votemap_whitelist", pickle.dumps({first_layer, second_layer.id}))
    client.set("last_vote_reminder", b"old reminder")
    client.hset("VOTES", "player", "map")
    client.rpush("MAP_SELECTION", "map")
    client.set(VotemapKeys.VERSION, "0.2")
    for key in VOTEMAP_TRANSIENT_KEYS:
        client.set(key, b"stale")
    client.rpush(VotemapKeys.RESULT_HISTORY, b"preserved history")

    assert migrate_votemap_state(client) is True

    assert client.get(VotemapKeys.VERSION) == str(VOTEMAP_SCHEMA_VERSION).encode()
    assert {
        value.decode() for value in client.smembers(VotemapKeys.MAP_WHITELIST)
    } == whitelist
    assert not any(client.exists(key) for key in LEGACY_VOTEMAP_KEYS)
    assert not any(client.exists(key) for key in VOTEMAP_TRANSIENT_KEYS)
    assert client.lrange(VotemapKeys.RESULT_HISTORY, 0, -1) == [b"preserved history"]


def test_v0_migration_prefers_an_existing_prefixed_whitelist():
    client = _client()
    prefixed_map = next(iter(LAYERS.values())).id
    legacy_map = next(iter(list(LAYERS.values())[1:])).id
    client.sadd(VotemapKeys.MAP_WHITELIST, prefixed_map)
    client.set("votemap_whitelist", pickle.dumps({legacy_map}))

    assert migrate_votemap_state(client) is True
    assert client.smembers(VotemapKeys.MAP_WHITELIST) == {prefixed_map.encode()}


def test_v1_migration_is_idempotent():
    client = _client()
    client.set(VotemapKeys.VERSION, VOTEMAP_SCHEMA_VERSION)
    client.set(VotemapKeys.NEXT_MAP, b"keep-on-v1")

    assert migrate_votemap_state(client) is False
    assert client.get(VotemapKeys.NEXT_MAP) == b"keep-on-v1"


def test_newer_schema_version_is_rejected():
    client = _client()
    client.set(VotemapKeys.VERSION, VOTEMAP_SCHEMA_VERSION + 1)

    with pytest.raises(ValueError, match="newer CRCON version"):
        migrate_votemap_state(client)


def test_malformed_prefixed_whitelist_is_replaced_from_legacy_data():
    client = _client()
    legacy_map = next(iter(LAYERS.values())).id
    client.set(VotemapKeys.MAP_WHITELIST, b"not a Redis set")
    client.set("votemap_whitelist", pickle.dumps({legacy_map}))

    assert migrate_votemap_state(client) is True
    assert client.smembers(VotemapKeys.MAP_WHITELIST) == {legacy_map.encode()}


def test_votemap_state_instantiation_does_not_run_migrations():
    client = _client()
    client.set(VotemapKeys.NEXT_MAP, b"keep-until-maintenance")

    with patch("rcon.vote_map.state.get_redis_client", return_value=client):
        VotemapState()

    assert client.get(VotemapKeys.NEXT_MAP) == b"keep-until-maintenance"
    assert client.get(VotemapKeys.VERSION) is None


def test_maintenance_migrates_votemap_state_in_every_populated_database(monkeypatch):
    discovery_client = _client()
    discovery_client.info = lambda section: {
        "db1": {"keys": 2},
        "db7": {"keys": 4},
    }
    clients = {database: _client(database) for database in (0, 1, 7)}

    monkeypatch.setattr(
        votemap_migrations.redis.Redis,
        "from_url",
        lambda _: discovery_client,
    )
    monkeypatch.setattr(
        votemap_migrations,
        "redis_client_for_database",
        lambda _client, database: clients[database],
    )

    assert migrate_all_votemap_states("redis://unused/0") == (3, 3)
    assert all(client.get(VotemapKeys.VERSION) == b"1" for client in clients.values())

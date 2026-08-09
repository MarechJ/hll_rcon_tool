"""
When creating subsequent migrations
def _migrate_to_v2(value: Mapping[str, Any]) -> dict[str, Any]:
    item = dict(value)

    item.setdefault("new_map_field", [])
    for player_stat in item.get("player_stats", {}).values():
        player_stat.setdefault("new_player_field", 0)

    item["_schema_version"] = 2
    return item


MAP_INFO_MIGRATIONS = {
    1: _migrate_to_v1,
    2: _migrate_to_v2,
}
"""
import logging
import os
import uuid
from collections.abc import Mapping
from types import SimpleNamespace
from typing import Any, cast

import orjson
import redis

from rcon.types import MapInfo

logger = logging.getLogger(__name__)



MAPS_HISTORY_SCHEMA_VERSION = 1
MAPS_HISTORY_SCHEMA_KEY_SUFFIX = "schema_version"
MAPS_HISTORY_MIGRATION_LOCK_SUFFIX = "migration_lock"
MAPS_HISTORY_BACKUP_SUFFIX = "backup_previous"
MAPS_HISTORY_BACKUP_TTL_SECONDS = 7 * 24 * 60 * 60


def _migrate_player_stat_v1(player_id: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Invalid maps_history player_stats entry for {player_id!r}")

    stat = dict(value)
    defaults = {
        "vehicle_kills": 0,
        "p_vehicle_kills": 0,
        "vehicles_destroyed": 0,
        "p_vehicles_destroyed": 0,
        "kills_and_assists": 0,
        "p_kills_and_assists": 0,
        "deaths_and_redeploys": 0,
        "p_deaths_and_redeploys": 0,
        "units": [],
        "has_spawned": False,
    }
    for key, default in defaults.items():
        if stat.get(key) is None:
            stat[key] = default

    p_unit = dict(stat.get("p_unit") or {})
    p_unit.setdefault("ts", 0)
    p_unit.setdefault("team", -111)
    p_unit.setdefault("squad", -111)
    p_unit.setdefault("role", -111)
    stat["p_unit"] = p_unit

    p_coord = dict(stat.get("p_coord") or {})
    p_coord.setdefault("x", 0.0)
    p_coord.setdefault("y", 0.0)
    p_coord.setdefault("z", 0.0)
    stat["p_coord"] = p_coord

    names = stat.get("names")
    if not isinstance(names, list) or not names:
        stat["names"] = [player_id]

    if stat.get("status") not in {"online", "offline", "idle"}:
        stat["status"] = "offline"

    return stat


def _migrate_to_v1(value: Mapping[str, Any]) -> dict[str, Any]:
    item = dict(value)

    player_stats = item.get("player_stats")
    if player_stats is None:
        player_stats = {}
    if not isinstance(player_stats, Mapping):
        raise ValueError("Invalid maps_history player_stats value")
    item["player_stats"] = {
        str(player_id): _migrate_player_stat_v1(str(player_id), stat)
        for player_id, stat in player_stats.items()
    }

    game_layout = item.get("game_layout")
    if not isinstance(game_layout, Mapping):
        game_layout = {}
    game_layout = dict(game_layout)
    game_layout.setdefault("requested", [])
    game_layout.setdefault("set", [])
    item["game_layout"] = game_layout

    if not isinstance(item.get("cap_flips"), list):
        item["cap_flips"] = []
    if not isinstance(item.get("match_time"), int):
        item["match_time"] = 0
    item["_schema_version"] = 1
    return item


MAP_INFO_MIGRATIONS = {
    1: _migrate_to_v1,
}


def migrate_map_info(value: Any) -> MapInfo:
    """Return a current MapInfo without mutating the supplied cached value."""
    if not isinstance(value, Mapping):
        raise ValueError("Invalid maps_history item")

    item = dict(value)
    version = item.get("_schema_version", 0)
    if not isinstance(version, int) or version < 0:
        raise ValueError(f"Invalid maps_history schema version: {version!r}")
    if version > MAPS_HISTORY_SCHEMA_VERSION:
        raise ValueError(
            "maps_history was written by a newer CRCON version "
            f"({version} > {MAPS_HISTORY_SCHEMA_VERSION})"
        )

    for target_version in range(version + 1, MAPS_HISTORY_SCHEMA_VERSION + 1):
        item = MAP_INFO_MIGRATIONS[target_version](item)
    return cast(MapInfo, item)


def _decode_map_info(data: bytes | str) -> Any:
    value = orjson.loads(data)
    # Accept redis-cli/diagnostic output that encoded the JSON item as a string.
    if isinstance(value, str):
        value = orjson.loads(value)
    return value


def migrate_maps_history(history: Any, max_retries: int = 3) -> int:
    """Atomically persist all MapsHistory items in the current schema.

    The maintenance container runs this before application containers start.
    It retains the original list for seven days as a rollback aid.
    """
    client = history.red
    key = history.key
    schema_key = f"{key}:{MAPS_HISTORY_SCHEMA_KEY_SUFFIX}"
    lock_key = f"{key}:{MAPS_HISTORY_MIGRATION_LOCK_SUFFIX}"
    backup_key = f"{key}:{MAPS_HISTORY_BACKUP_SUFFIX}"

    stored_version = client.get(schema_key)
    if stored_version is not None:
        stored_version = int(stored_version)
        if stored_version > MAPS_HISTORY_SCHEMA_VERSION:
            raise ValueError(
                "maps_history was migrated by a newer CRCON version "
                f"({stored_version} > {MAPS_HISTORY_SCHEMA_VERSION})"
            )
        if stored_version == MAPS_HISTORY_SCHEMA_VERSION:
            return 0

    with client.lock(lock_key, timeout=60, blocking_timeout=60):
        # A second maintenance process may have completed while this process
        # waited for the distributed lock.
        stored_version = client.get(schema_key)
        if stored_version is not None:
            stored_version = int(stored_version)
            if stored_version > MAPS_HISTORY_SCHEMA_VERSION:
                raise ValueError(
                    "maps_history was migrated by a newer CRCON version "
                    f"({stored_version} > {MAPS_HISTORY_SCHEMA_VERSION})"
                )
            if stored_version == MAPS_HISTORY_SCHEMA_VERSION:
                return 0

        for attempt in range(max_retries):
            temporary_key = f"{key}:migrating:{uuid.uuid4().hex}"
            try:
                with client.pipeline() as pipe:
                    pipe.watch(key)
                    raw_items = pipe.lrange(key, 0, -1)
                    decoded_items = [_decode_map_info(raw) for raw in raw_items]
                    normalized_items = [
                        migrate_map_info(item) for item in decoded_items
                    ]
                    migrated_items = [orjson.dumps(item) for item in normalized_items]
                    needs_rewrite = any(
                        original != normalized
                        for original, normalized in zip(decoded_items, normalized_items)
                    )

                    if not needs_rewrite:
                        pipe.unwatch()
                        client.set(schema_key, MAPS_HISTORY_SCHEMA_VERSION)
                        return 0

                    pipe.multi()
                    pipe.delete(temporary_key)
                    if migrated_items:
                        pipe.rpush(temporary_key, *migrated_items)
                        pipe.ltrim(temporary_key, 0, history.max_len - 1)
                        pipe.delete(backup_key)
                        pipe.rename(key, backup_key)
                        pipe.expire(backup_key, MAPS_HISTORY_BACKUP_TTL_SECONDS)
                        pipe.rename(temporary_key, key)
                    pipe.set(schema_key, MAPS_HISTORY_SCHEMA_VERSION)
                    pipe.execute()

                if migrated_items:
                    logger.info(
                        "Migrated %d maps_history items to schema version %d",
                        len(migrated_items),
                        MAPS_HISTORY_SCHEMA_VERSION,
                    )
                return len(migrated_items)
            except redis.WatchError:
                client.delete(temporary_key)
                if attempt + 1 == max_retries:
                    raise
                logger.warning("maps_history changed during migration; retrying")
            except Exception:
                client.delete(temporary_key)
                raise

    return 0


def _redis_client_for_database(client: redis.Redis, database: int) -> redis.Redis:
    connection_kwargs = dict(client.connection_pool.connection_kwargs)
    connection_kwargs["db"] = database
    return redis.Redis(connection_pool=redis.ConnectionPool(**connection_kwargs))


def _populated_database_numbers(client: redis.Redis) -> list[int]:
    databases = {int(client.connection_pool.connection_kwargs.get("db", 0))}
    for name in client.info("keyspace"):
        if isinstance(name, bytes):
            name = name.decode()
        if name.startswith("db") and name[2:].isdigit():
            databases.add(int(name[2:]))
    return sorted(databases)


def migrate_all_maps_histories(redis_url: str) -> tuple[int, int]:
    """Migrate maps_history in every populated logical Redis database."""
    discovery_client = redis.Redis.from_url(redis_url)
    database_count = 0
    item_count = 0
    try:
        for database in _populated_database_numbers(discovery_client):
            client = _redis_client_for_database(discovery_client, database)
            try:
                if not client.exists("maps_history"):
                    continue
                database_count += 1
                item_count += migrate_maps_history(
                    SimpleNamespace(red=client, key="maps_history", max_len=500)
                )
            finally:
                client.close()
    finally:
        discovery_client.close()

    logger.info(
        "maps_history migration checked %d Redis database(s) and migrated %d item(s)",
        database_count,
        item_count,
    )
    return database_count, item_count


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("HLL_REDIS_URL")
    if not redis_url:
        raise RuntimeError("HLL_REDIS_URL is required to migrate maps_history")
    migrate_all_maps_histories(redis_url)


if __name__ == "__main__":
    main()

"""Versioned migration for durable votemap Redis state."""

import logging
import os
import pickle
from collections.abc import Iterable
from typing import Any

import redis

from rcon import maps
from rcon.cache_migrations.redis_databases import (
    populated_database_numbers,
    redis_client_for_database,
)
from rcon.vote_map.storage import VOTEMAP_SCHEMA_VERSION, VotemapKeys

logger = logging.getLogger(__name__)


VOTEMAP_MIGRATION_LOCK_KEY = "votemap:migration-lock"

LEGACY_VOTEMAP_WHITELIST_KEY = "votemap_whitelist"
LEGACY_VOTEMAP_KEYS = (
    "last_vote_reminder",
    LEGACY_VOTEMAP_WHITELIST_KEY,
    "VOTES",
    "MAP_SELECTION",
)

VOTEMAP_TRANSIENT_KEYS = (
    VotemapKeys.LATEST_REMINDER,
    VotemapKeys.MAP_SELECTION,
    VotemapKeys.VOTES,
    VotemapKeys.ADMIN_NEXT_MAP,
    VotemapKeys.PLAYER_CHOICE,
    VotemapKeys.NEXT_MAP,
)


def _map_ids(values: Iterable[Any]) -> set[str]:
    map_ids = set()
    for value in values:
        if isinstance(value, bytes):
            value = value.decode()
        map_ids.add(maps.parse_layer(value).id)
    return map_ids


def _legacy_whitelist(client: redis.Redis) -> set[str] | None:
    raw = client.get(LEGACY_VOTEMAP_WHITELIST_KEY)
    if raw is None:
        return None

    try:
        values = pickle.loads(raw)
        if not isinstance(values, Iterable) or isinstance(values, (str, bytes)):
            raise ValueError("legacy votemap whitelist is not an iterable of maps")
        return _map_ids(values)
    except Exception:
        logger.exception(
            "Unable to migrate %s; the votemap whitelist will be reset on use",
            LEGACY_VOTEMAP_WHITELIST_KEY,
        )
        return None


def _stored_schema_version(client: redis.Redis) -> int:
    raw = client.get(VotemapKeys.VERSION)
    if raw is None:
        return 0

    try:
        version = int(raw)
    except (TypeError, ValueError):
        # Development versions of the unreleased state used values such as
        # 0.2. They are all the legacy v0 layout for migration purposes.
        return 0

    if version > VOTEMAP_SCHEMA_VERSION:
        raise ValueError(
            "votemap state was migrated by a newer CRCON version "
            f"({version} > {VOTEMAP_SCHEMA_VERSION})"
        )
    return version if version == VOTEMAP_SCHEMA_VERSION else 0


def migrate_votemap_state(client: redis.Redis) -> bool:
    """Migrate one Redis database from the legacy votemap layout to version 1."""
    if _stored_schema_version(client) == VOTEMAP_SCHEMA_VERSION:
        return False

    with client.lock(VOTEMAP_MIGRATION_LOCK_KEY, timeout=60, blocking_timeout=60):
        if _stored_schema_version(client) == VOTEMAP_SCHEMA_VERSION:
            return False

        # A prefixed whitelist may already exist when migrating a development
        # build of the new feature. Prefer it over the legacy pickled value.
        has_prefixed_whitelist = client.type(VotemapKeys.MAP_WHITELIST) == b"set"
        whitelist = None if has_prefixed_whitelist else _legacy_whitelist(client)

        with client.pipeline(transaction=True) as pipe:
            pipe.delete(*VOTEMAP_TRANSIENT_KEYS, *LEGACY_VOTEMAP_KEYS)
            if not has_prefixed_whitelist:
                pipe.delete(VotemapKeys.MAP_WHITELIST)
                if whitelist is not None and whitelist:
                    pipe.sadd(VotemapKeys.MAP_WHITELIST, *sorted(whitelist))
            pipe.set(VotemapKeys.VERSION, VOTEMAP_SCHEMA_VERSION)
            pipe.execute()

    logger.info("Migrated votemap cache to schema version %d", VOTEMAP_SCHEMA_VERSION)
    return True


def migrate_all_votemap_states(redis_url: str) -> tuple[int, int]:
    """Migrate votemap state in every populated logical Redis database."""
    discovery_client = redis.Redis.from_url(redis_url)
    database_count = 0
    migration_count = 0
    try:
        for database in populated_database_numbers(discovery_client):
            client = redis_client_for_database(discovery_client, database)
            try:
                database_count += 1
                migration_count += int(migrate_votemap_state(client))
            finally:
                client.close()
    finally:
        discovery_client.close()

    logger.info(
        "votemap migration checked %d Redis database(s) and migrated %d",
        database_count,
        migration_count,
    )
    return database_count, migration_count


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("HLL_REDIS_URL")
    if not redis_url:
        raise RuntimeError("HLL_REDIS_URL is required to migrate votemap state")
    migrate_all_votemap_states(redis_url)


if __name__ == "__main__":
    main()

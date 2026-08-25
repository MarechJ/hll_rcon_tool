"""Helpers for running cache migrations across logical Redis databases."""

import redis


GLOBAL_REDIS_DATABASE = 0


def redis_client_for_database(client: redis.Redis, database: int) -> redis.Redis:
    connection_kwargs = dict(client.connection_pool.connection_kwargs)
    connection_kwargs["db"] = database
    return redis.Redis(connection_pool=redis.ConnectionPool(**connection_kwargs))


def populated_database_numbers(
    client: redis.Redis, *, include_global_database: bool = False
) -> list[int]:
    """Return populated Redis databases.

    Database 0 is shared global state and must be opted into explicitly. Cache
    migrations are server-scoped by default.
    """
    databases = {int(client.connection_pool.connection_kwargs.get("db", 0))}
    for name in client.info("keyspace"):
        if isinstance(name, bytes):
            name = name.decode()
        if name.startswith("db") and name[2:].isdigit():
            databases.add(int(name[2:]))
    if not include_global_database:
        databases.discard(GLOBAL_REDIS_DATABASE)
    return sorted(databases)

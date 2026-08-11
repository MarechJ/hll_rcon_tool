"""Helpers for running cache migrations across logical Redis databases."""

import redis


def redis_client_for_database(client: redis.Redis, database: int) -> redis.Redis:
    connection_kwargs = dict(client.connection_pool.connection_kwargs)
    connection_kwargs["db"] = database
    return redis.Redis(connection_pool=redis.ConnectionPool(**connection_kwargs))


def populated_database_numbers(client: redis.Redis) -> list[int]:
    databases = {int(client.connection_pool.connection_kwargs.get("db", 0))}
    for name in client.info("keyspace"):
        if isinstance(name, bytes):
            name = name.decode()
        if name.startswith("db") and name[2:].isdigit():
            databases.add(int(name[2:]))
    return sorted(databases)

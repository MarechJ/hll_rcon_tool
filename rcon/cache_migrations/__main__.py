"""Run all durable Redis migrations during maintenance startup."""

import logging
import os

from rcon.cache_migrations.maps_history import migrate_all_maps_histories
from rcon.cache_migrations.votemap import migrate_all_votemap_states


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    redis_url = os.environ.get("HLL_REDIS_URL")
    if not redis_url:
        raise RuntimeError("HLL_REDIS_URL is required to run cache migrations")

    migrate_all_maps_histories(redis_url)
    migrate_all_votemap_states(redis_url)


if __name__ == "__main__":
    main()

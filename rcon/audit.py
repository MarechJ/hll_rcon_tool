import json
import logging
from typing import List

from redis import BlockingConnectionPool, Redis

from rcon.cache_utils import get_redis_pool
from rcon.rcon import get_rcon
from rcon.types import AdminUserType

logger = logging.getLogger(__name__)

HEARTBEAT_KEY_PREFIX = "heartbeat_"
KNOWN_MODS_KEY = "mods"
PLAYER_ID = "player_id"

RED_POOL = None


def _red():
    # poor man's singleton
    red = get_redis_pool()
    global RED_POOL
    if not RED_POOL:
        RED_POOL = BlockingConnectionPool(max_connections=4)

    return Redis(connection_pool=red)


def _heartbeat_key(uniqueid):
    return f"{HEARTBEAT_KEY_PREFIX}{uniqueid}"


def heartbeat(username, player_id, timeout=120):
    red = _red()
    return red.setex(
        _heartbeat_key(username),
        timeout,
        json.dumps(dict(username=username, player_id=player_id)),
    )


# This exists only no to create a weird interdependancy / tight coupling with the API layer.
# Ideally we'd extract the services (i.e. broadcast, logs_event, etc) in a separated package, and let them
# use a service account to talk the the API.
def set_registered_mods(moderators_name_steamids: List[tuple]):
    red = _red()

    logger.warning("Registering mods: %s", moderators_name_steamids)

    red.delete("moderators")
    for k, v in moderators_name_steamids:
        red.hset("moderators", k, v)


def online_mods(rcon=None) -> list[AdminUserType]:
    red = _red()
    return [
        json.loads(red.get(u)) for u in red.scan_iter(f"{HEARTBEAT_KEY_PREFIX}*", 1)
    ]


def ingame_mods(rcon=None) -> list[AdminUserType]:
    red = _red()
    mods = red.hgetall("moderators") or {}

    if not mods:
        return []

    rcon = rcon or get_rcon()
    players = rcon.get_players()
    mods_ids = set(v.decode() for v in mods.values())
    ig_mods: list[AdminUserType] = []
    for player in players:
        if player[PLAYER_ID] in mods_ids:
            ig_mods.append({"username": player["name"], PLAYER_ID: player[PLAYER_ID]})

    return ig_mods


if __name__ == "__main__":
    heartbeat("test", "42")
    online = online_mods()
    print("online: ", online)
    set_registered_mods([("bla", "76561197984877751")])
    print(ingame_mods())

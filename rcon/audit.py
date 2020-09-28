from typing import List
from itertools import chain

from redis import Redis, BlockingConnectionPool

from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.cache_utils import get_redis_pool
import json

HEARTBEAT_KEY_PREFIX = 'heartbeat_'
KNOWN_MODS_KEY = 'mods'

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


def heartbeat(username, steam_id_64, timeout=120):
    red = _red()
    return red.setex(_heartbeat_key(username), timeout, json.dumps(dict(username=username, steam_id_64=steam_id_64)))


def online_mods():
    red = _red()

    return [json.loads(red.get(u)) for u in red.scan_iter(f"{HEARTBEAT_KEY_PREFIX}*", 1)]

# This exists only no to create a weird interdependancy / tight coupling with the API layer.
# Ideally we'd extract the services (i.e. broadcast, logs_event, etc) in a separated package, and let them
# use a service account to talk the the API. 
def set_registered_mods(moderators_name_steamids: List[tuple]):
    red = _red()

    for k, v in moderators_name_steamids:
        red.hset("moderators", k, v)
    

def ingame_mods():
    red = _red()
    mods = red.hgetall("moderators") or {}

    if not mods:
        return []

    rcon = RecordedRcon(SERVER_INFO)
    players = rcon.get_players()
    mods_ids = set(v.decode() for v in mods.values())
    ig_mods = []
    for player in players:
        if player['steam_id_64'] in mods_ids:
            ig_mods.append({"username": player["name"],  'steam_id_64': player['steam_id_64']})

    return ig_mods

if __name__ == "__main__":
    heartbeat("test", "42")
    online = online_mods()
    print("online: ", online)
    set_registered_mods([("bla", "76561197984877751")])
    print(ingame_mods())

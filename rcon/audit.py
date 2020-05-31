from redis import Redis

from rcon.cache_utils import get_redis_pool
import json

HEARTBEAT_KEY_PREFIX = 'heartbeat_'
KNOWN_MODS_KEY = 'mods'

def _red():
    red = get_redis_pool()
    red = Redis(connection_pool=red)
    return red

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
# user a service account to talk the the API. 
def set_registered_mods(steam_ids):
    if steam_ids:
        _red().sadd(KNOWN_MODS_KEY, *steam_ids)

def get_registered_mods():
    return  _red().smembers(KNOWN_MODS_KEY)


if __name__ == "__main__":
    heartbeat("test", "42")
    online = online_mods()
    print(online)
    assert "test" in online
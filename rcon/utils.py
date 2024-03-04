import inspect
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from itertools import islice
from typing import Any, Generic, Iterable, TypeVar

import redis

from rcon.cache_utils import get_redis_pool
from rcon.types import GetDetailedPlayer, MapInfo

logger = logging.getLogger("rcon")

STEAMID = "steam_id_64"
NAME = "name"
ROLE = "role"


class DefaultStringFormat(dict):
    """Base class for str.format usage to not crash with invalid keys"""

    def __missing__(self, key):
        logger.error("Invalid key=%s used in string format")
        return key


INDEFINITE_VIP_DATE = datetime(
    year=3000,
    month=1,
    day=1,
    tzinfo=timezone.utc,
)


ALL_ROLES = (
    "armycommander",
    "officer",
    "rifleman",
    "assault",
    "automaticrifleman",
    "medic",
    "support",
    "heavymachinegunner",
    "antitank",
    "engineer",
    "tankcommander",
    "crewman",
    "spotter",
    "sniper",
)

ALL_ROLES_KEY_INDEX_MAP = {v: i for i, v in enumerate(ALL_ROLES)}


def get_current_map(rcon):
    map_ = rcon.get_map()

    if map_.endswith("_RESTART"):
        map_ = map_.replace("_RESTART", "")

    return map_


T = TypeVar("T")


class FixedLenList(Generic[T]):
    def __init__(
        self, key, max_len=100, serializer=json.dumps, deserializer=json.loads
    ):
        self.red = redis.StrictRedis(connection_pool=get_redis_pool())
        self.max_len = max_len
        self.serializer = serializer
        self.deserializer = deserializer
        self.key = key

    def add(self, obj):
        self.red.lpush(self.key, self.serializer(obj))
        self.red.ltrim(self.key, 0, self.max_len - 1)

    def remove(self, obj):
        self.red.lrem(self.key, 0, self.serializer(obj))

    def update(self, index, obj):
        self.red.lset(self.key, index, self.serializer(obj))

    def __getitem__(self, index) -> T:
        if isinstance(index, slice):
            if index.step:
                raise ValueError("Step is not supported")
            end = index.stop or -1
            start = index.start or 0
            return [self.deserializer(o) for o in self.red.lrange(self.key, start, end)]
        val = self.red.lindex(self.key, index)
        if val is None:
            raise IndexError("Index out of bound")
        return self.deserializer(val)

    def lpop(self):
        val = self.red.lpop(self.key)
        if val is None:
            return val
        return self.deserializer(val)

    def lpush(self, obj):
        self.red.lpush(self.key, self.serializer(obj))

    def __iter__(self):
        for o in self.red.lrange(self.key, 0, -1):
            yield self.deserializer(o)

    def __len__(self):
        return self.red.llen(self.key)


class MapsHistory(FixedLenList[MapInfo]):
    def __init__(self, key="maps_history", max_len=500):
        super().__init__(key, max_len)

    def save_map_end(self, old_map=None, end_timestamp: int = None):
        ts = end_timestamp or datetime.now().timestamp()
        logger.info("Saving end of map %s at time %s", old_map, ts)
        prev = self.lpop() or MapInfo(
            name=old_map, start=None, end=None, guessed=True, player_stats=dict()
        )
        prev["end"] = ts
        self.lpush(prev)
        return prev

    def save_new_map(self, new_map, guessed=True, start_timestamp: int = None):
        ts = start_timestamp or datetime.now().timestamp()
        logger.info("Saving start of new map %s at time %s", new_map, ts)
        new = MapInfo(
            name=new_map, start=ts, end=None, guessed=guessed, player_stats=dict()
        )
        self.add(new)
        return new


class ApiKey:
    def __init__(self):
        num = os.getenv("SERVER_NUMBER")
        if not num:
            raise ValueError("SERVER_NUMBER variable is not set, can't start")

        REDIS_PARTS = {
            "HOST": os.getenv("HLL_REDIS_HOST"),
            "PORT": os.getenv("HLL_REDIS_PORT"),
        }

        if not REDIS_PARTS["HOST"]:
            raise ValueError("HLL_REDIS_HOST must be set")

        if not REDIS_PARTS["PORT"]:
            raise ValueError("HLL_REDIS_PORT must be set")

        self.red = redis.StrictRedis(
            host=REDIS_PARTS["HOST"], port=REDIS_PARTS["PORT"], db=0
        )
        self.key_prefix = "frontend_"
        self.key = f"{self.key_prefix}{num}"

    def generate_key(self):
        api_key = secrets.token_urlsafe(64)
        self.red.set(self.key, api_key)
        return api_key

    def get_key(self):
        key = self.red.get(self.key)
        if key:
            return key.decode()
        return key

    def delete_key(self):
        self.red.delete(self.key)

    def get_all_keys(self):
        return {
            k.decode(): self.red.get(k.decode()).decode()
            for k in self.red.keys(f"{self.key_prefix}*")
        }


def get_server_number() -> str:
    """Get the CRCON server number"""
    server_number = os.getenv("SERVER_NUMBER")
    if not server_number:
        # Shouldn't get here because SERVER_NUMBER is a mandatory ENV Var
        raise ValueError("SERVER_NUMBER is not set")

    return server_number


def exception_in_chain(e: BaseException, c) -> bool:
    if isinstance(e, c):
        return True

    if e.__context__ is not None:
        s = exception_in_chain(e.__context__, c)
        if s:
            return True

    if e.__cause__ is not None:
        s = exception_in_chain(e.__cause__, c)
        if s:
            return True

    return False


def dict_differences(old: dict[Any, Any], new: dict[Any, Any]) -> dict[Any, Any]:
    """Compare old/new and return a dict of differences by key"""
    diff = {}
    for k, v in old.items():
        if isinstance(old[k], dict):
            sub_diff = dict_differences(old[k], new[k])
            if sub_diff:
                diff[k] = sub_diff
        else:
            if old[k] != new[k]:
                diff[k] = new[k]

    return diff


def is_invalid_name_whitespace(name: str) -> bool:
    return name.endswith(" ")


def is_invalid_name_pineapple(name: str) -> bool:
    return len(name) == 20 and name.endswith("?")


def default_player_info_dict(player) -> GetDetailedPlayer:
    return {
        "name": player,
        "steam_id_64": "",
        "profile": None,
        "is_vip": False,
        "unit_id": None,
        "unit_name": None,
        "loadout": None,
        "team": None,
        "role": None,
        "kills": 0,
        "deaths": 0,
        "combat": 0,
        "offense": 0,
        "defense": 0,
        "support": 0,
        "level": 0,
    }


def parse_raw_player_info(raw: str, player) -> GetDetailedPlayer:
    """Parse the result of the playerinfo command from the game server"""

    """
        Name: T17 Scott
        steamID64: 01234567890123456
        Team: Allies            # "None" when not in team
        Role: Officer
        Unit: 0 - Able          # Absent when not in unit
        Loadout: NCO            # Absent when not in team
        Kills: 0 - Deaths: 0
        Score: C 50, O 0, D 40, S 10
        Level: 34

    """

    data = default_player_info_dict(player)
    raw_data = {}

    for line in raw.split("\n"):
        if not line:
            continue
        if ": " not in line:
            logger.warning("Invalid info line: %s", line)
            continue

        key, val = line.split(": ", 1)
        raw_data[key.lower()] = val

    logger.debug(raw_data)
    # Remap keys and parse values
    data[STEAMID] = raw_data.get("steamid64")  # type: ignore
    data["team"] = raw_data.get("team", "None")
    if raw_data["role"].lower() == "armycommander":
        data["unit_id"], data["unit_name"] = (-1, "Commmand")
    else:
        data["unit_id"], data["unit_name"] = (
            raw_data.get("unit").split(" - ")  # type: ignore
            if raw_data.get("unit")
            else ("None", None)
        )
    data["kills"], data["deaths"] = (  # type: ignore
        raw_data.get("kills").split(" - Deaths: ")  # type: ignore
        if raw_data.get("kills")
        else ("0", "0")
    )
    for k in ["role", "loadout", "level"]:
        data[k] = raw_data.get(k)

    scores = dict(
        [
            score.split(" ", 1)
            for score in raw_data.get("score", "C 0, O 0, D 0, S 0").split(", ")
        ]
    )
    map_score = {"C": "combat", "O": "offense", "D": "defense", "S": "support"}
    for key, val in map_score.items():
        data[map_score[key]] = scores.get(key, "0")

    # Typecast values
    # cast strings to lower
    for key in ["team", "unit_name", "role", "loadout"]:
        data[key] = data[key].lower() if data.get(key) else None

    # cast string numbers to ints
    for key in [
        "kills",
        "deaths",
        "level",
        "combat",
        "offense",
        "defense",
        "support",
        "unit_id",
    ]:
        try:
            data[key] = int(data[key])
        except (ValueError, TypeError):
            data[key] = 0

    return data


# https://docs.python.org/3.12/library/itertools.html#itertools.batched
def batched(iterable: Iterable[Any], n: int):
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


class SafeStringFormat(dict):
    def __missing__(self, key):
        called_from = inspect.stack()[1]
        logger.error(
            "SafeStringFormat key='%s' not found, called from %s, line number: %s, context=%s",
            key,
            called_from.filename,
            called_from.lineno,
            called_from.code_context,
        )
        return f"{{{key}}}"

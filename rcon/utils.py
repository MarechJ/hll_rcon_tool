import inspect
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from itertools import islice
from typing import Any, Generic, Iterable, TypeVar

import orjson
import redis
import redis.exceptions

from rcon.cache_utils import get_redis_pool
from rcon.types import GetDetailedPlayer, MapInfo

logger = logging.getLogger("rcon")

PLAYER_ID = "player_id"
NAME = "name"
ROLE = "role"


class DefaultStringFormat(dict):
    """Base class for str.format usage to not crash with invalid keys"""

    def __missing__(self, key):
        logger.error("Invalid key=%s used in string format")
        return key


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


T = TypeVar("T")

# Represents a redis stream ID, these are by default
# the unix timestamp of when the element was added
# with a 0 indexed sequence number when there are
# multiple entries at the same timestamp
# ex: "1526919030474-0"
StreamID = str | None

REDIS_STREAM_OUT_OF_ORDER = (
    "The ID specified in XADD is equal or smaller than the target stream top item"
)
REDIS_STREAM_INVALID_ID = "Invalid stream ID specified as stream command argument"


class StreamOlderElement(Exception):
    """Raised when trying to add an element older than the newest element"""


class StreamInvalidID(Exception):
    """Raised when a stream does not contain the requested element"""


class StreamNoElements(Exception):
    """Raised when a stream query returns no elements"""


class Stream(Generic[T]):
    def __init__(
        self, key, serializer=orjson.dumps, deserializer=orjson.loads, maxlen=10_000
    ) -> None:
        self.red = redis.StrictRedis(connection_pool=get_redis_pool())
        self.key = key
        self.serializer = serializer
        self.deserializer = deserializer
        self.maxlen = maxlen

    def _to_compatible_object(self, obj: dict[Any, Any]) -> T:
        return {self.serializer(k): self.serializer(v) for k, v in obj.items()}

    def _from_compatible_object(self, raw_obj: dict[bytes, bytes]):
        return {self.deserializer(k): self.deserializer(v) for k, v in raw_obj.items()}

    def __len__(self) -> int:
        return self.red.xlen(self.key)  # type: ignore

    def __getitem__(self, key: StreamID) -> tuple[StreamID, T]:
        id_: bytes
        obj: dict[bytes, bytes]
        try:
            id_, obj = next(self.range(min_id=key, max_id=key))
            return (id_.decode(), self._to_compatible_object(obj))
        except IndexError:
            raise KeyError(key)

    def add(
        self,
        obj: dict[Any, Any],
        custom_id: str | None = None,
        approximate_size=True,
        make_non_existent_stream=True,
        min_id_to_retain: StreamID | None = None,
        limit: int | None = None,
    ) -> StreamID:
        """Serialize and add the given object returning its redis stream ID"""
        custom_id = custom_id or "*"

        # Redis can only store key/value pairs that are
        # bytes | memoryview | str | int | float
        # so we serialize keys and values when adding
        # and deserialize when returning
        compatible_dict = self._to_compatible_object(obj)

        try:
            added_id: StreamID = self.red.xadd(
                name=self.key,
                fields=compatible_dict,
                id=custom_id,
                maxlen=self.maxlen,
                approximate=approximate_size,
                nomkstream=not make_non_existent_stream,
                minid=min_id_to_retain,
                limit=limit,
            )
            return added_id.decode()
        except redis.exceptions.ResponseError as e:
            if e.args[0] == REDIS_STREAM_OUT_OF_ORDER:
                raise StreamOlderElement
            else:
                raise

    def delete(self, *ids) -> int:
        """Delete ids from the stream returning the number deleted"""
        return self.red.xdel(self.key, *ids)

    def read(
        self,
        last_id: str | None = None,
        count: int | None = None,
        block_ms: int | None = None,
    ):
        if last_id is None:
            last_id = "$"

        try:
            response = self.red.xread(
                streams={self.key: last_id}, count=count, block=block_ms
            )
        except redis.exceptions.ResponseError:
            raise StreamInvalidID(REDIS_STREAM_INVALID_ID)

        body: dict[bytes, bytes]
        if response:
            body = response[0][1]
            id_: bytes
            return [
                (id_.decode(), self._from_compatible_object(obj)) for id_, obj in body
            ]
        else:
            raise StreamNoElements

    def range(
        self, min_id="-", max_id="+", count: int | None = None, exclusive_start=False
    ):
        if exclusive_start:
            min_id = "(" + min_id

        response: Iterable[tuple[bytes, dict[bytes, bytes]]] = self.red.xrange(
            self.key, min=min_id, max=max_id, count=count
        )
        id_: bytes
        body: dict[bytes, bytes]
        if response:
            for id_, body in response:
                yield id_.decode(), self._from_compatible_object(body)

    def rev_range(
        self, max_id="+", min_id="-", count: int | None = None, exclusive_start=False
    ):
        if exclusive_start:
            max_id = "(" + max_id

        response: Iterable[tuple[bytes, dict[bytes, bytes]]] = self.red.xrevrange(
            self.key, max=max_id, min=min_id, count=count
        )

        id_: bytes
        body: dict[bytes, bytes]
        if response:
            for id_, body in response:
                yield id_.decode(), self._from_compatible_object(body)

    def info(self, full: bool = False):
        response = self.red.xinfo_stream(self.key, full=full)
        return response

    def head(self) -> tuple[StreamID, T] | None:
        try:
            id_, obj = list(self.range(count=1))[0]
            return id_, obj
        except IndexError:
            return None

    def tail(self) -> tuple[StreamID, T] | None:
        try:
            id_, obj = list(self.rev_range(count=1))[0]
            return id_, obj
        except IndexError:
            return None


class FixedLenList(Generic[T]):
    def __init__(
        self, key, max_len=100, serializer=orjson.dumps, deserializer=orjson.loads
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

    def __getitem__(self, index: slice | int) -> T:
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

        # For the multi server stuff (server discovery, forwarding, etc.)
        # they must share the same redis database for this, db 0 is unused by default
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

    def get_all_keys(self) -> dict[str, str]:
        return {
            k.decode(): self.red.get(k.decode()).decode()
            for k in self.red.keys(f"{self.key_prefix}*")
        }


def get_server_number() -> str:
    """Get the CRCON server number"""
    server_number = os.getenv("SERVER_NUMBER")
    # TODO: enforce that this is an int
    if not server_number:
        # Shouldn't get here because SERVER_NUMBER is a mandatory ENV Var
        raise ValueError("SERVER_NUMBER is not set")

    return server_number


# Add a quick shorthand for the SERVER NUMBER but don't fail in the maintenance container
if os.getenv("SERVER_NUMBER"):
    SERVER_NUMBER = int(get_server_number())


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


def default_player_info_dict(player) -> GetDetailedPlayer:
    return {
        "name": player,
        "player_id": "",
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
    data[PLAYER_ID] = raw_data.get("steamid64")  # type: ignore
    data["team"] = raw_data.get("team", "None")
    if raw_data["role"].lower() == "armycommander":
        data["unit_id"], data["unit_name"] = (-1, "Command")
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


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MissingType(metaclass=SingletonMeta):
    def __bool__(self):
        return False

    def __iter__(self):
        return
        yield

    def __repr__(self):
        return "MISSING"


MISSING = MissingType()


def server_numbers_to_mask(*server_numbers):
    result = 0
    for number in server_numbers:
        if number <= 0 or number > 32:
            raise ValueError("Server number must be between 1 and 32")
        # Shift the positive bit to create a mask and then merge that mask with the result
        # eg. [1, 2, 4] -> 0001, 0010, 1000 -> 1011
        result |= 1 << (number - 1)
    return result


def mask_to_server_numbers(mask: int) -> set[int]:
    server_numbers = set()
    # bin() returns '0b...', so we slice of the first two characters and then iterate over the remaining
    # characters from back to front.
    # eg. bin(7) -> '0b1011' -> [1, 1, 0, 1] -> [1, 2, 4]
    for i, c in enumerate(bin(mask)[:1:-1], 1):
        if c == "1":
            server_numbers.add(i)
    return server_numbers


def humanize_timedelta(td: timedelta | datetime | None) -> str:
    """Converts a timedelta to a human-readable string.

    Example:
    timedelta(-60*60*24*2.5) => "2 days ago"
    timedelta(60*60 - 5) => "in an hour"
    None => "forever"
    """
    if td is None:
        return "forever"

    if isinstance(td, datetime):
        td = td - datetime.now(tz=timezone.utc)

    seconds = int(td.total_seconds())
    if seconds < 0:
        fmt = "{} ago"
        seconds = abs(seconds)
    else:
        fmt = "in {}"

    minutes = seconds / 60
    if int(minutes) <= 1:
        return fmt.format("a minute")
    elif minutes < 59:
        return fmt.format(f"{int(minutes)} minutes")

    hours = minutes / 60
    if int(hours) <= 1:
        return fmt.format(f"an hour")
    elif hours < 23.5:
        return fmt.format(f"{int(hours)} hours")

    days = hours / 24
    if int(days) <= 1:
        return fmt.format(f"a day")
    elif days < 6.9:
        return fmt.format(f"{int(days)} days")

    weeks = days / 7
    if int(weeks) <= 1:
        return fmt.format(f"a week")
    elif days < 29.9:
        return fmt.format(f"{int(weeks)} weeks")

    months = days / 30
    if int(months) <= 1:
        return fmt.format(f"a month")
    elif months < 11.95:
        return fmt.format(f"{int(months)} months")

    years = days / 365
    if int(years) <= 1:
        return fmt.format(f"a year")
    return fmt.format("{} years")


def strtobool(val) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    if val is None:
        return False

    if isinstance(val, bool) or val == MISSING:
        return val

    # sourced from https://stackoverflow.com/a/18472142 with modification
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def get_server_number_mask():
    """Calculate server masks for Blacklist/VIP lists"""
    server_number = SERVER_NUMBER
    return 1 << (server_number - 1)

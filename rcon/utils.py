import json
import logging
import os
import secrets
from datetime import datetime
from typing import Generic, TypeVar
from urllib.parse import urlparse

import redis

from rcon.cache_utils import get_redis_pool
from rcon.typedefs import MapInfo

logger = logging.getLogger("rcon")

ALL_MAPS = (
    "carentan_offensive_ger",
    "carentan_offensive_us",
    "carentan_warfare",
    "driel_offensive_ger",
    "driel_offensive_us",
    "driel_warfare",
    "elalamein_offensive_CW",
    "elalamein_offensive_ger",
    "elalamein_warfare",
    "foy_offensive_ger",
    "foy_offensive_us",
    "foy_warfare_night",
    "foy_warfare",
    "hill400_offensive_ger",
    "hill400_offensive_US",
    "hill400_warfare",
    "hurtgenforest_offensive_ger",
    "hurtgenforest_offensive_US",
    "hurtgenforest_warfare_V2_night",
    "hurtgenforest_warfare_V2",
    "kharkov_offensive_ger",
    "kharkov_offensive_rus",
    "kharkov_warfare",
    "kursk_offensive_ger",
    "kursk_offensive_rus",
    "kursk_warfare_night",
    "kursk_warfare",
    "omahabeach_offensive_ger",
    "omahabeach_offensive_us",
    "omahabeach_warfare",
    "purpleheartlane_offensive_ger",
    "purpleheartlane_offensive_us",
    "purpleheartlane_warfare_night",
    "purpleheartlane_warfare",
    "remagen_offensive_ger",
    "remagen_offensive_us",
    "remagen_warfare_night",
    "remagen_warfare",
    "stalingrad_offensive_ger",
    "stalingrad_offensive_rus",
    "stalingrad_warfare",
    "stmariedumont_off_ger",
    "stmariedumont_off_us",
    "stmariedumont_warfare",
    "stmereeglise_offensive_ger",
    "stmereeglise_offensive_us",
    "stmereeglise_warfare",
    "utahbeach_offensive_ger",
    "utahbeach_offensive_us",
    "utahbeach_warfare",
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


def numbered_maps(maps):
    return {str(idx): map_ for idx, map_ in enumerate(maps)}


def categorize_maps(maps):
    warfare_offsensive = {
        "warfare": [],
        "offensive": [],
    }
    for m in maps:
        if "offensive" in m or m.startswith("stmariedumont_off"):
            warfare_offsensive["offensive"].append(m)
        if "warfare" in m:
            warfare_offsensive["warfare"].append(m)

    return warfare_offsensive


def map_name(map_):
    name, *rest = map_.split("_")
    # if "night" in map_:
    #    return f"{name}_night"
    return name


def get_map_side(map_):
    try:
        parts = map_.split("_")
        return parts[2].lower() if parts[2] in ["us", "ger", "rus"] else None
    except IndexError:
        return None


LOG_MAP_NAMES_TO_MAP = {
    "CARENTAN OFFENSIVE": "carentan_offensive_ger",
    "CARENTAN WARFARE": "carentan_warfare",
    "FOY OFFENSIVE": "foy_offensive_ger",
    "FOY WARFARE": "foy_warfare",
    "HILL 400 OFFENSIVE": "hill400_offensive_ger",
    "HILL 400 WARFARE": "hill400_warfare",
    "HÜRTGEN FOREST OFFENSIVE": "hurtgenforest_offensive_ger",
    "HÜRTGEN FOREST WARFARE": "hurtgenforest_warfare_V2",
    "KURSK OFFENSIVE": "kursk_offensive_ger",
    "KURSK WARFARE": "kursk_warfare",
    "Kharkov OFFENSIVE": "kharkov_offensive_rus",
    "Kharkov WARFARE": "kharkov_warfare",
    "PURPLE HEART LANE OFFENSIVE": "purpleheartlane_offensive_ger",
    "PURPLE HEART LANE WARFARE": "purpleheartlane_warfare",
    "REMAGEN OFFENSIVE": "remagen_offensive_ger",
    "REMAGEN WARFARE": "remagen_warfare",
    "SAINTE-MÈRE-ÉGLISE OFFENSIVE": "stmereeglise_offensive_ger",
    "SAINTE-MÈRE-ÉGLISE WARFARE": "stmereeglise_warfare",
    "ST MARIE DU MONT OFFENSIVE": "stmariedumont_off_ger",
    "ST MARIE DU MONT WARFARE": "stmariedumont_warfare",
    "STALINGRAD OFFENSIVE": "stalingrad_offensive_ger",
    "STALINGRAD WARFARE": "stalingrad_warfare",
    "UTAH BEACH OFFENSIVE": "utahbeach_offensive_ger",
    "UTAH BEACH WARFARE": "utahbeach_warfare",
    "OMAHA BEACH WARFARE": "omahabeach_warfare",
    "OMAHA BEACH OFFENSIVE": "omahabeach_offensive_ger",
    "DRIEL WARFARE": "driel_warfare",
    "DRIEL OFFENSIVE": "driel_offensive_ger",
    "EL ALAMEIN WARFARE": "elalamein_warfare",
    "EL ALAMEIN OFFENSIVE": "elalamein_offensive_ger",
}

LONG_HUMAN_MAP_NAMES = {
    "carentan_offensive_ger": "Carentan Offensive (GER)",
    "carentan_offensive_us": "Carentan Offensive (US)",
    "carentan_warfare": "Carentan",
    "driel_offensive_ger": "Driel Offensive (GER)",
    "driel_offensive_us": "Driel Offensive (UK)",
    "driel_warfare": "Driel",
    "elalamein_offensive_CW": "El Alamein Offensive (UK)",
    "elalamein_offensive_ger": "El Alamein Offensive (GER)",
    "elalamein_warfare": "El Alamein",
    "foy_offensive_ger": "Foy Offensive (GER)",
    "foy_offensive_us": "Foy Offensive (US)",
    "foy_warfare_night": "Foy (Night)",
    "foy_warfare": "Foy",
    "hill400_offensive_ger": "Hill 400 Offensive (GER)",
    "hill400_offensive_US": "Hill 400 Offensive (US)",
    "hill400_warfare": "Hill 400",
    "hurtgenforest_offensive_ger": "Hürtgen Forest Offensive (GER)",
    "hurtgenforest_offensive_US": "Hürtgen Forest Offensive (US)",
    "hurtgenforest_warfare_V2_night": "Hürtgen Forest (Night)",
    "hurtgenforest_warfare_V2": "Hürtgen Forest",
    "kharkov_offensive_ger": "Kharkov Offensive (GER)",
    "kharkov_offensive_rus": "Kharkov Offensive (RUS)",
    "kharkov_warfare": "Kharkov",
    "kursk_offensive_ger": "Kursk Offensive (GER)",
    "kursk_offensive_rus": "Kursk Offensive (RUS)",
    "kursk_warfare_night": "Kursk (Night)",
    "kursk_warfare": "Kursk",
    "omahabeach_offensive_ger": "Omaha Beach Offensive (GER)",
    "omahabeach_offensive_us": "Omaha Beach Offensive (US)",
    "omahabeach_warfare": "Omaha Beach",
    "purpleheartlane_offensive_ger": "Purple Heart Lane Offensive (GER)",
    "purpleheartlane_offensive_us": "Purple Heart Lane Offensive (US)",
    "purpleheartlane_warfare_night": "Purple Heart Lane (Night)",
    "purpleheartlane_warfare": "Purple Heart Lane",
    "remagen_offensive_ger": "Remagen Offensive (GER)",
    "remagen_offensive_us": "Remagen Offensive (US)",
    "remagen_warfare_night": "Remagen (Night)",
    "remagen_warfare": "Remagen",
    "stalingrad_offensive_ger": "Stalingrad Offensive (GER)",
    "stalingrad_offensive_rus": "Stalingrad Offensive (RUS)",
    "stalingrad_warfare": "Stalingrad",
    "stmariedumont_off_ger": "Ste Marie du Mont Offensive (GER)",
    "stmariedumont_off_us": "Ste Marie du Mont Offensive (US)",
    "stmariedumont_warfare": "Ste Marie du Mont",
    "stmereeglise_offensive_ger": "Ste Mère Église Offensive (GER)",
    "stmereeglise_offensive_us": "Ste Mère Église Offensive (US)",
    "stmereeglise_warfare": "Ste Mère Église",
    "utahbeach_offensive_ger": "Utah Beach Offensive (GER)",
    "utahbeach_offensive_us": "Utah Beach Offensive (US)",
    "utahbeach_warfare": "Utah Beach",
}

SHORT_HUMAN_MAP_NAMES = {
    "carentan_offensive_ger": "Carentan Off. (GER)",
    "carentan_offensive_us": "Carentan Off. (US)",
    "carentan_warfare": "Carentan",
    "driel_offensive_ger": "Driel Off. (GER)",
    "driel_offensive_us": "Driel Off. (UK)",
    "driel_warfare": "Driel",
    "elalamein_offensive_CW": "El Alamein Off. (UK)",
    "elalamein_offensive_ger": "El Alamein Off. (GER)",
    "elalamein_warfare": "El Alamein",
    "foy_offensive_ger": "Foy Off. (GER)",
    "foy_offensive_us": "Foy Off. (US)",
    "foy_warfare_night": "Foy (Night)",
    "foy_warfare": "Foy",
    "hill400_offensive_ger": "Hill400 Off. (GER)",
    "hill400_offensive_US": "Hill400 Off. (US)",
    "hill400_warfare": "Hill400",
    "hurtgenforest_offensive_ger": "Hürtgen Off. (GER)",
    "hurtgenforest_offensive_US": "Hürtgen Off. (US)",
    "hurtgenforest_warfare_V2_night": "Hürtgen (Night)",
    "hurtgenforest_warfare_V2": "Hürtgen",
    "kharkov_offensive_ger": "Kharkov Off. (GER)",
    "kharkov_offensive_rus": "Kharkov Off. (RUS)",
    "kharkov_warfare": "Kharkov",
    "kursk_offensive_ger": "Kursk Off. (GER)",
    "kursk_offensive_rus": "Kursk Off. (RUS)",
    "kursk_warfare_night": "Kursk (Night)",
    "kursk_warfare": "Kursk",
    "omahabeach_offensive_ger": "Omaha Off. (GER)",
    "omahabeach_offensive_us": "Omaha Off. (US)",
    "omahabeach_warfare": "Omaha",
    "purpleheartlane_offensive_ger": "PHL Off. (GER)",
    "purpleheartlane_offensive_us": "PHL Off. (US)",
    "purpleheartlane_warfare_night": "PHL (Night)",
    "purpleheartlane_warfare": "PHL",
    "remagen_offensive_ger": "Remagen Off. (GER)",
    "remagen_offensive_us": "Remagen Off. (US)",
    "remagen_warfare_night": "Remagen (Night)",
    "remagen_warfare": "Remagen",
    "stalingrad_offensive_ger": "Stalingrad Off. (GER)",
    "stalingrad_offensive_rus": "Stalingrad Off. (RUS)",
    "stalingrad_warfare": "Stalingrad",
    "stmariedumont_off_ger": "SMDM Off. (GER)",
    "stmariedumont_off_us": "SMDM Off. (US)",
    "stmariedumont_warfare": "SMDM",
    "stmereeglise_offensive_ger": "SME Off. (GER)",
    "stmereeglise_offensive_us": "SME Off. (US)",
    "stmereeglise_warfare": "SME",
    "utahbeach_offensive_ger": "Utah Off. (GER)",
    "utahbeach_offensive_us": "Utah Off. (US)",
    "utahbeach_warfare": "Utah",
}

NO_MOD_LONG_HUMAN_MAP_NAMES = {
    "carentan_offensive_ger": "Carentan (GER)",
    "carentan_offensive_us": "Carentan (US)",
    "carentan_warfare": "Carentan",
    "driel_offensive_ger": "Driel (GER)",
    "driel_offensive_us": "Driel (UK)",
    "driel_warfare": "Driel",
    "elalamein_offensive_CW": "El Alamein (UK)",
    "elalamein_offensive_ger": "El Alamein (GER)",
    "elalamein_warfare": "El Alamein",
    "foy_offensive_ger": "Foy (GER)",
    "foy_offensive_us": "Foy (US)",
    "foy_warfare_night": "Foy (Night)",
    "foy_warfare": "Foy",
    "hill400_offensive_ger": "Hill 400 (GER)",
    "hill400_offensive_US": "Hill 400 (US)",
    "hill400_warfare": "Hill 400",
    "hurtgenforest_offensive_ger": "Hürtgen Forest (GER)",
    "hurtgenforest_offensive_US": "Hürtgen Forest (US)",
    "hurtgenforest_warfare_V2_night": "Hürtgen Forest (Night)",
    "hurtgenforest_warfare_V2": "Hürtgen Forest",
    "kharkov_offensive_ger": "Kharkov (GER)",
    "kharkov_offensive_rus": "Kharkov (RUS)",
    "kharkov_warfare": "Kharkov",
    "kursk_offensive_ger": "Kursk (GER)",
    "kursk_offensive_rus": "Kursk (RUS)",
    "kursk_warfare_night": "Kursk (Night)",
    "kursk_warfare": "Kursk",
    "omahabeach_offensive_ger": "Omaha (GER)",
    "omahabeach_offensive_us": "Omaha Beach (US)",
    "omahabeach_warfare": "Omaha Beach",
    "purpleheartlane_offensive_ger": "Purple Heart Lane (GER)",
    "purpleheartlane_offensive_us": "Purple Heart Lane (US)",
    "purpleheartlane_warfare_night": "Purple Heart Lane (Night)",
    "purpleheartlane_warfare": "Purple Heart Lane",
    "remagen_offensive_ger": "Remagen (GER)",
    "remagen_offensive_us": "Remagen (US)",
    "remagen_warfare_night": "Remagen (Night)",
    "remagen_warfare": "Remagen",
    "stalingrad_offensive_ger": "Stalingrad (GER)",
    "stalingrad_offensive_rus": "Stalingrad (RUS)",
    "stalingrad_warfare": "Stalingrad",
    "stmariedumont_off_ger": "Ste Marie du Mont (GER)",
    "stmariedumont_off_us": "Ste Marie du Mont (US)",
    "stmariedumont_warfare": "Ste Marie du Mont",
    "stmereeglise_offensive_ger": "Ste Mère Église (GER)",
    "stmereeglise_offensive_us": "Ste Mère Église (US)",
    "stmereeglise_warfare": "Ste Mère Église",
    "utahbeach_offensive_ger": "Utah Beach (GER)",
    "utahbeach_offensive_us": "Utah Beach (US)",
    "utahbeach_warfare": "Utah Beach",
}

NO_MOD_SHORT_HUMAN_MAP_NAMES = {
    "carentan_offensive_ger": "Carentan (GER)",
    "carentan_offensive_us": "Carentan (US)",
    "carentan_warfare": "Carentan",
    "driel_offensive_ger": "Driel (GER)",
    "driel_offensive_us": "Driel (UK)",
    "driel_warfare": "Driel",
    "elalamein_offensive_CW": "El Alamein (UK)",
    "elalamein_offensive_ger": "El Alamein (GER)",
    "elalamein_warfare": "El Alamein",
    "foy_offensive_ger": "Foy (GER)",
    "foy_offensive_us": "Foy (US)",
    "foy_warfare_night": "Foy (Night)",
    "foy_warfare": "Foy",
    "hill400_offensive_ger": "Hill400 (GER)",
    "hill400_offensive_US": "Hill400 (US)",
    "hill400_warfare": "Hill400",
    "hurtgenforest_offensive_ger": "Hürtgen (GER)",
    "hurtgenforest_offensive_US": "Hürtgen (US)",
    "hurtgenforest_warfare_V2_night": "Hürtgen (Night)",
    "hurtgenforest_warfare_V2": "Hürtgen",
    "kharkov_offensive_ger": "Kharkov (GER)",
    "kharkov_offensive_rus": "Kharkov (RUS)",
    "kharkov_warfare": "Kharkov",
    "kursk_offensive_ger": "Kursk (GER)",
    "kursk_offensive_rus": "Kursk (RUS)",
    "kursk_warfare_night": "Kursk (Night)",
    "kursk_warfare": "Kursk",
    "omahabeach_offensive_ger": "Omaha (GER)",
    "omahabeach_offensive_us": "Omaha (US)",
    "omahabeach_warfare": "Omaha",
    "purpleheartlane_offensive_ger": "PHL (GER)",
    "purpleheartlane_offensive_us": "PHL (US)",
    "purpleheartlane_warfare_night": "PHL (Night)",
    "purpleheartlane_warfare": "PHL",
    "remagen_offensive_ger": "Remagen (GER)",
    "remagen_offensive_us": "Remagen (US)",
    "remagen_warfare_night": "Remagen (Night)",
    "remagen_warfare": "Remagen",
    "stalingrad_offensive_ger": "Stalingrad (GER)",
    "stalingrad_offensive_rus": "Stalingrad (RUS)",
    "stalingrad_warfare": "Stalingrad",
    "stmariedumont_off_ger": "SMDM (GER)",
    "stmariedumont_off_us": "SMDM (US)",
    "stmariedumont_warfare": "SMDM",
    "stmereeglise_offensive_ger": "SME (GER)",
    "stmereeglise_offensive_us": "SME (US)",
    "stmereeglise_warfare": "SME",
    "utahbeach_offensive_ger": "Utah (GER)",
    "utahbeach_offensive_us": "Utah (US)",
    "utahbeach_warfare": "Utah",
}

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

        parts = urlparse(os.getenv("REDIS_URL"))
        self.red = redis.StrictRedis(host=parts.hostname, port=parts.port, db=0)
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


def get_server_number() -> int:
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

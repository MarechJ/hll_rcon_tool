import json
import logging
import os
import secrets
from datetime import datetime
from urllib.parse import urlparse

import redis

from rcon.cache_utils import get_redis_client, get_redis_pool

logger = logging.getLogger("rcon")

ALL_MAPS = (
    "foy_warfare",
    "foy_offensive_ger",
    "foy_offensive_us",
    "stmariedumont_warfare",
    "utahbeach_warfare",
    "utahbeach_offensive_ger",
    "utahbeach_offensive_us",
    "omahabeach_offensive_us",
    "stmereeglise_warfare",
    "stmereeglise_offensive_us",
    "stmereeglise_offensive_ger",
    "purpleheartlane_warfare",
    "purpleheartlane_offensive_us",
    "purpleheartlane_offensive_ger",
    "hill400_warfare",
    "hill400_offensive_US",
    "hill400_offensive_ger",
    "carentan_warfare",
    "carentan_offensive_us",
    "carentan_offensive_ger",
    "hurtgenforest_warfare_V2",
    "hurtgenforest_offensive_US",
    "hurtgenforest_offensive_ger",
    'kursk_warfare',
    'kursk_offensive_rus',
    'kursk_offensive_ger',
    'stalingrad_warfare',
    'stalingrad_offensive_rus',
    'stalingrad_offensive_ger',
    'stmariedumont_off_us',
    'stmariedumont_off_ger',
    "remagen_warfare",
    "remagen_offensive_ger",
    "remagen_offensive_us",
    "foy_warfare_night",
    "hurtgenforest_warfare_V2_night",
    "kursk_warfare_night",
    "purpleheartlane_warfare_night",
    "remagen_warfare_night",
    "omahabeach_warfare",
    "omahabeach_offensive_ger",
)


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
        if "offensive" in m:
            warfare_offsensive["offensive"].append(m)
        if "warfare" in m:
            warfare_offsensive["warfare"].append(m)

    return warfare_offsensive


def map_name(map_):
    name, *rest = map_.split("_")
    return name


def get_map_side(map_):
    try:
        parts = map_.split("_")
        return parts[2].lower() if parts[2] in ["us", "ger", "rus"] else None
    except IndexError:
        return None


LONG_HUMAN_MAP_NAMES = {
    "foy_warfare": "Foy",
    "foy_offensive_ger": "Foy Offensive (GER)",
    "foy_offensive_us": "Foy Offensive (US)",
    "stmariedumont_warfare": "St Marie du Mont",
    'stmariedumont_off_us': "St Marie Du Mont Offensive (US)",
    'stmariedumont_off_ger': "St Marie Du Mont Offensive (GER)",
    "hurtgenforest_warfare_V2": "Hurtgen Forest",
    "hurtgenforest_offensive_ger": "Hurtgen Forest Offensive (GER)",
    "hurtgenforest_offensive_US": "Hurtgen Forest Offensive (US)",
    "utahbeach_warfare": "Utah beach",
    "utahbeach_offensive_us": "Utah Beach Offensive (US)",
    "utahbeach_offensive_ger": "Utah Beach Offensive (GER)",
    "omahabeach_offensive_us": "Omaha Beach Offensive (US)",
    "stmereeglise_warfare": "St Mere Eglise",
    "stmereeglise_offensive_ger": "St Mere Eglise Offensive (GER)",
    "stmereeglise_offensive_us": "St Mere Eglise Offensive (US)",
    "purpleheartlane_warfare": "Purple Heart Lane",
    "purpleheartlane_offensive_us": "Purple Heart Lane Offensive (US)",
    "purpleheartlane_offensive_ger": "Purple Heart Lane Offensive (GER)",
    "hill400_warfare": "Hill 400",
    "hill400_offensive_US": "Hill 400 Offensive (US)",
    "hill400_offensive_ger": "Hill 400 Offensive (GER)",
    "carentan_warfare": "Carentan",
    "carentan_offensive_us": "Carentan Offensive (US)",
    "carentan_offensive_ger": "Carentan Offensive (GER)",
    'kursk_warfare': "Kursk",
    'kursk_offensive_rus': "Kursk Offensive (RUS)",
    'kursk_offensive_ger': "Kursk Offensive (GER)",
    'stalingrad_warfare': "Stalingrad",
    'stalingrad_offensive_rus': "Stalingrad Offensive (RUS)",
    'stalingrad_offensive_ger': "Stalingrad Offensive (GER)",
    "remagen_warfare": "Remagen",
    "remagen_offensive_ger": "Remagen Offensive (GER)",
    "remagen_offensive_us": "Remagen Offensive (US)",
    "foy_warfare_night": "Foy (Night)",
    "hurtgenforest_warfare_V2_night": "Hurtgen Forest (Night)",
    "kursk_warfare_night": "Kursk (Night)",
    "purpleheartlane_warfare_night": "Purpleheartlane (Night)",
    "remagen_warfare_night": "Remagen (Night)",
    "omahabeach_warfare": "Omaha Beach",
    "omahabeach_offensive_ger": " Omaha Beach Offensive (GER)",
}

SHORT_HUMAN_MAP_NAMES = {
    "foy_warfare": "Foy",
    "foy_offensive_ger": "Foy Off. (GER)",
    "foy_offensive_us": "Foy Off. (US)",
    "stmariedumont_warfare": "SMDM",
    'stmariedumont_off_us': "SMDM Off. (US)",
    'stmariedumont_off_ger': "SMDM Off. (GER)",
    "hurtgenforest_warfare_V2": "Hurtgen",
    "hurtgenforest_offensive_ger": "Hurtgen Off. (GER)",
    "hurtgenforest_offensive_US": "Hurtgen Off. (US)",
    "utahbeach_warfare": "Utah",
    "utahbeach_offensive_us": "Utah Off. (US)",
    "utahbeach_offensive_ger": "Utah Off. (GER)",
    "omahabeach_offensive_us": "Omaha Off. (US)",
    "stmereeglise_warfare": "SME",
    "stmereeglise_offensive_ger": "SME Off. (GER)",
    "stmereeglise_offensive_us": "SME Off. (US)",
    "purpleheartlane_warfare": "PHL",
    "purpleheartlane_offensive_us": "PHL Off. (US)",
    "purpleheartlane_offensive_ger": "PHL Off. (GER)",
    "hill400_warfare": "Hill400",
    "hill400_offensive_US": "Hill400 Off. (US)",
    "hill400_offensive_ger": "Hill400 Off. (GER)",
    "carentan_warfare": "Carentan",
    "carentan_offensive_us": "Carentan Off. (US)",
    "carentan_offensive_ger": "Carentan Off. (GER)",
    'kursk_warfare': "Kursk",
    'kursk_offensive_rus': "Kursk Off. (RUS)",
    'kursk_offensive_ger': "Kursk Off. (GER)",
    'stalingrad_warfare': "Stalingrad",
    'stalingrad_offensive_rus': "Stalingrad Off. (RUS)",
    'stalingrad_offensive_ger': "Stalingrad Off. (GER)",
    "remagen_warfare": "Remagen",
    "remagen_offensive_ger": "Remagen Off. (GER)",
    "remagen_offensive_us": "Remagen Off. (US)",
    "foy_warfare_night": "Foy (Night)",
    "hurtgenforest_warfare_V2_night": "Hurtgen (Night)",
    "kursk_warfare_night": "Kursk (Night)",
    "purpleheartlane_warfare_night": "PHL (Night)",
    "remagen_warfare_night": "Remagen (Night)",
    "omahabeach_warfare": "Omaha",
    "omahabeach_offensive_ger": " Omaha Off. (GER)",
}


NO_MOD_LONG_HUMAN_MAP_NAMES = {
    "foy_warfare": "Foy",
    "foy_offensive_us": "Foy (US)",
    "foy_offensive_ger": "Foy (GER)",
    "stmariedumont_warfare": "St Marie Du Mont",
    'stmariedumont_off_us': "St Marie Du Mont (US)",
    'stmariedumont_off_ger': "St Marie Du Mont (GER)",
    "hurtgenforest_warfare_V2": "Hurtgen Forest",
    "hurtgenforest_offensive_ger": "Hurtgen Forest (GER)",
    "hurtgenforest_offensive_US": "Hurtgen Forest (US)",
    "utahbeach_warfare": "Utah Beach",
    "utahbeach_offensive_us": "Utah Beach (US)",
    "utahbeach_offensive_ger": "Utah Beach (GER)",
    "omahabeach_offensive_us": "Omaha Beach (US)",
    "stmereeglise_warfare": "St Mere Eglise",
    "stmereeglise_offensive_ger": "St Mere Eglise (GER)",
    "stmereeglise_offensive_us": "St Mere Eglise (US)",
    "purpleheartlane_warfare": "Purple Heart Lane",
    "purpleheartlane_offensive_us": "Purple Heart Lane (US)",
    "purpleheartlane_offensive_ger": "Purple Heart Lane (GER)",
    "hill400_warfare": "Hill 400",
    "hill400_offensive_US": "Hill 400 (US)",
    "hill400_offensive_ger": "Hill 400 (GER)",
    "carentan_warfare": "Carentan",
    "carentan_offensive_us": "Carentan (US)",
    "carentan_offensive_ger": "Carentan (GER)",
    'kursk_warfare': "Kursk",
    'kursk_offensive_rus': "Kursk (RUS)",
    'kursk_offensive_ger': "Kursk (GER)",
    'stalingrad_warfare': "Stalingrad",
    'stalingrad_offensive_rus': "Stalingrad (RUS)",
    'stalingrad_offensive_ger': "Stalingrad (GER)",
    "remagen_warfare": "Remagen",
    "remagen_offensive_ger": "Remagen (GER)",
    "remagen_offensive_us": "Remagen (US)",
    "foy_warfare_night": "Foy (Night)",
    "hurtgenforest_warfare_V2_night": "Hurtgen forest (Night)",
    "kursk_warfare_night": "Kursk (Night)",
    "purpleheartlane_warfare_night": "Purple Heart Lane  (Night)",
    "remagen_warfare_night": "Remagen (Night)",
    "omahabeach_warfare": "Omaha Beach",
    "omahabeach_offensive_ger": " Omaha (GER)",
}

NO_MOD_SHORT_HUMAN_MAP_NAMES = {
    "foy_warfare": "Foy",
    "foy_offensive_us": "Foy (US)",
    "foy_offensive_ger": "Foy (GER)",
    "stmariedumont_warfare": "SMDM",
    'stmariedumont_off_us': "SMDM (US)",
    'stmariedumont_off_ger': "SMDM (GER)",
    "hurtgenforest_warfare_V2": "Hurtgen",
    "hurtgenforest_offensive_ger": "Hurtgen (GER)",
    "hurtgenforest_offensive_US": "Hurtgen (US)",
    "utahbeach_warfare": "Utah",
    "utahbeach_offensive_us": "Utah (US)",
    "utahbeach_offensive_ger": "Utah (GER)",
    "omahabeach_offensive_us": "Omaha",
    "stmereeglise_warfare": "SME",
    "stmereeglise_offensive_us": "SME (US)",
    "stmereeglise_offensive_ger": "SME (GER)",
    "purpleheartlane_warfare": "PHL",
    "purpleheartlane_offensive_us": "PHL (US)",
    "purpleheartlane_offensive_ger": "PHL (GER)",
    "hill400_warfare": "Hill400",
    "hill400_offensive_US": "Hill400 (US)",
    "hill400_offensive_ger": "Hill400 (GER)",
    "carentan_warfare": "Carentan",
    "carentan_offensive_us": "Carentan (US)",
    "carentan_offensive_ger": "Carentan (GER)",
    'kursk_warfare': "Kursk",
    'kursk_offensive_rus': "Kursk (RUS)",
    'kursk_offensive_ger': "Kursk (GER)",
    'stalingrad_warfare': "Stalingrad",
    'stalingrad_offensive_rus': "Stalingrad (RUS)",
    'stalingrad_offensive_ger': "Stalingrad (GER)",
    "remagen_warfare": "Remagen",
    "remagen_offensive_ger": "Remagen (GER)",
    "remagen_offensive_us": "Remagen (US)",
    "foy_warfare_night": "Foy (Night)",
    "hurtgenforest_warfare_V2_night": "Hurtgen (Night)",
    "kursk_warfare_night": "Kursk (Night)",
    "purpleheartlane_warfare_night": "PHL (Night)",
    "remagen_warfare_night": "Remagen (Night)",
    "omahabeach_warfare": "Omaha",
    "omahabeach_offensive_ger": " Omaha (GER)",
}


class FixedLenList:
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

    def __getitem__(self, index):
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


class MapsHistory(FixedLenList):
    def __init__(self, key="maps_history", max_len=500):
        super().__init__(key, max_len)

    def save_map_end(self, old_map):
        ts = datetime.now().timestamp()
        logger.info("Saving end of map %s at time %s", old_map, ts)
        prev = self.lpop() or dict(name=old_map, start=None, end=None)
        prev["end"] = ts
        self.lpush(prev)
        return prev

    def save_new_map(self, new_map):
        ts = datetime.now().timestamp()
        logger.info("Saving start of new map %s at time %s", new_map, ts)
        new = dict(name=new_map, start=ts, end=None)
        self.add(new)
        return new

class ApiKey:
    def __init__(self):
        num = os.getenv('SERVER_NUMBER')
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

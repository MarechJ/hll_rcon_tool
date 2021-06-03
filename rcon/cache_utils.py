import redis
import simplejson
import pickle
import logging
import os
import functools
from cachetools.func import ttl_cache as cachetools_ttl_cache
from contextlib import contextmanager

logger = logging.getLogger(__name__)

_REDIS_POOL = None


class RedisCached:
    PREFIX = 'cached_'

    def __init__(self, pool, ttl_seconds, function, is_method=False, cache_falsy=True, serializer=simplejson.dumps, deserializer=simplejson.loads):
        self.red = redis.Redis(connection_pool=pool)
        self.function = function
        self.serializer = serializer
        self.deserializer = deserializer
        self.ttl_seconds = ttl_seconds
        self.is_method = is_method
        self.cache_falsy = cache_falsy

    @staticmethod
    def clear_all_caches(pool):
        red = redis.Redis(connection_pool=pool)
        keys = list(red.scan_iter(match=f"{RedisCached.PREFIX}*"))
        logger.warning("Wiping cached values %s", keys)
        if not keys:
            return
        return red.delete(*keys)

    @property
    def key_prefix(self):
        return f'{self.PREFIX}{self.function.__qualname__}'

    def key(self, *args, **kwargs):
        if self.is_method:
            args = args[1:]
        params = self.serializer({'args': args, "kwargs": kwargs})
        if isinstance(params, bytes):
            return self.key_prefix.encode() + b'__' + params
        return f"{self.key_prefix}__{params}"

    @property
    def __name__(self):
        return self.function.__name__


    @property
    def __wrapped__(self):
        return self.function

    def __call__(self, *args, **kwargs):
        val = None
        key = self.key(*args, **kwargs)
        try:
            val = self.red.get(key)
        except redis.exceptions.RedisError:
            logger.exception("Unable to use cache")

        if val is not None:
            #logger.debug("Cache HIT for %s", self.key(*args, **kwargs))
            return self.deserializer(val)

        #logger.debug("Cache MISS for %s", self.key(*args, **kwargs))
        val = self.function(*args, **kwargs)

        if not val and not self.cache_falsy:
            logger.debug("Caching falsy result is disabled for %s", self.__name__)
            return val 

        try:
            self.red.setex(key, self.ttl_seconds, self.serializer(val))
            #logger.debug("Cache SET for %s", self.key(*args, **kwargs))
        except redis.exceptions.RedisError:
            logger.exception("Unable to set cache")

        return val

    def get_cached_value_for(self, *args, **kwargs):
        return self.red.get(self.key(*args, **kwargs))

    def clear_for(self, *args, **kwargs):
        key = self.key(*args, **kwargs)
        if key:
            self.red.delete(key)

    def clear_all(self):
        try:
            keys = list(self.red.scan_iter(match=f"{self.key_prefix}*"))
            if keys:
                self.red.delete(*keys)
        except redis.exceptions.RedisError:
            logger.exception("Unable to clear cache")
        #else:
        #   logger.debug("Cache CLEARED for %s", keys)


def get_redis_pool(decode_responses=True):
    global _REDIS_POOL
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        return None
 
    if _REDIS_POOL is None:
        logger.warning("Redis pool initializing")
        _REDIS_POOL = redis.ConnectionPool.from_url(
            redis_url, max_connections=10, socket_connect_timeout=5,
            socket_timeout=5, decode_responses=decode_responses
        )

    return _REDIS_POOL


def get_redis_client(decode_responses=True):
    pool = get_redis_pool(decode_responses)
    return redis.Redis(connection_pool=pool)


def ttl_cache(ttl, *args, is_method=True, cache_falsy=True, **kwargs):
    pool = get_redis_pool(decode_responses=False)
    if not pool:
        logger.debug("REDIS_URL is not set falling back to memory cache")
        return cachetools_ttl_cache(*args, ttl=ttl, **kwargs)

    def decorator(func):
        cached_func = RedisCached(
            pool, ttl, function=func, is_method=is_method, cache_falsy=cache_falsy, serializer=pickle.dumps, deserializer=pickle.loads)

        def wrapper(*args, **kwargs):
            # Re-wrapping to preserve function signature
            return cached_func(*args, **kwargs)

        functools.update_wrapper(wrapper, func)
        wrapper.cache_clear = cached_func.clear_all
        return wrapper
    return decorator


@contextmanager
def invalidates(*cached_funcs):
    for f in cached_funcs:
        f.cache_clear()
    yield None
    for f in cached_funcs:
        f.cache_clear()

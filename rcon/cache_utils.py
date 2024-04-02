import functools
import logging
import os
import pickle
from contextlib import contextmanager
from typing import Callable

import redis
import redis.exceptions
import simplejson
from cachetools.func import ttl_cache as cachetools_ttl_cache

logger = logging.getLogger(__name__)

_REDIS_POOL = None


class RedisCached:
    PREFIX = "cached_"

    def __init__(
        self,
        pool,
        ttl_seconds,
        function,
        function_cache_unavailable: Callable | None = None,
        red: redis.StrictRedis | None = None,
        is_method=False,
        cache_falsy=True,
        serializer=simplejson.dumps,
        deserializer=simplejson.loads,
    ):
        # TODO: isinstance check ttl_seconds it must be an int
        # not a float or anything else
        if pool is None:
            pool = get_redis_pool()

        if red is None:
            self.red = redis.Redis(connection_pool=pool)
        else:
            self.red = red
        self.function = function
        self.function_cache_unavailable = function_cache_unavailable
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
        return f"{self.PREFIX}{self.function.__qualname__}"

    def key(self, *args, **kwargs):
        if self.is_method:
            args = args[1:]
        params = self.serializer({"args": args, "kwargs": kwargs})
        if isinstance(params, bytes):
            return self.key_prefix.encode() + b"__" + params
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
        func = self.function
        try:
            val = self.red.get(key)
        except redis.exceptions.RedisError as e:
            logger.exception("Unable to use cache: %s", e)
            if self.function_cache_unavailable:
                func = self.function_cache_unavailable
                logger.error("Using fallback function due to cache failure: %s", func)

        if val is not None:
            # logger.debug("Cache HIT for %s", self.key(*args, **kwargs))
            return self.deserializer(val)

        # logger.debug("Cache MISS for %s", self.key(*args, **kwargs))
        val = func(*args, **kwargs)

        if not val and not self.cache_falsy:
            logger.debug("Caching falsy result is disabled for %s", self.__name__)
            return val

        try:
            self.red.setex(key, self.ttl_seconds, self.serializer(val))
            # logger.debug("Cache SET for %s", self.key(*args, **kwargs))
        except redis.exceptions.RedisError:
            logger.exception("Unable to set cache")

        return val

    def get_cached_value_for(self, *args, **kwargs):
        if self.is_method:
            key = self.key(None, *args, **kwargs)
        else:
            key = self.key(*args, **kwargs)
        return self.red.get(key)

    def clear_for(self, *args, **kwargs):
        if self.is_method:
            key = self.key(None, *args, **kwargs)
        else:
            key = self.key(*args, **kwargs)
        logger.debug("Invalidating cache for %s", key)
        if key:
            self.red.delete(key)

    def clear_all(self):
        try:
            keys = list(self.red.scan_iter(match=f"{self.key_prefix}*"))
            if keys:
                self.red.delete(*keys)
        except redis.exceptions.RedisError:
            logger.exception("Unable to clear cache")
        # else:
        #   logger.debug("Cache CLEARED for %s", keys)


def get_redis_pool(decode_responses=True):
    global _REDIS_POOL
    redis_url = os.getenv("HLL_REDIS_URL")
    if not redis_url:
        return None

    if _REDIS_POOL is None:
        logger.info("Redis pool initializing")
        _REDIS_POOL = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=1000,
            socket_connect_timeout=5,
            socket_timeout=5,
            decode_responses=decode_responses,
        )

    return _REDIS_POOL


def get_redis_client(decode_responses=True):
    pool = get_redis_pool(decode_responses)
    return redis.Redis(connection_pool=pool)


def ttl_cache(
    ttl,
    *args,
    is_method=True,
    cache_falsy=True,
    function_cache_unavailable=None,
    **kwargs,
):
    pool = get_redis_pool(decode_responses=False)
    # Allow use of in memory cache and not redis when running tests
    # but still use redis when running the development web server
    if os.getenv("DEBUG") and not pool:
        logger.warning(f"Unable to connect to Redis, using memory cache")
        return cachetools_ttl_cache(*args, ttl=ttl, **kwargs)
    # the maintenance container does not use the redis cache but this method is imported
    # and it will fail if it can't connect to redis otherwise
    elif os.getenv("HLL_MAINTENANCE_CONTAINER") and not pool:
        # skip logging but still use the in memory cache tools to allow importing
        return cachetools_ttl_cache(*args, ttl=ttl, **kwargs)
    if not pool:
        logger.error("Unable to connect to Redis")
        raise ConnectionError("Unable to connect to Redis")

    def decorator(func):
        cached_func = RedisCached(
            pool,
            ttl,
            function=func,
            function_cache_unavailable=function_cache_unavailable,
            is_method=is_method,
            cache_falsy=cache_falsy,
            serializer=pickle.dumps,
            deserializer=pickle.loads,
        )

        def wrapper(*args, **kwargs):
            # Re-wrapping to preserve function signature
            return cached_func(*args, **kwargs)

        functools.update_wrapper(wrapper, func)
        wrapper.cache_clear = cached_func.clear_all
        wrapper.get_cached_value_for = cached_func.get_cached_value_for
        wrapper.clear_for = cached_func.clear_for
        wrapper.cache = cached_func
        return wrapper

    return decorator


@contextmanager
def invalidates(*cached_funcs):
    for f in cached_funcs:
        f.cache_clear()
    yield None
    for f in cached_funcs:
        f.cache_clear()

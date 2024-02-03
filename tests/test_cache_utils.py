import os
from logging import getLogger
from unittest import mock

import redis
import redis.exceptions

from rcon.cache_utils import RedisCached, ttl_cache

logger = getLogger(__name__)


class MockRedis:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get(self, key):
        raise redis.exceptions.RedisError

    def setex(self, _1, _2, _3):
        pass


def _needs_qual_name():
    pass


def test_cache_unavailable(monkeypatch):
    cached_func = mock.Mock(spec=_needs_qual_name)
    uncached_func = mock.Mock(spec=_needs_qual_name)

    c = RedisCached(
        pool=None,
        red=MockRedis(),
        ttl_seconds=1,
        function=cached_func,
        function_cache_unavailable=uncached_func,
        serializer=lambda x: None,
        deserializer=lambda x: None,
    )

    c()

    uncached_func.assert_called()
    cached_func.assert_not_called()


def test_cache_available():
    cached_func = mock.Mock(spec=_needs_qual_name)
    uncached_func = mock.Mock(spec=_needs_qual_name)

    c = RedisCached(
        pool=None,
        ttl_seconds=1,
        function=cached_func,
        function_cache_unavailable=uncached_func,
        serializer=lambda x: str(x),
        deserializer=lambda x: str(x),
    )

    c()

    # This test will only run successfully if there is an actual redis instance
    if os.getenv("HLL_REDIS_URL"):
        cached_func.assert_called()
        uncached_func.assert_not_called()


def test_mem_cache_used(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")
    # This is kind of janky but cachetools returns a decorated function not a class instance
    # so we can't isinstance check it
    c = ttl_cache(ttl=1)
    assert not isinstance(c, RedisCached)

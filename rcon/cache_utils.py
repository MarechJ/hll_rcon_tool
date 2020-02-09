import redis


#REDIS_POOL = redis.BlockingConnectionPool(max_connections=20, host='localhost', port=6379, db=0)


def ttl_cache(ttl, invalidate_on=None, serialize_args=None):
    r = redis.Redis(connection_pool=REDIS_POOL)
    pass

import logging
import os
import redis
from rconweb.settings import ENVIRONMENT

INSTANCE_KEY_PREFIX = "rcon_instance_{}"

def _get_main_redis_db():
    redis_url = os.getenv('REDIS_URL')
    redis_url = redis_url[:-1] + "0"
    return redis.from_url(redis_url)

def register_instance():
    red = _get_main_redis_db()
    title = os.getenv('SERVER_SHORT_NAME')
    external_port = os.getenv('RCONWEB_PORT')
    red.set(INSTANCE_KEY_PREFIX.format(external_port), title)

def get_registered_instance():
    red = _get_main_redis_db()
    keys = red.keys(INSTANCE_KEY_PREFIX.format('*'))
    return [
        dict(
            title=red.get(k).decode('utf-8'),
            port=k.decode('utf-8').replace(INSTANCE_KEY_PREFIX.format(''), '')
        )
        for k in keys
    ]

register_instance()
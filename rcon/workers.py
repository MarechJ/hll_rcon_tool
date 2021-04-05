import time
from redis import Redis
from rq import Queue
from datetime import timedelta
from rcon.cache_utils import get_redis_client
from rcon.settings import SERVER_INFO


def get_queue(redis_client=None):
    red = get_redis_client()
    return Queue(connection=red)


def broadcast(msg):
    from rcon.recorded_commands import RecordedRcon

    rcon = RecordedRcon(SERVER_INFO)
    rcon.set_broadcast(msg)


def temporary_broadcast(rcon, message, seconds):
    prev = rcon.set_broadcast(message, save=False)
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=seconds), broadcast, prev)


def welcome(msg):
    from rcon.recorded_commands import RecordedRcon

    rcon = RecordedRcon(SERVER_INFO)
    rcon.set_welcome_message(msg)


def temporary_welcome(rcon, message, seconds):
    prev = rcon.set_welcome_message(message, save=False)
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=seconds), welcome, prev)


def temp_welcome_standalone(msg, seconds):
    from rcon.recorded_commands import RecordedRcon

    rcon = RecordedRcon(SERVER_INFO)
    prev = rcon.set_welcome_message(msg, save=False)
    time.sleep(seconds)
    rcon.set_welcome_message(prev)
    

def temporary_welcome_in(message, seconds, restore_after_seconds):
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=seconds), temp_welcome_standalone, message, restore_after_seconds)
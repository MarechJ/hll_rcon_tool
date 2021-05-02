from logging import Logger
import logging
import datetime
import os
from rcon.utils import map_name
import time
from redis import Redis
from rq import Queue, queue
from datetime import timedelta
from rcon.cache_utils import get_redis_client
from rcon.settings import SERVER_INFO
from rcon.models import enter_session, Maps, PlayerStats
from rcon.scoreboard import TimeWindowStats
from rcon.player_history import get_player
from sqlalchemy import and_

logger = logging.getLogger("rcon")


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
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds), welcome, prev)


def temporary_welcome_in(message, seconds, restore_after_seconds):
    queue = get_queue()
    queue.enqueue_in(
        timedelta(seconds=seconds),
        temp_welcome_standalone,
        message,
        restore_after_seconds,
    )


def get_or_create_map(sess, start, end, server_number, map_name):
    map_ = sess.query(Maps).filter(and_(Maps.start == start, Maps.end == end, Maps.server_number == server_number, Maps.map_name == map_name)).one_or_none()
    if map_:
        logger.warning("Map already exists %s", map_.to_dict())
        return map_
    map_ = Maps(
            start=start,
            end=end,
            server_number=server_number,
            map_name=map_name,
        )
    sess.add(map_)
    sess.commit()
    return map_

def record_stats_worker(map_info):
    queue = get_queue()
    queue.enqueue(record_stats, map_info)


def record_stats(map_info):
    logger.info("Recording stats for %s", map_info)
    try: 
        _record_stats(map_info)
        logger.info("Done recording stats for %s", map_info)
    except Exception:
        logger.exception("Unexpected error while recording stats for %s", map_info)

def _record_stats(map_info):
    stats = TimeWindowStats()

    start = datetime.datetime.fromtimestamp(map_info.get('start'))
    end = datetime.datetime.fromtimestamp(map_info.get('end'))

    if not start or not end:
        logger.error("Can't record stats, no time info for %s", map_info)
        return

    with enter_session() as sess:
        map = get_or_create_map(sess=sess, start=start, end=end, server_number=os.getenv("SERVER_NUMBER"), map_name=map_info["name"])
        player_stats = stats.get_players_stats_at_time(from_=start, until=end)
        for player, stats in player_stats.items():
            if steam_id_64 := stats.get("steam_id_64"):
                player_record = get_player(sess, steam_id_64=steam_id_64)
                if not player_record:
                    logger.error("Can't find DB record for %s", steam_id_64)
                    continue
                
                player_stats = dict(
                    playersteamid_id=player_record.id,
                    map_id=map.id,
                    kills=stats.get("kills"),
                    kills_streak=stats.get("kills_streak"),
                    death=stats.get("death"),
                    deaths_without_kill_streak=stats.get("deaths_without_kill_streak"),
                    teamkills=stats.get("teamkills"),
                    teamkills_streak=stats.get("teamkills_streak"),
                    deaths_by_tk=stats.get("deaths_by_tk"),
                    deaths_by_tk_streak=stats.get("deaths_by_tk_streak"),
                    nb_vote_started=stats.get("nb_vote_started"),
                    nb_voted_yes=stats.get("nb_voted_yes"),
                    nb_voted_no=stats.get("nb_voted_no"),
                    time_seconds=stats.get("time_seconds"),
                    kills_per_minute=stats.get("kills_per_minute"),
                    deaths_per_minute=stats.get("deaths_per_minute"),
                    kill_death_ratio=stats.get("kill_death_ratio")
                )
                logger.debug(f"Saving stats %s", player_stats)
                player_stat_record = PlayerStats(
                   **player_stats
                )
                sess.add(player_stat_record)
            else:
                logger.error("Stat object does not contain a steam id: %s", stats)

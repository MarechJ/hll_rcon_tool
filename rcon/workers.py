import datetime
import logging
import os
from datetime import timedelta
from typing import Set

from concurrent.futures import as_completed
from dateutil import relativedelta
from rq import Queue
from rq.job import Job
from sqlalchemy import and_

from rcon.cache_utils import get_redis_client
from rcon.models import Maps, PlayerStats, enter_session
from rcon.player_history import get_player
from rcon.recorded_commands import RecordedRcon
from rcon.scoreboard import TimeWindowStats
from rcon.settings import SERVER_INFO

logger = logging.getLogger("rcon")


def get_queue(redis_client=None):
    red = get_redis_client()
    return Queue(connection=red, default_timeout=60 * 20)


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
    map_ = (
        sess.query(Maps)
        .filter(
            and_(
                Maps.start == start,
                Maps.end == end,
                Maps.server_number == server_number,
                Maps.map_name == map_name,
            )
        )
        .one_or_none()
    )
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
    queue.enqueue_in(timedelta(seconds=60 * 6), record_stats, map_info)


def record_stats(map_info):
    logger.info("Recording stats for %s", map_info)
    try:
        _record_stats(map_info)
        logger.info("Done recording stats for %s", map_info)
    except Exception:
        logger.exception("Unexpected error while recording stats for %s", map_info)


def _record_stats(map_info=None, map=None):
    start = datetime.datetime.utcfromtimestamp(map_info.get("start"))
    end = datetime.datetime.utcfromtimestamp(map_info.get("end"))

    if not start or not end:
        logger.error("Can't record stats, no time info for %s", map_info)
        return

    with enter_session() as sess:
        map_ = get_or_create_map(
            sess=sess,
            start=start,
            end=end,
            server_number=os.getenv("SERVER_NUMBER"),
            map_name=map_info["name"],
        )
        record_stats_from_map(sess, map_)
        sess.commit()


def record_stats_from_map(sess, map_):
    stats = TimeWindowStats()
    player_stats = stats.get_players_stats_at_time(
        from_=map_.start, until=map_.end, server_number=str(map_.server_number)
    )

    seen_players: Set[str] = set()
    for player, stats in player_stats.items():
        if steam_id_64 := stats.get("steam_id_64"):

            # If a player has changed their name and had stats recorded under two or more
            # names in the same match it will otherwise try to insert duplicate records
            # This will only record stats for the first instance of the player it sees, the other(s)
            # will be lost of course
            if steam_id_64 in seen_players:
                logger.info(f"Failed to record duplicate stats for {steam_id_64}")
                continue
            seen_players.add(steam_id_64)

            player_record = get_player(sess, steam_id_64=steam_id_64)
            if not player_record:
                logger.error("Can't find DB record for %s", steam_id_64)
                continue

            player_stats = dict(
                playersteamid_id=player_record.id,
                map_id=map_.id,
                name=stats.get("player"),
                kills=stats.get("kills"),
                kills_streak=stats.get("kills_streak"),
                deaths=stats.get("deaths"),
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
                kill_death_ratio=stats.get("kill_death_ratio"),
                longest_life_secs=stats.get("longest_life_secs"),
                shortest_life_secs=stats.get("shortest_life_secs"),
                weapons=stats.get("weapons"),
                most_killed=stats.get("most_killed"),
                death_by=stats.get("death_by"),
            )
            logger.debug(f"Saving stats %s", player_stats)
            player_stat_record = PlayerStats(**player_stats)
            sess.add(player_stat_record)
        else:
            logger.error("Stat object does not contain a steam id: %s", stats)


def get_job_results(job_key):
    job = Job.fetch(job_key, connection=get_redis_client())
    if not job:
        return {
            "status": "Job not found or expired",
            "result": None,
            "started_at": None,
            "ended_at": None,
            "func_name": None,
        }
    return {
        "status": job.get_status(),
        # avoid showing previous' job result if they use the same id
        "result": job.result if job.get_status() == "finished" else None,
        "started_at": job.started_at,
        "ended_at": job.ended_at,
        "func_name": job.func_name,
        "check_timestamp": datetime.datetime.now().timestamp(),
    }


def worker_bulk_vip(name_ids, job_key, mode="override"):
    queue = get_queue()
    return queue.enqueue(
        bulk_vip,
        name_ids=name_ids,
        mode=mode,
        result_ttl=6000,
        job_timeout=1200,
        job_id=job_key,
    )


def bulk_vip(name_ids, mode="override"):
    errors = []
    ctl = RecordedRcon(SERVER_INFO)
    logger.info(f"bulk_vip name_ids {name_ids[0]} type {type(name_ids)}")
    vips = ctl.get_vip_ids()

    removal_futures = {
        ctl.run_in_pool(idx, "do_remove_vip", vip["steam_id_64"]): vip
        for idx, vip in enumerate(vips)
    }
    for future in as_completed(removal_futures):
        try:
            result = future.result()
            if result != "SUCCESS":
                errors.append(f"Failed to add {removal_futures[future]}")
        except Exception:
            logger.exception(f"Failed to remove vip from {removal_futures[future]}")

    processed_additions = []
    for name, steam_id, expiration_timestamp in name_ids:
        if not expiration_timestamp:
            expiration_timestamp = (
                datetime.datetime.utcnow() + relativedelta.relativedelta(years=200)
            ).isoformat()
        else:
            expiration_timestamp = expiration_timestamp.isoformat()

        processed_additions.append((name, steam_id, expiration_timestamp))

    add_futures = {
        ctl.run_in_pool(
            idx,
            "do_add_vip",
            name,
            steam_id,
            expiration=expiration_timestamp,
        ): steam_id
        for idx, (name, steam_id, expiration_timestamp) in enumerate(
            processed_additions
        )
    }
    for future in as_completed(add_futures):
        try:
            result = future.result()
            if result != "SUCCESS":
                errors.append(f"Failed to add {add_futures[future]}")
        except Exception:
            logger.exception(f"Failed to add vip to {add_futures[future]}")

    if not errors:
        errors.append("ALL OK")
    return errors

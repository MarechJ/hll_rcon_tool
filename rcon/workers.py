import datetime
import logging
import os
from concurrent.futures import as_completed
from datetime import timedelta
from typing import Set

from rq import Queue
from rq.job import Job
from sqlalchemy import and_
from sqlalchemy.orm import Session

from rcon.cache_utils import get_redis_client
from rcon.models import Maps, PlayerStats, enter_session
from rcon.player_history import get_player
from rcon.scoreboard import TimeWindowStats
from rcon.types import MapInfo, PlayerStat
from rcon.utils import INDEFINITE_VIP_DATE

logger = logging.getLogger("rcon")


def get_queue(redis_client=None):
    red = get_redis_client()
    return Queue(connection=red, default_timeout=60 * 20)


def broadcast(msg):
    from rcon.api_commands import get_rcon_api

    rcon = get_rcon_api()
    rcon.set_broadcast(msg)


def temporary_broadcast(rcon, message, seconds):
    prev = rcon.set_broadcast(message, save=False)
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=seconds), broadcast, prev)


def welcome(msg):
    from rcon.api_commands import get_rcon_api

    rcon = get_rcon_api()
    rcon.set_welcome_message(msg)


def temporary_welcome(rcon, message, seconds):
    prev = rcon.set_welcome_message(message)
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=seconds), welcome, prev)


def temp_welcome_standalone(msg, seconds):
    from rcon.api_commands import get_rcon_api

    rcon = get_rcon_api()
    prev = rcon.set_welcome_message(msg)
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


def record_stats_worker(map_info: MapInfo):
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=60 * 6), record_stats, map_info)


def record_stats(map_info: MapInfo):
    logger.info("Recording stats for %s", map_info)
    try:
        _record_stats(map_info)
        logger.info("Done recording stats for %s", map_info)
    except Exception:
        logger.exception("Unexpected error while recording stats for %s", map_info)


def _record_stats(map_info: MapInfo):
    raw_start = map_info.get("start")
    raw_end = map_info.get("end")

    if not raw_start or not raw_end:
        logger.error("Can't record stats, no time info for %s", map_info)
        return

    start = datetime.datetime.utcfromtimestamp(raw_start)
    end = datetime.datetime.utcfromtimestamp(raw_end)
    with enter_session() as sess:
        map_ = get_or_create_map(
            sess=sess,
            start=start,
            end=end,
            server_number=os.getenv("SERVER_NUMBER"),
            map_name=map_info["name"],
        )
        record_stats_from_map(sess, map_, map_info.get("player_stats", dict()))
        sess.commit()


def record_stats_from_map(
    sess: Session, map_, ps: dict[str, PlayerStat] = (), force: bool = False
):
    stats = TimeWindowStats()
    player_stats = stats.get_players_stats_at_time(
        from_=map_.start, until=map_.end, server_number=str(map_.server_number)
    )

    seen_players: Set[str] = set()
    for player, stats in player_stats.items():
        if player_id := stats.get("player_id"):
            # If a player has changed their name and had stats recorded under two or more
            # names in the same match it will otherwise try to insert duplicate records
            # This will only record stats for the first instance of the player it sees, the other(s)
            # will be lost of course
            if player_id in seen_players:
                logger.info(f"Failed to record duplicate stats for {player_id}")
                continue
            seen_players.add(player_id)

            player_record = get_player(sess, player_id=player_id)
            if not player_record:
                logger.error("Can't find DB record for %s", player_id)
                continue

            existing: PlayerStats | None = (
                sess.query(PlayerStats)
                .filter(
                    PlayerStats.map_id == map_.id,
                    PlayerStats.player_id_id == player_record.id,
                )
                .one_or_none()
            )
            default_stat = PlayerStat(combat=0, offense=0, defense=0, support=0)
            if existing is not None:
                default_stat = PlayerStat(
                    combat=existing.combat,
                    offense=existing.offense,
                    defense=existing.defense,
                    support=existing.support,
                )
            map_stats: PlayerStat = ps.get(player_id, default_stat)
            player_stat = dict(
                player_id_id=player_record.id,
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
                death_by_weapons=stats.get("death_by_weapons"),
                combat=map_stats.get("combat", 0) + map_stats.get("p_combat", 0),
                offense=map_stats.get("offense", 0) + map_stats.get("p_offense", 0),
                defense=map_stats.get("defense", 0) + map_stats.get("p_defense", 0),
                support=map_stats.get("support", 0) + map_stats.get("p_support", 0),
            )
            if existing is not None and force != True:
                continue
            elif existing is not None and force == True:
                logger.debug(f"Updating stats %s", player_stat)
                existing.kills = player_stat.get("kills")
                existing.kills_streak = player_stat.get("kills_streak")
                existing.deaths = player_stat.get("deaths")
                existing.deaths_without_kill_streak = player_stat.get(
                    "deaths_without_kill_streak"
                )
                existing.teamkills = player_stat.get("teamkills")
                existing.teamkills_streak = player_stat.get("teamkills_streak")
                existing.deaths_by_tk = player_stat.get("deaths_by_tk")
                existing.deaths_by_tk_streak = player_stat.get("deaths_by_tk_streak")
                existing.nb_vote_started = player_stat.get("nb_vote_started")
                existing.nb_voted_yes = player_stat.get("nb_voted_yes")
                existing.nb_voted_no = player_stat.get("nb_voted_no")
                existing.time_seconds = player_stat.get("time_seconds")
                existing.kills = player_stat.get("kills")
                existing.kills_per_minute = player_stat.get("kills_per_minute")
                existing.deaths_per_minute = player_stat.get("deaths_per_minute")
                existing.kill_death_ratio = player_stat.get("kill_death_ratio")
                existing.longest_life_secs = player_stat.get("longest_life_secs")
                existing.shortest_life_secs = player_stat.get("shortest_life_secs")
                existing.weapons = player_stat.get("weapons")
                existing.most_killed = player_stat.get("most_killed")
                existing.death_by = player_stat.get("death_by")
                existing.death_by_weapons = player_stat.get("death_by_weapons")
                existing.combat = player_stat.get("combat")
                existing.offense = player_stat.get("offense")
                existing.defense = player_stat.get("defense")
                existing.support = player_stat.get("support")
            else:
                logger.debug(f"Saving stats %s", player_stat)
                player_stat_record = PlayerStats(**player_stat)
                sess.add(player_stat_record)
        else:
            logger.error("Stat object does not contain a player ID: %s", stats)


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
    from rcon.api_commands import get_rcon_api

    ctl = get_rcon_api()
    errors = []
    logger.info(f"bulk_vip name_ids {name_ids[0]} type {type(name_ids)}")
    vips = ctl.get_vip_ids()

    removal_futures = {
        ctl.run_in_pool("remove_vip", vip["player_id"]): vip
        for idx, vip in enumerate(vips)
    }
    for future in as_completed(removal_futures):
        try:
            result = future.result()
            if not result:
                errors.append(f"Failed to add {removal_futures[future]}")
        except Exception:
            logger.exception(f"Failed to remove vip from {removal_futures[future]}")

    processed_additions = []
    for description, player_id, expiration_timestamp in name_ids:
        if not expiration_timestamp:
            expiration_timestamp = INDEFINITE_VIP_DATE.isoformat()
        else:
            expiration_timestamp = expiration_timestamp.isoformat()

        processed_additions.append((description, player_id, expiration_timestamp))

    add_futures = {
        ctl.run_in_pool(
            "add_vip",
            player_id=player_id,
            description=description,
            expiration=expiration_timestamp,
        ): player_id
        for idx, (description, player_id, expiration_timestamp) in enumerate(
            processed_additions
        )
    }
    for future in as_completed(add_futures):
        try:
            result = future.result()
            if not result:
                errors.append(f"Failed to add {add_futures[future]}")
        except Exception:
            logger.exception(f"Failed to add vip to {add_futures[future]}")

    if not errors:
        errors.append("ALL OK")
    return errors

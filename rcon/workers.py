import datetime
import logging
import os
from concurrent.futures import as_completed
from datetime import timedelta
from typing import Any, Optional, Set

from rq import Queue
from rq.job import Job, Retry
from sqlalchemy import and_
from sqlalchemy.orm import Session

from rcon.cache_utils import get_redis_client
from rcon.game_logs import get_historical_logs_records
from rcon.models import Maps, PlayerStats, enter_session
from rcon.player_history import get_player
from rcon.player_stats import TimeWindowStats
from rcon.types import MapInfo, MapScore, PlayerStat, GameLayout
from rcon.utils import GAME_LOG_STAT_FIELDS, INDEFINITE_VIP_DATE, TEMP_FIELDS, MapsHistory, get_temp_default_stats

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
    queue.enqueue_in(timedelta(seconds=seconds), welcome, prev)


def temporary_welcome_in(message, seconds, restore_after_seconds):
    queue = get_queue()
    queue.enqueue_in(
        timedelta(seconds=seconds),
        temp_welcome_standalone,
        message,
        restore_after_seconds,
    )


def get_or_create_map(sess: Session, start: datetime.datetime, end: datetime.datetime, server_number: int, map_name: str, game_layout: GameLayout, cap_flips: list[MapScore], match_time: int):
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
        game_layout=game_layout,
        cap_flips=cap_flips,
        match_time=match_time,
    )
    sess.add(map_)
    sess.commit()
    return map_


def record_stats_worker(map_info: MapInfo):
    queue = get_queue()
    # tries to record stats instantly and retries up to 5 times, e.g. when the game logs are
    # not yet saved in the database.
    # One possible expected exception occurs when the game logs are not yet dumped into the db. This retries should
    # therefore be higher than the default dump interval of logs in LogRecorder
    queue.enqueue(record_stats, map_info, retry=Retry(max=15, interval=30))


def record_stats(map_info: MapInfo):
    logger.info("Recording stats for %s", map_info)
    try:
        _record_stats(map_info)
        logger.info("Done recording stats for %s", map_info)
    except Exception as e:
        logger.exception("Unexpected error while recording stats for %s", map_info)
        raise e

def clear_stats_cache(map: Maps, map_info: MapInfo | None):
    # ensure the map result and stats were saved
    if map_info is None or map.result is None:
        return
    maps_history = MapsHistory()
    map_index, map_to_update = next(((idx, m) for idx, m in enumerate(maps_history) if m["start"] == map_info["start"] and m["end"] == map_info["end"] and m["name"] == map_info["name"]), (None, None))
    if not map_index or not map_to_update:
        return
    map_to_update["player_stats"] = {}
    map_to_update["cap_flips"] = []
    maps_history.update(map_index, map_to_update)

def _record_stats(map_info: MapInfo):
    raw_start = map_info.get("start")
    raw_end = map_info.get("end")

    if not raw_start or not raw_end:
        logger.error("Can't record stats, no time info for %s", map_info)
        return

    start = datetime.datetime.fromtimestamp(raw_start, datetime.timezone.utc)
    end = datetime.datetime.fromtimestamp(raw_end, datetime.timezone.utc)
    with enter_session() as sess:
        map_ = get_or_create_map(
            sess=sess,
            start=start,
            end=end,
            server_number=int(os.getenv("SERVER_NUMBER")),
            map_name=map_info["name"],
            game_layout=map_info["game_layout"] if "game_layout" in map_info else GameLayout(requested=[], set=[]),
            cap_flips=map_info["cap_flips"],
            match_time=map_info["match_time"],
        )
        record_stats_from_map(sess, map_, map_info)
        clear_stats_cache(map_, map_info)
        sess.commit()

def _compute_temporary_stats(temp_stats: dict[str, Any]) -> dict[str, int]:
    """Add any p_* [shortly for prev] contributions to produce final values."""
    adjusted = {}
    for field, p_field in TEMP_FIELDS.items():
        base = temp_stats.get(field)
        p_val = temp_stats.get(p_field)
        if isinstance(p_val, int) and base:
            adjusted[field] = base + p_val
        else:
            adjusted[field] = base
    return adjusted

def _build_player_stat_dict(
    player_id_id: int,
    map_id: int,
    game_log_stats: dict[str, Any],
    temp_stats: dict[str, Any],
) -> dict[str, Any]:
    """Combine game log stats with temp stats values."""
    adjusted = _compute_temporary_stats(temp_stats)
    return {
        "player_id_id": player_id_id,
        "map_id": map_id,
        "name": game_log_stats.get("player"),
        **{field: game_log_stats.get(field) for field in GAME_LOG_STAT_FIELDS},
        **adjusted,
    }

def _are_match_logs_available(session: Session, map: Maps) -> bool:
    # A game can either be ended by a MATCH ENDED log event (when the game ended normally after a 5-0 win or the
    # match time is up) or when a new MATCH STARTED log event occurred (e.g. on a map change or objective change).
    # If both did not happen in the historical logs, assume that the LogRecorder did not yet dumped the logs into the
    # database.

    match_ended_search = get_historical_logs_records(
        session,
        from_=map.start,
        till=map.end,
        time_sort="asc",
        action="MATCH ENDED",
        exact_action=True,
        server_filter=str(map.server_number),
        limit=1,
    )
    if len(match_ended_search) > 0:
        logger.debug("match logs available based on found 'MATCH ENDED' log")
        return True
    
    match_started_search = get_historical_logs_records(
        session,
        from_=map.start,
        till=map.end + datetime.timedelta(seconds=30),
        time_sort="asc",
        action="MATCH START",
        exact_action=True,
        server_filter=str(map.server_number),
        limit=2,
    )

    if len(match_started_search) > 1:
        logger.debug("match logs available based on found 'MATCH START' log")
        return True

    return False

def _save_match_result(session: Session, map: Maps):
    game_log_stats = TimeWindowStats()
    map.result = game_log_stats.map_result(
        from_=map.start, until=map.end, server_number=str(map.server_number)
    )
    logger.info("Saving map result: %s", map.result)
    session.add(map)

def _get_game_logs_stats(session: Session, map: Maps):
    game_log_stats = TimeWindowStats()
    return game_log_stats.get_players_stats_at_time(
        from_=map.start, until=map.end, server_number=str(map.server_number)
    )

def record_stats_from_map(
    sess: Session, map_: Maps, map_info: MapInfo | None, force: bool = False
) -> None:
    if not _are_match_logs_available(sess, map_):
        # An exception will automatically re-enqueue the record stats task.
        raise Exception("match logs are not yet available, skipping recording stats")

    temp_stats = map_info.get("player_stats", {}) if map_info else {}

    _save_match_result(sess, map_)

    seen_players: Set[str] = set()
    for _, player_game_log_stats in _get_game_logs_stats(sess, map_).items():
        player_id = player_game_log_stats.get("player_id")
        if not player_id:
            logger.error("Stat object does not contain a player ID: %s", player_game_log_stats)
            continue

        if player_id in seen_players:
            logger.info(f"Failed to record duplicate stats for {player_id}")
            continue

        seen_players.add(player_id)

        player_record = get_player(sess, player_id=player_id)
        if not player_record:
            logger.error("Can't find DB record for %s", player_id)
            continue

        # Check for any already recorded stats
        existing: Optional["PlayerStats"] = (
            sess.query(PlayerStats)
            .filter(
                PlayerStats.map_id == map_.id,
                PlayerStats.player_id_id == player_record.id,
            )
            .one_or_none()
        )

        # The stats were already recorded once
        if existing is not None and not force:
            continue

        player_temp_stats = temp_stats.get(player_id, get_temp_default_stats(existing))

        combined_player_stats = _build_player_stat_dict(
            player_record.id, map_.id, player_game_log_stats, player_temp_stats
        )

        if existing is not None and force:
            logger.debug("Updating stats for player %s on map %s", player_id, map_.id)
            for key, value in combined_player_stats.items():
                if key not in ("player_id_id", "map_id"):
                    setattr(existing, key, value)
            continue
        
        logger.debug("Saving stats for player %s on map %s", player_id, map_.id)
        player_stat_record = PlayerStats(**combined_player_stats)
        sess.add(player_stat_record)

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

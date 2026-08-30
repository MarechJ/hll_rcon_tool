"""Persistent per-server status for VIP List synchronization."""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import redis

from rcon.vip_sync_executor import VipSyncExecutionResult

logger = logging.getLogger(__name__)

STATUS_KEY_PREFIX = "vip-list-sync-status"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _status_key(server_number: int) -> str:
    return f"{STATUS_KEY_PREFIX}:{int(server_number)}"


def _get_redis() -> redis.Redis:
    redis_url = os.getenv("HLL_REDIS_URL")
    if not redis_url:
        raise RuntimeError("HLL_REDIS_URL not set")

    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
    )


def get_vip_sync_status(server_number: int) -> dict[str, Any] | None:
    """Return the most recently recorded synchronization status."""
    red = _get_redis()
    try:
        payload = red.get(_status_key(server_number))
    finally:
        red.close()

    if payload is None:
        return None

    status = json.loads(payload)
    if not isinstance(status, dict):
        raise TypeError("Invalid VIP synchronization status payload")

    return status


def _read_existing_status(
    red: redis.Redis,
    server_number: int,
) -> dict[str, Any]:
    payload = red.get(_status_key(server_number))
    if payload is None:
        return {}

    status = json.loads(payload)
    return status if isinstance(status, dict) else {}


def _store_status(
    red: redis.Redis,
    server_number: int,
    status: dict[str, Any],
) -> None:
    red.set(
        _status_key(server_number),
        json.dumps(status, separators=(",", ":"), sort_keys=True),
    )


def record_vip_sync_started(
    server_number: int,
    trigger: str,
) -> None:
    """Record the start of a real synchronization run."""
    try:
        red = _get_redis()
        try:
            existing = _read_existing_status(red, server_number)
            _store_status(
                red,
                server_number,
                {
                    "server_number": int(server_number),
                    "state": "running",
                    "trigger": str(trigger),
                    "started_at": _utc_now(),
                    "completed_at": None,
                    "last_success_at": existing.get("last_success_at"),
                    "added": 0,
                    "removed": 0,
                    "failures": [],
                },
            )
        finally:
            red.close()
    except Exception:
        logger.exception(
            "Unable to record VIP synchronization start for server %s",
            server_number,
        )


def record_vip_sync_completed(
    server_number: int,
    trigger: str,
    execution: VipSyncExecutionResult,
) -> None:
    """Record the result of a completed synchronization run."""
    try:
        red = _get_redis()
        try:
            existing = _read_existing_status(red, server_number)
            completed_at = _utc_now()
            successful = execution.successful

            _store_status(
                red,
                server_number,
                {
                    "server_number": int(server_number),
                    "state": "successful" if successful else "failed",
                    "trigger": str(trigger),
                    "started_at": existing.get("started_at"),
                    "completed_at": completed_at,
                    "last_success_at": (
                        completed_at if successful else existing.get("last_success_at")
                    ),
                    "added": len(execution.added),
                    "removed": len(execution.removed),
                    "failures": [
                        {
                            "action": failure.action,
                            "player_id": failure.player_id,
                            "error": failure.error,
                        }
                        for failure in execution.failures
                    ],
                },
            )
        finally:
            red.close()
    except Exception:
        logger.exception(
            "Unable to record VIP synchronization result for server %s",
            server_number,
        )


def record_vip_sync_failed(
    server_number: int,
    trigger: str,
    error: BaseException,
) -> None:
    """Record a synchronization failure outside plan execution."""
    try:
        red = _get_redis()
        try:
            existing = _read_existing_status(red, server_number)
            _store_status(
                red,
                server_number,
                {
                    "server_number": int(server_number),
                    "state": "failed",
                    "trigger": str(trigger),
                    "started_at": existing.get("started_at"),
                    "completed_at": _utc_now(),
                    "last_success_at": existing.get("last_success_at"),
                    "added": 0,
                    "removed": 0,
                    "failures": [
                        {
                            "action": "synchronize",
                            "player_id": None,
                            "error": f"{type(error).__name__}: {error}",
                        }
                    ],
                },
            )
        finally:
            red.close()
    except Exception:
        logger.exception(
            "Unable to record VIP synchronization failure for server %s",
            server_number,
        )

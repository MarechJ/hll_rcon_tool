"""Redis-driven and periodic VIP List synchronization."""

import logging
import os
import struct
import time
from dataclasses import dataclass

import redis

from rcon.rcon import Rcon, get_rcon
from rcon.utils import get_server_number, server_numbers_to_mask
from rcon.vip_sync_runner import synchronize_gameserver_vips

logger = logging.getLogger(__name__)

ALL_SERVERS_MASK = 2**32 - 1
DEFAULT_SYNC_INTERVAL_SECONDS = 5 * 60


@dataclass(frozen=True)
class VipSyncCommand:
    """Request a full VIP synchronization on selected CRCON servers."""

    server_mask: int

    def encode(self) -> bytes:
        return struct.pack("I", self.server_mask)

    @classmethod
    def decode(cls, data: bytes) -> "VipSyncCommand":
        expected_size = struct.calcsize("I")
        if len(data) != expected_size:
            raise ValueError(f"Invalid VIP synchronization command size: {len(data)}")

        (server_mask,) = struct.unpack("I", data)
        return cls(server_mask=server_mask)


class VipSyncCommandHandler:
    """Synchronize this CRCON server after notifications and periodically."""

    CHANNEL = "vip-list-sync"

    def __init__(self) -> None:
        redis_url = os.getenv("HLL_REDIS_URL")
        if not redis_url:
            raise RuntimeError("HLL_REDIS_URL not set")

        self.red = redis.Redis.from_url(
            redis_url,
            single_connection_client=True,
            decode_responses=False,
        )
        self.pubsub = self.red.pubsub(ignore_subscribe_messages=True)
        self.rcon = get_rcon()
        self.server_number = int(get_server_number())
        self.server_mask = server_numbers_to_mask(self.server_number)
        self.interval_seconds = max(
            30,
            int(
                os.getenv(
                    "VIP_LIST_SYNC_INTERVAL_SECONDS",
                    DEFAULT_SYNC_INTERVAL_SECONDS,
                )
            ),
        )

    @staticmethod
    def send(server_mask: int | None) -> int:
        """Publish a synchronization request and return subscriber count."""
        normalized_mask = ALL_SERVERS_MASK if server_mask is None else int(server_mask)
        if normalized_mask == 0:
            return 0

        redis_url = os.getenv("HLL_REDIS_URL")
        if not redis_url:
            raise RuntimeError("HLL_REDIS_URL not set")

        red = redis.Redis.from_url(redis_url, decode_responses=False)
        try:
            return int(
                red.publish(
                    VipSyncCommandHandler.CHANNEL,
                    VipSyncCommand(normalized_mask).encode(),
                )
            )
        finally:
            red.close()

    def synchronize(self, trigger: str) -> None:
        """Perform one full synchronization without terminating on failure."""
        try:
            Rcon.get_vip_ids.cache_clear()
            result = synchronize_gameserver_vips(
                server_number=self.server_number,
                rcon=self.rcon,
                dry_run=False,
                trigger=trigger,
            )

            logger.info(
                "VIP List synchronization completed: trigger=%s "
                "additions=%s removals=%s failures=%s",
                trigger,
                len(result.plan.to_add),
                len(result.plan.to_remove),
                len(result.execution.failures),
            )
        except Exception:
            logger.exception(
                "VIP List synchronization failed: trigger=%s",
                trigger,
            )

    def run(self) -> None:
        """Listen for changes and run a periodic safety synchronization."""
        logger.info(
            "Starting VIP List synchronization handler for server %s "
            "with interval %s seconds",
            self.server_number,
            self.interval_seconds,
        )
        self.pubsub.subscribe(self.CHANNEL)

        self.synchronize(trigger="startup")
        next_periodic_sync = time.monotonic() + self.interval_seconds

        while True:
            remaining = max(0.0, next_periodic_sync - time.monotonic())
            message = self.pubsub.get_message(timeout=min(1.0, remaining))

            if message is not None:
                try:
                    command = VipSyncCommand.decode(message["data"])
                    if command.server_mask & self.server_mask:
                        self.synchronize(trigger="notification")
                except Exception:
                    logger.exception(
                        "Failed to process VIP List synchronization message"
                    )

            if time.monotonic() >= next_periodic_sync:
                self.synchronize(trigger="periodic")
                next_periodic_sync = time.monotonic() + self.interval_seconds

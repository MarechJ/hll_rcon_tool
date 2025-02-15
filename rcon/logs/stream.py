import datetime
import logging
import time
from collections import defaultdict

import redis

from rcon.cache_utils import get_redis_client
from rcon.rcon import Rcon, get_rcon
from rcon.types import StructuredLogLineWithMetaData
from rcon.user_config.log_stream import LogStreamUserConfig
from rcon.utils import Stream, StreamOlderElement, StreamID, StreamNoElements

logger = logging.getLogger(__name__)

class LogStream:
    # Each CRCON uses its own redis database, no need for keys to be unique across servers
    def __init__(
            self,
            rcon: Rcon | None = None,
            red: redis.StrictRedis | None = None,
            key="log_stream",
            maxlen: int | None = None,
    ) -> None:
        config = LogStreamUserConfig.load_from_db()
        self.rcon = rcon or get_rcon()
        self.red = red or get_redis_client()
        self.log_history_key = key
        self.log_stream = Stream(key=key, maxlen=maxlen or config.stream_size)

    def clear(self):
        logger.info("Clearing stream")
        self.red.delete(self.log_history_key)

    def bucket_by_timestamp(self, logs: list[StructuredLogLineWithMetaData]):
        """Organize logs by their game server timestamp

        Redis streams must be in sequential order, we use custom keys that are the
        unix timestamp of the time the log occurred on the game server, but each
        timestamp can have multiple logs.

        Return each unique timestamp and the logs that occured at that time
        """
        # logs has the newest logs first, oldest last
        buckets: dict[datetime.datetime, list[StructuredLogLineWithMetaData]] = (
            defaultdict(list)
        )

        ordered_logs: list[
            tuple[datetime.datetime, list[StructuredLogLineWithMetaData]]
        ] = []

        for log in reversed(logs):
            timestamp = datetime.datetime.fromtimestamp(log["timestamp_ms"] / 1000)
            buckets[timestamp].append(log)

        for timestamp in buckets.keys():
            ordered_logs.append((timestamp, buckets[timestamp]))

        return ordered_logs

    def run(
            self,
            loop_frequency_secs: int | None = None,
            initial_since_min: int | None = None,
            active_since_min: int | None = None,
    ):
        """Poll the game server and add new logs to the stream"""

        config = LogStreamUserConfig.load_from_db()

        since_min = initial_since_min or config.startup_since_mins
        logs = self.rcon.get_structured_logs(since_min_ago=since_min)["logs"]
        since_min = active_since_min or config.refresh_since_mins

        last_seen_id = None
        while True:
            config = LogStreamUserConfig.load_from_db()
            if not config.enabled:
                break
            ordered_logs = self.bucket_by_timestamp(logs)
            new_logs = 0
            for timestamp, log_bucket in ordered_logs:
                for idx, log in enumerate(log_bucket):
                    timestamp_ms = log["timestamp_ms"] // 1000
                    stream_id = f"{timestamp_ms}-{idx}"
                    try:
                        last_seen_id = self.log_stream.add(custom_id=stream_id, obj=log)
                        new_logs += 1
                    except StreamOlderElement:
                        continue

            if new_logs:
                logger.info(f"Added {new_logs} new logs {last_seen_id=}")
            time.sleep(loop_frequency_secs or config.refresh_frequency_sec)
            logs = self.rcon.get_structured_logs(since_min_ago=since_min)["logs"]

    def logs_since(
            self, last_seen: StreamID | None = None, block_ms=500
    ) -> list[tuple[StreamID, StructuredLogLineWithMetaData]]:
        """Return a list of logs more recent than the last_seen ID"""
        try:
            if last_seen is None:
                logs: list[tuple[StreamID, StructuredLogLineWithMetaData]] = []
                tail_log: tuple[StreamID, StructuredLogLineWithMetaData] = (
                    self.log_stream.tail()
                )
                if tail_log:
                    logs.append(tail_log)
            else:
                logs: list[tuple[StreamID, StructuredLogLineWithMetaData]] = (
                    self.log_stream.read(last_id=last_seen, block_ms=block_ms)
                )
            return logs
        except StreamNoElements:
            response: list[tuple[StreamID, StructuredLogLineWithMetaData]] = []
            return response

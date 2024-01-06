import time
from logging import getLogger

import redis
import redis.exceptions

from rcon.cache_utils import get_redis_client
from rcon.rcon import Rcon, get_rcon

logger = getLogger(__name__)

LOOP_FREQUENCY_SEC = 0.5


class Series:
    # CHILDREN MUST DEFINE A CLASS ATTRIBUTE: NAME
    NAME: str

    def __init__(
        self,
        client=None,
        min_resolution_ms=30000,
        retention_days=60,
        max_fails=5,
        slices=None,
    ):
        self.client: redis.Redis = client or get_redis_client()
        self.slices = slices or {
            "minute": (f"{self.NAME}avgRuleMinute", "avg", 1000 * 60),
            "hour": (f"{self.NAME}avgRuleHour", "avg", 1000 * 60 * 60),
            "day": (f"{self.NAME}avgRuleDay", "avg", 1000 * 60 * 60 * 24),
        }
        self.retention_msecs = 1000 * 60 * 60 * 24 * retention_days
        self.min_resolution_ms = min_resolution_ms / 1000
        self.last_run_time = 0
        self.fails = 0
        self.max_fails = max_fails

    def migrate(self):
        try:
            logger.debug(
                "Creating timeseries %s with ms retention %s",
                self.NAME,
                self.retention_msecs,
            )
            self.ts = self.client.ts().create(
                self.NAME, retention_msecs=self.retention_msecs
            )
        except redis.exceptions.ResponseError:
            logger.debug(
                "Already exists. Updating timeseries %s with ms retention %s",
                self.NAME,
                self.retention_msecs,
            )
            self.ts.alter(self.NAME, retention_msecs=self.retention_msecs)

        for rule_name, agg_method, time_resolution in self.slices.values():
            logger.debug("Creating timeseries aggregation %s", rule_name)
            try:
                self.client.ts().create(rule_name)
                self.client.ts().createrule(
                    self.NAME, rule_name, agg_method, time_resolution
                )
            except redis.exceptions.ResponseError:
                logger.debug("Already exists timeseries aggregation %s", rule_name)
                pass  # rule already exists
                # TODO: Handle change

    def get_last(self):
        return self.client.get(self.NAME)

    def get_series(self, by="minute", start=0, end=-1):
        return self.client.ts().range(self.slices[by][0], start, end)

    def get_range(self, *args, **kwargs):
        # Exposes the series raw range function
        # https://oss.redislabs.com/redistimeseries/commands/#filtering
        return self.client.ts().range(self.NAME, *args, **kwargs)

    def snapshot(self, rcon: Rcon):
        raise NotImplementedError

    def run_on_time(self, rcon):
        now = time.time()
        if now - self.last_run_time <= self.min_resolution_ms:
            return
        logger.debug("Taking snaphost for %s", self.NAME)
        try:
            self.snapshot(rcon)
        except:
            self.fails += 1
            if self.fails > self.max_fails:
                raise
            return
        self.last_run_time = now
        return now


class PlayerCount(Series):
    NAME = "player_count"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def snapshot(self, rcon):
        slots = rcon.get_slots()
        nb, _ = slots.split("/")

        self.client.ts().add(self.NAME, "*", float(nb))


def run():
    rcon = get_rcon()
    red = get_redis_client()
    registered_series = [PlayerCount(red)]
    for series in registered_series:
        series.migrate()

    while True:
        for series in registered_series:
            series.run_on_time(rcon)
        time.sleep(LOOP_FREQUENCY_SEC)


if __name__ == "__main__":
    run()

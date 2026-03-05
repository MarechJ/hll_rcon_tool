import logging

from rcon.cache_utils import get_redis_client

logger = logging.getLogger(__name__)

class PerformanceStatistics:
    """
    Provides a way to persist performance-related metrics over multiple service (instances).
    """
    def __init__(self, namespace: str, enabled: bool = False):
        self.red = get_redis_client()
        self.namespace = namespace
        self.enabled = enabled

    def metric_key(self, metric: str) -> str:
        return self.namespace + '::' + metric

    def increment(self, metric: str, value: int = 1):
        if not self.enabled:
            return
        self.red.incr(self.metric_key(metric), value)

    def dump(self) -> dict[str, int]:
        """
        Returns the current set of metrics collected for the configured namespace. This will also indicate the
        start of a new time-window for metrics to be collected. All already existing metrics, after calling dump,
        will be reset to 0.
        :return:
        """
        keys = self.red.keys(self.metric_key('*'), decode_responses=True)
        p = self.red.pipeline()
        for k in keys:
            p.set(k, 0, get=True)
        a = p.execute()

        res = {}
        idx = 0
        for k in keys:
            res[k.decode().replace(self.namespace + '::', '')] = int(a[idx])
            idx += 1
        return res

from datetime import datetime, timedelta
from typing import List


def is_time(times: List[datetime], interval_seconds: int):
    try:
        last_time = times[-1]
    except IndexError:
        last_time = datetime(year=1988, month=1, day=1)

    if datetime.now() - last_time < timedelta(seconds=interval_seconds):
        return False
    return True

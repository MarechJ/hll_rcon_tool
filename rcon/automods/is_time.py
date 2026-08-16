from datetime import UTC, datetime, timedelta


def is_time(times: list[datetime], interval_seconds: int):
    try:
        last_time = times[-1]
    except IndexError:
        last_time = datetime(year=1988, month=1, day=1, tzinfo=UTC)

    return not datetime.now(tz=UTC) - last_time < timedelta(seconds=interval_seconds)

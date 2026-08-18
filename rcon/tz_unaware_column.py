from datetime import datetime, timezone

from sqlalchemy import TypeDecorator, DateTime


class UTCDateTime(TypeDecorator):
    """Same as SQLAlchemy DateTime, but always stores with UTC and always reads UTC to support TZ unaware database fields."""
    impl = DateTime(timezone=False)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is not None:
            if value.tzinfo is not None:
                value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value

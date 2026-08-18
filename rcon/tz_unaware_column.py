from datetime import UTC, datetime

from sqlalchemy import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator):
    """Same as SQLAlchemy DateTime, but always stores with UTC and always reads UTC to support TZ unaware database fields."""
    impl = DateTime(timezone=False)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is not None and value.tzinfo is not None:
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        if value is not None:
            value = value.replace(tzinfo=UTC)
        return value

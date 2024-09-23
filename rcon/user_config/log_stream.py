from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class LogStreamConfigType(TypedDict):
    enabled: bool
    stream_size: int
    startup_since_mins: int
    refresh_frequency_sec: int
    refresh_since_mins: int


class LogStreamUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    stream_size: int = Field(ge=1, le=100_000, default=1000)
    startup_since_mins: int = Field(default=2)
    refresh_frequency_sec: int = Field(default=1)
    refresh_since_mins: int = Field(default=2)

    @staticmethod
    def save_to_db(values: LogStreamConfigType, dry_run=False):
        key_check(LogStreamConfigType.__required_keys__, values.keys())
        validated_conf = LogStreamUserConfig(
            enabled=values.get("enabled"),
            stream_size=values.get("stream_size"),
            startup_since_mins=values.get("startup_since_mins"),
            refresh_frequency_sec=values.get("refresh_frequency_sec"),
            refresh_since_mins=values.get("refresh_since_mins"),
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf)

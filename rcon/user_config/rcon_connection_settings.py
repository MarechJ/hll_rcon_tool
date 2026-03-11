from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class RconConnectionSettingsType(TypedDict):
    thread_pool_size: int
    performance_statistics_enabled: bool
    performance_statistics_interval_seconds: int


class RconConnectionSettingsUserConfig(BaseUserConfig):
    # TODO: max open and threadpool seem redundant
    # TODO: been made entirely redundant since RCON V2, remove
    thread_pool_size: int = Field(ge=1, le=100, default=20)
    performance_statistics_enabled: bool = Field(default=False)
    performance_statistics_interval_seconds: int = Field(default=30)

    @staticmethod
    def save_to_db(values: RconConnectionSettingsType, dry_run=False):
        key_check(
            RconConnectionSettingsType.__required_keys__,
            RconConnectionSettingsType.__optional_keys__,
            values.keys(),
        )

        validated_conf = RconConnectionSettingsUserConfig(
            thread_pool_size=values.get("thread_pool_size"),
            performance_statistics_enabled=values.get("performance_statistics_enabled"),
            performance_statistics_interval_seconds=values.get("performance_statistics_interval_seconds"),
        )

        if not dry_run:
            set_user_config(RconConnectionSettingsUserConfig.KEY(), validated_conf)

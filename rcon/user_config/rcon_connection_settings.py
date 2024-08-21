from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class RconConnectionSettingsType(TypedDict):
    thread_pool_size: int
    max_open: int
    max_idle: int


class RconConnectionSettingsUserConfig(BaseUserConfig):
    # TODO: max open and threadpool seem redundant
    thread_pool_size: int = Field(ge=1, le=100, default=20)
    max_open: int = Field(ge=1, le=100, default=20)
    max_idle: int = Field(ge=1, le=100, default=20)

    @staticmethod
    def save_to_db(values: RconConnectionSettingsType, dry_run=False):
        key_check(RconConnectionSettingsType.__required_keys__, values.keys())

        validated_conf = RconConnectionSettingsUserConfig(
            thread_pool_size=values.get("thread_pool_size"),
            max_open=values.get("max_open"),
            max_idle=values.get("max_idle"),
        )

        if not dry_run:
            set_user_config(RconConnectionSettingsUserConfig.KEY(), validated_conf)

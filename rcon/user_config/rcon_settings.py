from typing import ClassVar, TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class RconSettingsType(TypedDict):
    thread_pool_size: int
    max_open: int
    max_idle: int


class RconSettingsUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "steam_settings"

    # TODO: max open and threadpool seem redundant
    thread_pool_size: int = Field(ge=1, le=100, default=20)
    max_open: int = Field(ge=1, le=100, default=20)
    max_idle: int = Field(ge=1, le=100, default=20)

    @staticmethod
    def save_to_db(values: RconSettingsType, dry_run=False):
        key_check(RconSettingsType.__required_keys__, values.keys())

        validated_conf = RconSettingsUserConfig(
            thread_pool_size=values.get("thread_pool_size"),
            max_open=values.get("max_open"),
            max_idle=values.get("max_idle"),
        )

        if not dry_run:
            set_user_config(RconSettingsUserConfig.KEY(), validated_conf.model_dump())

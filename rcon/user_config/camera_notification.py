from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class CameraNotificationType(TypedDict):
    broadcast: bool
    welcome: bool


class CameraNotificationUserConfig(BaseUserConfig):
    broadcast: bool = Field(default=False)
    welcome: bool = Field(default=False)

    @staticmethod
    def save_to_db(values: CameraNotificationType, dry_run=False):
        key_check(CameraNotificationType.__required_keys__, values.keys())

        validated_conf = CameraNotificationUserConfig(
            broadcast=values.get("broadcast"), welcome=values.get("welcome")
        )

        if not dry_run:
            set_user_config(
                CameraNotificationUserConfig.KEY(), validated_conf.model_dump()
            )

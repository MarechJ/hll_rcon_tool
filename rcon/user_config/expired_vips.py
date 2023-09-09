from typing import ClassVar, Optional, TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class ExpiredVipsType(TypedDict):
    enabled: bool
    interval_minutes: int
    discord_webhook_url: str | None


class ExpiredVipsUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "expired_vips"

    enabled: bool = Field(default=True)
    interval_minutes: int = Field(ge=1, default=60)
    discord_webhook_url: Optional[str]

    @staticmethod
    def save_to_db(values: ExpiredVipsType, dry_run=False):
        key_check(ExpiredVipsType.__required_keys__, values.keys())

        validated_conf = ExpiredVipsUserConfig(
            enabled=values.get("enabled"),
            interval_minutes=values.get("interval_minutes"),
            discord_webhook_url=values.get("discord_webhook_url"),
        )

        if not dry_run:
            set_user_config(ExpiredVipsUserConfig.KEY(), validated_conf.model_dump())

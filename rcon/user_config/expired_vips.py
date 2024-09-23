from typing import Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class ExpiredVipsType(TypedDict):
    enabled: bool
    interval_minutes: int
    discord_webhook_url: Optional[HttpUrl]


class ExpiredVipsUserConfig(BaseUserConfig):
    enabled: bool = Field(default=True)
    interval_minutes: int = Field(ge=1, default=60)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @staticmethod
    def save_to_db(values: ExpiredVipsType, dry_run=False):
        key_check(
            ExpiredVipsType.__required_keys__,
            ExpiredVipsType.__optional_keys__,
            values.keys(),
        )

        validated_conf = ExpiredVipsUserConfig(
            enabled=values.get("enabled"),
            interval_minutes=values.get("interval_minutes"),
            discord_webhook_url=values.get("discord_webhook_url"),
        )

        if not dry_run:
            set_user_config(ExpiredVipsUserConfig.KEY(), validated_conf)

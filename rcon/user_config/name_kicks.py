import re
from typing import ClassVar, Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer, field_validator

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

KICK_REASON = "Your nickname is invalid"


class NameKickType(TypedDict):
    regular_expressions: list[str]
    kick_reason: str
    discord_webhook_url: Optional[HttpUrl]
    whitelist_flags: list[str]


class NameKickUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "name_kicks"

    regular_expressions: list[str] = Field(default_factory=list)
    kick_reason: str = Field(default=KICK_REASON)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)
    whitelist_flags: list[str] = Field(default_factory=list)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @field_validator("regular_expressions")
    @classmethod
    def compile_regexes(cls, vs):
        for idx, v in enumerate(vs):
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Error parsing regex: `{v}`: {e}")

        return vs

    @staticmethod
    def save_to_db(values: NameKickType, dry_run=False):
        key_check(NameKickType.__required_keys__, values.keys())

        validated_conf = NameKickUserConfig(
            regular_expressions=values.get("regular_expressions"),
            kick_reason=values.get("kick_reason"),
            discord_webhook_url=values.get("discord_webhook_url"),
            whitelist_flags=values.get("whitelist_flags"),
        )

        if not dry_run:
            set_user_config(NameKickUserConfig.KEY(), validated_conf.model_dump())

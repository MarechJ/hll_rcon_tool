import re
from typing import TypedDict

import pydantic

DISCORD_USER_ID_PATTERN = re.compile(r"<@\d+>")
DISCORD_ROLE_ID_PATTERN = re.compile(r"<@&\d+>")


class DynamicHookType(TypedDict):
    url: str
    user_mentions: list[dict[str, str]]
    role_mentions: list[dict[str, str]]


class DiscordUserIdFormat(pydantic.BaseModel):
    """A discord user ID format for mentions <@123456789>"""

    value: str

    @pydantic.field_validator("value")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if re.match(DISCORD_USER_ID_PATTERN, v):
            return v
        else:
            raise ValueError(f"{v} is not a valid Discord user ID ex: <@123456789>")


class DiscordRoleIdFormat(pydantic.BaseModel):
    """A discord role ID format for mentions <@&123456789>"""

    value: str

    @pydantic.field_validator("value")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if re.match(DISCORD_ROLE_ID_PATTERN, v):
            return v
        else:
            raise ValueError(f"{v} is not a valid Discord role ID ex: <@&123456789>")


class DiscordWebhook(pydantic.BaseModel):
    """A webhook URL and list of user/role IDs to mention in <@> and <@&> format"""

    user_mentions: list[DiscordUserIdFormat] = pydantic.Field(default_factory=list)
    role_mentions: list[DiscordRoleIdFormat] = pydantic.Field(default_factory=list)
    url: str


class DiscordWebhooksUserConfig(pydantic.BaseModel):
    """A list of discord webhooks for a specific hook type (camera, watchlist, etc)"""

    name: str
    hooks: list[DiscordWebhook] = pydantic.Field(default_factory=list)

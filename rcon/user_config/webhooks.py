import re
from typing import Any, ClassVar, TypedDict

import pydantic

from rcon.user_config.utils import (
    BaseUserConfig,
    InvalidConfigurationError,
    key_check,
    set_user_config,
)

DISCORD_USER_ID_PATTERN = re.compile(r"<@\d+>")
DISCORD_ROLE_ID_PATTERN = re.compile(r"<@&\d+>")


class DynamicHookType(TypedDict):
    url: str
    user_mentions: list[str]
    role_mentions: list[str]


def parse_raw_hooks(raw_hooks: list[DynamicHookType]) -> list["DiscordWebhook"]:
    if not isinstance(raw_hooks, list):
        raise InvalidConfigurationError("%s must be a list", raw_hooks)

    validated_hooks: list[DiscordWebhook] = []
    for raw_hook in raw_hooks:
        user_mentions = raw_hook["user_mentions"]
        user_ids = frozenset(user_mentions)
        role_mentions = raw_hook["role_mentions"]
        role_ids = frozenset(role_mentions)

        h = DiscordWebhook(
            url=raw_hook.get("url"), user_mentions=user_ids, role_mentions=role_ids
        )
        validated_hooks.append(h)

    return validated_hooks


# class DiscordUserIdFormat(pydantic.BaseModel):
#     """A discord user ID format for mentions <@123456789>"""

#     value: str

#     @pydantic.field_validator("value")
#     @classmethod
#     def validate_format(cls, v: str) -> str:
#         if re.match(DISCORD_USER_ID_PATTERN, v):
#             return v
#         else:
#             raise ValueError(f"{v} is not a valid Discord user ID ex: <@123456789>")


# class DiscordRoleIdFormat(pydantic.BaseModel):
#     """A discord role ID format for mentions <@&123456789>"""

#     value: str

#     @pydantic.field_validator("value")
#     @classmethod
#     def validate_format(cls, v: str) -> str:
#         if re.match(DISCORD_ROLE_ID_PATTERN, v):
#             return v
#         else:
#             raise ValueError(f"{v} is not a valid Discord role ID ex: <@&123456789>")


class DiscordWebhook(pydantic.BaseModel):
    """A webhook URL and list of user/role IDs to mention in <@> and <@&> format"""

    user_mentions: list[str] = pydantic.Field(default_factory=list)
    role_mentions: list[str] = pydantic.Field(default_factory=list)
    url: str

    @pydantic.field_validator("user_mentions")
    @classmethod
    def validate_user_formats(cls, vs: str) -> list[str]:
        user_ids = set()
        for v in vs:
            if re.match(DISCORD_USER_ID_PATTERN, v):
                user_ids.add(v)
            else:
                raise ValueError(f"{v} is not a valid Discord user ID ex: <@123456789>")
        return list(user_ids)

    @pydantic.field_validator("role_mentions")
    @classmethod
    def validate_role_formats(cls, vs: str) -> list[str]:
        role_ids = set()
        for v in vs:
            if re.match(DISCORD_ROLE_ID_PATTERN, v):
                role_ids.add(v)
            else:
                raise ValueError(
                    f"{v} is not a valid Discord role ID ex: <@&123456789>"
                )
        return list(role_ids)


class BaseWebhookUserConfig(BaseUserConfig):
    hooks: list[DiscordWebhook] = pydantic.Field(default_factory=list)

    @classmethod
    def save_to_db(cls, values: DynamicHookType, dry_run=False) -> None:
        for obj in values.get("hooks", []):
            key_check(DynamicHookType.__required_keys__, obj.keys())

        validated_hooks = parse_raw_hooks(values.get("hooks"))
        validated_conf = cls(hooks=validated_hooks)

        # pprint(validated_conf)
        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


class WatchlistWebhooksUserConfig(BaseWebhookUserConfig):
    KEY_NAME: ClassVar = "watchlist_webhooks"


class CameraWebhooksUserConfig(BaseWebhookUserConfig):
    KEY_NAME: ClassVar = "camera_webhooks"


def get_all_hook_types(
    as_dict=False, as_json=False
) -> (
    list[dict[str, Any]]
    | list[str]
    | tuple[CameraWebhooksUserConfig, WatchlistWebhooksUserConfig]
):
    cameras = CameraWebhooksUserConfig.load_from_db()
    watchlists = WatchlistWebhooksUserConfig.load_from_db()

    all_types = (cameras, watchlists)

    if as_dict:
        return [msg.model_dump() for msg in all_types]
    elif as_json:
        return [msg.model_dump_json() for msg in all_types]
    else:
        return all_types

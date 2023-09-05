import re
from typing import Any, ClassVar, TypedDict

import pydantic

from rcon.models import enter_session
from rcon.user_config.utils import (
    InvalidConfigurationError,
    get_user_config,
    set_user_config,
)
from rcon.utils import get_server_number

DISCORD_USER_ID_PATTERN = re.compile(r"<@\d+>")
DISCORD_ROLE_ID_PATTERN = re.compile(r"<@&\d+>")
EXPECTED_HOOK_TYPES = (
    "watchlist",
    "camera",
    # TODO
    # chat
    # kill
    # audit
)


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

    KEY_PREFIX: ClassVar = "discord_hooks"

    hook_type: str
    hooks: list[DiscordWebhook] = pydantic.Field(default_factory=list)

    @pydantic.field_validator("hook_type")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v not in EXPECTED_HOOK_TYPES:
            raise ValueError(
                f"{v} is not a valid hook type ({','.join(EXPECTED_HOOK_TYPES)}) "
            )

        return v

    @property
    def HOOKS_KEY(self):
        return f"{get_server_number()}_{self.KEY_PREFIX}_{self.hook_type}"

    @staticmethod
    def get_all_hook_types(
        as_dict=False, as_json=False
    ) -> list[dict[str, Any]] | list[str] | list["DiscordWebhooksUserConfig"]:
        """Load and return all hook types from the database (or defaults)"""
        hooks: list[DiscordWebhooksUserConfig] = []
        with enter_session() as sess:
            hooks = [
                DiscordWebhooksUserConfig(hook_type=hook_type).load_from_db()
                for hook_type in EXPECTED_HOOK_TYPES
            ]

        if as_dict:
            return [h.model_dump() for h in hooks]
        elif as_json:
            return [h.model_dump_json() for h in hooks]
        else:
            return hooks

    def load_from_db(self) -> "DiscordWebhooksUserConfig":
        """Load and return the hook type or default"""
        conf = get_user_config(self.HOOKS_KEY, None)
        if conf:
            return DiscordWebhooksUserConfig.model_validate(conf)

        return DiscordWebhooksUserConfig(hook_type=self.hook_type)

    def save_to_db(self, hooks: list[DynamicHookType], dry_run=False):
        """Create models from the request for validation then persist to the database

        :dry_run Validation only

        """
        if not isinstance(hooks, list):
            raise InvalidConfigurationError("%s must be a list", self.HOOKS_KEY)

        validated_hooks = []
        for raw_hook in hooks:
            user_ids: list[DiscordUserIdFormat] = []
            role_ids: list[DiscordRoleIdFormat] = []
            user_ids.extend(
                [
                    DiscordUserIdFormat(value=v.get("value"))
                    for v in raw_hook["user_mentions"]
                ]
            )
            role_ids.extend(
                [
                    DiscordRoleIdFormat(value=v.get("value"))
                    for v in raw_hook["role_mentions"]
                ]
            )

            h = DiscordWebhook(
                url=raw_hook["url"], user_mentions=user_ids, role_mentions=role_ids
            )
            validated_hooks.append(h)

        validated_conf = DiscordWebhooksUserConfig(
            hook_type=self.hook_type, hooks=validated_hooks
        )

        if not dry_run:
            set_user_config(self.HOOKS_KEY, validated_conf.model_dump())

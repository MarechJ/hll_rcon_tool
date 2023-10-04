import re
from typing import TypedDict

import pydantic

from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config

DISCORD_USER_ID_PATTERN = re.compile(r"<@\d+>")
DISCORD_ROLE_ID_PATTERN = re.compile(r"<@&\d+>")


class WebhookMentionType(TypedDict):
    url: pydantic.HttpUrl
    user_mentions: list[str]
    role_mentions: list[str]


class WebhookType(TypedDict):
    url: pydantic.HttpUrl


class RawWebhookType(TypedDict):
    hooks: list[WebhookType]


class RawWebhookMentionType(TypedDict):
    hooks: list[WebhookMentionType]


class AdminPingWebhookType(RawWebhookMentionType):
    trigger_words: list[str]


class ChatWebhookType(RawWebhookType):
    allow_mentions: bool


class KillsWebhookType(RawWebhookType):
    send_kills: bool
    send_team_kills: bool


class DiscordWebhook(pydantic.BaseModel):
    url: pydantic.HttpUrl

    @pydantic.field_serializer("url")
    def serialize_url(self, server_url: pydantic.HttpUrl, _info):
        return str(server_url)


class DiscordMentionWebhook(DiscordWebhook):
    """A webhook URL and list of user/role IDs to mention in <@> and <@&> format"""

    user_mentions: list[str] = pydantic.Field(default_factory=list)
    role_mentions: list[str] = pydantic.Field(default_factory=list)

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


class BaseMentionWebhookUserConfig(BaseUserConfig):
    hooks: list[DiscordMentionWebhook] = pydantic.Field(default_factory=list)

    @classmethod
    def save_to_db(cls, values: RawWebhookMentionType, dry_run=False) -> None:
        raw_hooks: list[WebhookMentionType] = values.get("hooks")
        _listType(values=raw_hooks)

        for obj in raw_hooks:
            key_check(WebhookMentionType.__required_keys__, obj.keys())

        validated_hooks = parse_raw_mention_hooks(raw_hooks)
        validated_conf = cls(hooks=validated_hooks)

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


class BaseWebhookUserConfig(BaseUserConfig):
    hooks: list[DiscordWebhook] = pydantic.Field(default_factory=list)

    @classmethod
    def save_to_db(cls, values: RawWebhookType, dry_run=False) -> None:
        raw_hooks: list[WebhookType] = values.get("hooks")
        _listType(values=raw_hooks)

        for obj in raw_hooks:
            key_check(WebhookType.__required_keys__, obj.keys())

        validated_hooks = [DiscordWebhook(url=obj.get("url")) for obj in raw_hooks]
        validated_conf = cls(hooks=validated_hooks)

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


class WatchlistWebhooksUserConfig(BaseMentionWebhookUserConfig):
    pass


class CameraWebhooksUserConfig(BaseMentionWebhookUserConfig):
    pass


class AdminPingWebhooksUserConfig(BaseMentionWebhookUserConfig):
    pass

    trigger_words: list[str] = pydantic.Field(default_factory=list)

    @pydantic.field_validator("trigger_words")
    @classmethod
    def ensure_case_unique(cls, vs):
        processed_words = set()
        v: str
        for v in vs:
            processed_words.add(v.lower().strip())

        return list(processed_words)

    @staticmethod
    def save_to_db(values: AdminPingWebhookType, dry_run=False) -> None:
        raw_hooks = values.get("hooks")
        _listType(values=raw_hooks)

        for obj in raw_hooks:
            key_check(WebhookMentionType.__required_keys__, obj.keys())

        validated_hooks = parse_raw_mention_hooks(raw_hooks)
        validated_conf = AdminPingWebhooksUserConfig(
            trigger_words=values.get("trigger_words"),
            hooks=validated_hooks,
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


class ChatWebhooksUserConfig(BaseWebhookUserConfig):
    allow_mentions: bool = pydantic.Field(default=False)

    @staticmethod
    def save_to_db(values: ChatWebhookType, dry_run=False) -> None:
        raw_hooks = values.get("hooks")
        _listType(values=raw_hooks)

        for obj in raw_hooks:
            key_check(WebhookType.__required_keys__, obj.keys())

        validated_hooks = [DiscordWebhook(url=obj.get("url")) for obj in raw_hooks]
        validated_conf = ChatWebhooksUserConfig(
            allow_mentions=values.get("allow_mentions"),
            hooks=validated_hooks,
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


class AuditWebhooksUserConfig(BaseWebhookUserConfig):
    pass


class KillsWebhooksUserConfig(BaseWebhookUserConfig):
    send_kills: bool = pydantic.Field(default=False)
    send_team_kills: bool = pydantic.Field(default=True)

    @staticmethod
    def save_to_db(values: KillsWebhookType, dry_run=False) -> None:
        raw_hooks = values.get("hooks")
        _listType(values=raw_hooks)

        for obj in raw_hooks:
            key_check(WebhookType.__required_keys__, obj.keys())

        validated_hooks = [DiscordWebhook(url=obj.get("url")) for obj in raw_hooks]
        validated_conf = KillsWebhooksUserConfig(
            send_kills=values.get("send_kills"),
            send_team_kills=values.get("send_team_kills"),
            hooks=validated_hooks,
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


def parse_raw_mention_hooks(
    raw_hooks: list[WebhookMentionType],
) -> list["DiscordMentionWebhook"]:
    validated_hooks: list[DiscordMentionWebhook] = []
    for raw_hook in raw_hooks:
        user_mentions = raw_hook.get("user_mentions")
        user_ids = set(user_mentions)
        role_mentions = raw_hook.get("role_mentions")
        role_ids = set(role_mentions)

        h = DiscordMentionWebhook(
            url=raw_hook.get("url"),
            user_mentions=list(user_ids),
            role_mentions=list(role_ids),
        )
        validated_hooks.append(h)

    return validated_hooks


def get_all_hook_types(as_dict=True, as_json=False):
    cameras = CameraWebhooksUserConfig.load_from_db()
    watchlists = WatchlistWebhooksUserConfig.load_from_db()
    chats = ChatWebhooksUserConfig.load_from_db()
    kills = KillsWebhooksUserConfig.load_from_db()
    audits = AuditWebhooksUserConfig.load_from_db()

    all_types = (cameras, watchlists, chats, kills, audits)

    if as_dict:
        return [{msg.__repr_name__(): msg.model_dump()} for msg in all_types]
    elif as_json:
        return [msg.model_dump_json() for msg in all_types]

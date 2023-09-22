from typing import TypedDict

from pydantic import BaseModel, Field

from rcon.typedefs import AllLogTypes
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config
from rcon.user_config.webhooks import DiscordMentionWebhook, WebhookMentionType


class LogLineWebhookType(TypedDict):
    log_type: AllLogTypes
    webhooks: list[WebhookMentionType]


class LogLineType(TypedDict):
    log_types: list[LogLineWebhookType]


class LogLineWebhook(BaseModel):
    log_type: AllLogTypes
    webhooks: list[DiscordMentionWebhook] = Field(default_factory=list)


class LogLineWebhookUserConfig(BaseUserConfig):
    log_types: list[LogLineWebhook] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: LogLineType, dry_run=False):
        key_check(LogLineType.__required_keys__, values.keys())
        raw_hooks: list[LogLineWebhookType] = values.get("log_types")
        _listType(values=raw_hooks)  # type: ignore

        validated_log_lines: list[LogLineWebhook] = []
        for raw_log_line in raw_hooks:
            key_check(LogLineWebhookType.__required_keys__, raw_log_line.keys())

            webhooks = [
                DiscordMentionWebhook(
                    url=h.get("url"),
                    user_mentions=h.get("user_mentions"),
                    role_mentions=h.get("role_mentions"),
                )
                for h in raw_log_line.get("webhooks")
            ]

            log_line = LogLineWebhook(
                log_type=raw_log_line.get("log_type"),
                webhooks=webhooks,
            )
            validated_log_lines.append(log_line)

        validated_conf = LogLineWebhookUserConfig(log_types=validated_log_lines)

        if not dry_run:
            set_user_config(LogLineWebhookUserConfig.KEY(), validated_conf.model_dump())

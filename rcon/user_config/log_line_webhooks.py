from typing import ClassVar, TypedDict

from pydantic import BaseModel, Field, field_validator

from rcon.typedefs import ALL_LOG_TYPES
from rcon.user_config.utils import (
    BaseUserConfig,
    InvalidConfigurationError,
    key_check,
    set_user_config,
)
from rcon.user_config.webhooks import DiscordMentionWebhook, WebhookMentionType


class LogLineWebhookType(TypedDict):
    log_type: str
    webhooks: list[WebhookMentionType]


class LogLineWebhook(BaseModel):
    log_type: str
    webhooks: list[DiscordMentionWebhook] = Field(default_factory=list)

    @field_validator("log_type")
    @classmethod
    def validate_log_type(cls, v):
        if v not in ALL_LOG_TYPES:
            raise ValueError(f"{v} not one of {ALL_LOG_TYPES}")

        return v


class LogLineWebhookUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "log_line_webhooks_config"

    log_types: list[LogLineWebhook] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values, dry_run=False):
        raw_hooks: list[LogLineWebhookType] = values.get("log_types")
        if not isinstance(raw_hooks, list):
            print(f"{type(values)=}")
            raise InvalidConfigurationError(f"{values} must be a list")

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

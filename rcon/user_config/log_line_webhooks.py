from typing import TypedDict

from pydantic import BaseModel, Field

from rcon.typedefs import AllLogTypes, InvalidLogTypeError
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config
from rcon.user_config.webhooks import DiscordMentionWebhook, WebhookMentionType


class LogLineWebhookType(TypedDict):
    log_types: list[AllLogTypes]
    webhook: WebhookMentionType


class LogLineType(TypedDict):
    webhooks: list[LogLineWebhookType]


class LogLineWebhook(BaseModel):
    log_types: list[AllLogTypes] = Field(default_factory=list)
    webhook: DiscordMentionWebhook


class LogLineWebhookUserConfig(BaseUserConfig):
    webhooks: list[LogLineWebhook] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: LogLineType, dry_run=False):
        key_check(LogLineType.__required_keys__, values.keys())
        raw_objects: list[LogLineWebhookType] = values.get("webhooks")
        _listType(values=raw_objects)  # type: ignore

        validated_log_lines: list[LogLineWebhook] = []
        for obj in raw_objects:
            key_check(LogLineWebhookType.__required_keys__, obj.keys())

            raw_webhook = obj.get("webhook")
            raw_log_types = obj.get("log_types")
            _listType(values=raw_log_types)  # type: ignore

            hook = DiscordMentionWebhook(
                url=raw_webhook.get("url"),
                user_mentions=raw_webhook.get("user_mentions"),
                role_mentions=raw_webhook.get("role_mentions"),
            )

            log_types: list[AllLogTypes] = []
            invalid_log_type = None
            try:
                for log_type in raw_log_types:
                    invalid_log_type = log_type
                    log_types.append(AllLogTypes(log_type))
            except ValueError:
                raise InvalidLogTypeError(invalid_log_type)  # type: ignore

            log_line = LogLineWebhook(
                log_types=raw_log_types,
                webhook=hook,
            )
            validated_log_lines.append(log_line)

        validated_conf = LogLineWebhookUserConfig(webhooks=validated_log_lines)

        if not dry_run:
            set_user_config(LogLineWebhookUserConfig.KEY(), validated_conf.model_dump())

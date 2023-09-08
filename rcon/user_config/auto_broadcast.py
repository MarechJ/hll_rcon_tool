from typing import ClassVar, Iterable, TypedDict

from pydantic import BaseModel, Field

from rcon.user_config.utils import (
    BaseUserConfig,
    InvalidConfigurationError,
    key_check,
    set_user_config,
)


class AutoBroadcastType(TypedDict):
    enabled: bool
    randomize: bool
    messages: Iterable[str]


class AutoBroadcastMessage(BaseModel):
    time_sec: int = Field(ge=1)
    message: str


class AutoBroadcastUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "auto_broadcasts"

    enabled: bool = Field(default=False, strict=True)
    randomize: bool = Field(default=False, strict=True)
    messages: list[AutoBroadcastMessage] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: AutoBroadcastType, dry_run=False):
        key_check(AutoBroadcastType.__required_keys__, values.keys())

        raw_messages = values.get("messages")
        if not isinstance(raw_messages, list):
            raise InvalidConfigurationError(f"{values} must be a list")

        validated_messages = []
        raw_message: str
        for raw_message in raw_messages:
            raw_message = raw_message.replace("\\n", "\n")

            try:
                time, message = raw_message.split(" ", 1)
            except IndexError:
                raise InvalidConfigurationError(
                    "Broacast message must be tuples (<int: seconds>, <str: message>)"
                )

            validated_messages.append(
                AutoBroadcastMessage(time_sec=int(time), message=message)
            )

        validated_conf = AutoBroadcastUserConfig(
            enabled=values.get("enabled"),
            randomize=values.get("randomize"),
            messages=validated_messages,
        )

        if not dry_run:
            set_user_config(AutoBroadcastUserConfig.KEY(), validated_conf.model_dump())

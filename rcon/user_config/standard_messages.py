from pprint import pprint
from typing import Any, ClassVar, Iterable, TypedDict

import pydantic

from rcon.user_config.utils import (
    BaseUserConfig,
    InvalidConfigurationError,
    key_check,
    set_user_config,
)


class StandardMessageType(TypedDict):
    messages: list[str]


class BaseStandardMessageUserConfig(BaseUserConfig):
    messages: list[str] = pydantic.Field(default_factory=list)

    @classmethod
    def KEY(cls) -> str:
        return f"{cls.KEY_NAME}"

    @classmethod
    def save_to_db(cls, values, dry_run=False):
        pprint(values)
        key_check(StandardMessageType.__required_keys__, values.keys())
        messages: list[str] = values.get("messages")
        if not isinstance(messages, list):
            raise InvalidConfigurationError(f"{messages} must be a list")

        validated_conf = cls(messages=messages)

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf.model_dump())


class StandardWelcomeMessagesUserConfig(BaseStandardMessageUserConfig):
    KEY_NAME: ClassVar = "standard_messages_welcome"


class StandardBroadcastMessagesUserConfig(BaseStandardMessageUserConfig):
    KEY_NAME: ClassVar = "standard_messages_broadcasts"


class StandardPunishmentMessagesUserConfig(BaseStandardMessageUserConfig):
    KEY_NAME: ClassVar = "standard_messages_punishments"


def get_all_message_keys() -> Iterable[str]:
    return (
        StandardWelcomeMessagesUserConfig.KEY_NAME,
        StandardBroadcastMessagesUserConfig.KEY_NAME,
        StandardPunishmentMessagesUserConfig.KEY_NAME,
    )


def get_all_message_types(
    as_dict=False, as_json=False
) -> (
    list[dict[str, Any]]
    | list[str]
    | tuple[
        StandardWelcomeMessagesUserConfig,
        StandardBroadcastMessagesUserConfig,
        StandardPunishmentMessagesUserConfig,
    ]
):
    welcomes = StandardWelcomeMessagesUserConfig.load_from_db()
    broadcasts = StandardBroadcastMessagesUserConfig.load_from_db()
    punishments = StandardPunishmentMessagesUserConfig.load_from_db()

    all_types = (welcomes, broadcasts, punishments)

    if as_dict:
        return [msg.model_dump() for msg in all_types]
    elif as_json:
        return [msg.model_dump_json() for msg in all_types]
    else:
        return all_types

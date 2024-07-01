import json
from typing import Any, TypedDict

import pydantic
from pydantic import Field

from rcon.user_config.auto_broadcast import (
    AutoBroadcastMessage,
    AutoBroadcastMessageType,
    RawAutoBroadCastMessage,
)
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config


class StandardMessageType(TypedDict):
    messages: list[str]


class StandardBroadcastMessagesType(TypedDict):
    messages: list[AutoBroadcastMessageType]


class BaseStandardMessageUserConfig(BaseUserConfig):
    messages: list[str] = pydantic.Field(default_factory=list)

    @classmethod
    def save_to_db(cls, values, dry_run=False):
        key_check(StandardMessageType.__required_keys__, values.keys())
        messages: list[str] = values.get("messages")
        _listType(values=messages)  # type: ignore

        validated_conf = cls(messages=messages)

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf)


class StandardWelcomeMessagesUserConfig(BaseStandardMessageUserConfig):
    pass


class StandardPunishmentMessagesUserConfig(BaseStandardMessageUserConfig):
    pass


class StandardBroadcastMessagesUserConfig(BaseUserConfig):
    messages: list[AutoBroadcastMessage] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: StandardBroadcastMessagesType, dry_run=False):
        key_check(StandardBroadcastMessagesType.__required_keys__, values.keys())

        raw_messages = values.get("messages")
        _listType(values=raw_messages)  # type: ignore

        validated_messages = []
        raw_message: str | AutoBroadcastMessageType
        for raw_message in raw_messages:
            # TODO: Fix this bandaid once the UI gets overhauled
            # Accept dict like objects when not set through the UI
            if isinstance(raw_message, dict):
                time = raw_message["time_sec"]
                message = raw_message["message"]
            # The UI passes these in as strings
            else:
                raw_message = raw_message.replace("\\n", "\n")
                time, message = RawAutoBroadCastMessage(
                    value=raw_message
                ).time_and_message
            validated_messages.append(
                AutoBroadcastMessage(time_sec=int(time), message=message)
            )

        validated_conf = StandardBroadcastMessagesUserConfig(
            messages=validated_messages,
        )

        if not dry_run:
            set_user_config(StandardBroadcastMessagesUserConfig.KEY(), validated_conf)


def get_all_message_types(
    as_dict=False, as_json=False
) -> (
    dict[str, dict[str, Any]]
    | str
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
        return {msg.__repr_name__(): msg.model_dump() for msg in all_types}
    elif as_json:
        return json.dumps({msg.__repr_name__(): msg.model_dump() for msg in all_types})
    else:
        return all_types

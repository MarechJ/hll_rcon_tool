import json
from typing import Any, TypedDict

import pydantic

from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config


class StandardMessageType(TypedDict):
    messages: list[str]


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


class StandardBroadcastMessagesUserConfig(BaseStandardMessageUserConfig):
    pass


class StandardPunishmentMessagesUserConfig(BaseStandardMessageUserConfig):
    pass


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

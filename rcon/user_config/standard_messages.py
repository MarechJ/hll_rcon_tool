import json
import os
from logging import getLogger
from typing import Any, TypedDict

logger = getLogger(__name__)
from typing import Self

import pydantic
from pydantic import Field

from rcon.user_config.auto_broadcast import (
    AutoBroadcastMessage,
    AutoBroadcastMessageType,
    RawAutoBroadCastMessage,
)
from rcon.user_config.utils import (
    BaseUserConfig,
    _listType,
    get_user_config,
    key_check,
    set_user_config,
)


class StandardMessageType(TypedDict):
    messages: list[str]


class StandardBroadcastMessagesType(TypedDict):
    messages: list[AutoBroadcastMessageType]


class BaseStandardMessageUserConfig(BaseUserConfig):
    messages: list[str] = pydantic.Field(default_factory=list)

    @classmethod
    def save_to_db(cls, values, dry_run=False):
        key_check(
            StandardMessageType.__required_keys__,
            StandardMessageType.__optional_keys__,
            values.keys(),
        )
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

    @classmethod
    def load_from_db(cls, default_on_validation_error: bool = True) -> Self:
        # This is a bandaid that allows us to port old style broadcasts which were
        # a list of strings in the format `time message`

        # This should never happen in production, but allows tests to run
        if not os.getenv("HLL_DB_URL"):
            logger.warning(f"HLL_DB_URL not set, returning a default instance")
            return cls()

        # If the cache is unavailable, it will fall back to creating a default
        # model instance, but will not persist it to the database and overwrite settings
        conf = get_user_config(cls.KEY(), default=None)
        if conf is not None:
            try:
                # This is the only difference between this and BaseUserConfig.load_from_db
                validated_messages: list[AutoBroadcastMessage] = []
                if (
                    "messages" in conf
                    and conf["messages"]
                    and isinstance(conf["messages"][-1], str)
                ):
                    for raw_message in conf["messages"]:
                        time, text = raw_message.split(maxsplit=1)
                        validated_messages.append(
                            AutoBroadcastMessage(time_sec=int(time), message=text)
                        )

                    config = StandardBroadcastMessagesUserConfig(
                        messages=validated_messages
                    )
                    StandardBroadcastMessagesUserConfig.save_to_db(
                        values=config.model_dump()
                    )
                    return config
                else:
                    return cls.model_validate(conf)
            except pydantic.ValidationError as e:
                if default_on_validation_error:
                    logger.error(
                        f"Error loading {cls.KEY()}, returning defaults, validation errors:"
                    )
                    logger.error(e)
                    return cls()
                else:
                    raise
        else:
            # This shouldn't happen because we seed the database on startup if the
            # records don't exist, if someone has manually edited their database that
            # is on them, previously we would not seed defaults and create/persist an
            # instance if `get_user_config` did not find a record for any reason.
            # This was resetting peoples legitimate configs in some scenarios, particularly
            # when containers were being created/torn down and a service or the backend queried
            # a model and postgres was unavailable.
            # Now models are only persisted to the database when they're either explicitly seeded
            # during backend startup, or if the `save_to_db` method is explicitly called, for
            # instance through the API, or CLI
            logger.error(f"{cls.KEY()} not found, returning defaults")

        return cls()

    @staticmethod
    def save_to_db(values: StandardBroadcastMessagesType, dry_run=False):
        key_check(
            StandardBroadcastMessagesType.__required_keys__,
            StandardBroadcastMessagesType.__optional_keys__,
            values.keys(),
        )

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


def get_all_message_types(as_dict=False, as_json=False) -> (
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

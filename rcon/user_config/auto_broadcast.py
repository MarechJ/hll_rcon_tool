import re
from typing import ClassVar, Iterable, TypedDict

from pydantic import BaseModel, Field, field_validator

from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config


class AutoBroadcastType(TypedDict):
    enabled: bool
    randomize: bool
    messages: Iterable[str]


class AutoBroadcastMessageType(TypedDict):
    time_sec: int
    message: str


class AutoBroadcastMessage(BaseModel):
    time_sec: int = Field(ge=1)
    message: str


class RawAutoBroadCastMessage(BaseModel):
    pattern: ClassVar = re.compile(r"(\d+) (.+)")
    value: str

    @staticmethod
    def split(value):
        return value.split(" ", 1)

    @property
    def time_and_message(self):
        time, message = self.split(self.value)
        return time, message

    @field_validator("value")
    @classmethod
    def validiate_time_and_message(cls, v):
        if match := re.match(cls.pattern, v):
            time, message = match.groups()
            return v
        else:
            raise ValueError(
                "Broacast message must be tuples (<int: seconds>, <str: message>)"
            )


class AutoBroadcastUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False, strict=True, title="Enable", description="Enable auto broadcasts")
    randomize: bool = Field(default=False, strict=True, title="Randomize messages", description="Set broadcasts in random order")
    messages: list[AutoBroadcastMessage] = Field(default_factory=list, title="Messages", description="A list of dicts with `time_sec` (length in seconds the broadcast is set for) and `message` (the broadcast message) keys")

    @staticmethod
    def save_to_db(values: AutoBroadcastType, dry_run=False):
        key_check(
            AutoBroadcastType.__required_keys__,
            AutoBroadcastType.__optional_keys__,
            values.keys(),
        )

        raw_messages = values.get("messages")
        _listType(values=raw_messages)  # type: ignore

        validated_messages = []
        raw_message: str
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

        validated_conf = AutoBroadcastUserConfig(
            enabled=values.get("enabled"),
            randomize=values.get("randomize"),
            messages=validated_messages,
        )

        if not dry_run:
            set_user_config(AutoBroadcastUserConfig.KEY(), validated_conf)

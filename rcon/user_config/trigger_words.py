from typing import TypedDict
import enum
from pydantic import Field, BaseModel, field_validator
import re
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config, _listType


# Have to inherit from str to allow for JSON serialization w/ pydantic
class MessageVariables(str, enum.Enum):
    vip_status = "vip_status"
    vip_expiration = "vip_expiration"
    # TODO: define all the other variables people can use in a message


class TriggerWordType(TypedDict):
    words: list[str]
    message: str


class TriggerWordsType(TypedDict):
    enabled: bool
    trigger_words: list[TriggerWordType]


class TriggerWord(BaseModel):
    words: list[str] = Field(default_factory=list)
    message: str = Field(default="")

    @field_validator("message")
    @classmethod
    def only_valid_variables(cls, v: str) -> str:
        bracket_re = re.compile(r"\{(.*?)\}")
        if match := re.match(bracket_re, v):
            for var in match.groups():
                MessageVariables(var)

        return v


class TriggerWordsUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    trigger_words: list[TriggerWord] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: TriggerWordsType, dry_run=False) -> None:
        key_check(TriggerWordsType.__required_keys__, values.keys())

        raw_trigger_words = values.get("trigger_words")
        _listType(values=raw_trigger_words)

        for obj in raw_trigger_words:
            key_check(TriggerWordType.__required_keys__, obj.keys())

        validated_words = []
        for raw_word in raw_trigger_words:
            words = raw_word.get("words")
            message = raw_word.get("message")
            validated_words.append(TriggerWord(words=words, message=message))

        validated_conf = TriggerWordsUserConfig(
            enabled=values.get("enabled"), trigger_words=validated_words
        )

        if not dry_run:
            set_user_config(TriggerWordsUserConfig.KEY(), validated_conf.model_dump())

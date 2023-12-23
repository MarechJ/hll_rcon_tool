import enum
import re
from typing import TypedDict

from pydantic import BaseModel, Field, field_validator

from rcon.types import MessageVariable, MessageVariableContext
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config

MESSAGE_VAR_RE = re.compile(r"\{(.*?)\}")
CHAT_WORDS_RE = re.compile(r"([^a-zA-Z!@])")


class TriggerWordType(TypedDict):
    words: list[str]
    message: str
    description: str


class TriggerWordsType(TypedDict):
    enabled: bool
    trigger_words: list[TriggerWordType]
    describe_words: list[str]


class TriggerWord(BaseModel):
    words: list[str] = Field(default_factory=list)
    message: str = Field(default="")
    description: str | None = Field(default=None)

    @field_validator("message")
    @classmethod
    def only_valid_variables(cls, v: str) -> str:
        match = re.match(MESSAGE_VAR_RE, v)
        if match := re.match(MESSAGE_VAR_RE, v):
            for var in match.groups():
                # Has to either be a valid MessageVariable or MessageVariableContext
                try:
                    MessageVariable(var)
                except ValueError:
                    MessageVariableContext(var)

        return v


class TriggerWordsUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    trigger_words: list[TriggerWord] = Field(default_factory=list)
    describe_words: list[str] = Field(default_factory=list)

    def describe_trigger_words(self) -> list[str]:
        return [
            f"{', '.join(word.words)} | {word.description}"
            for word in self.trigger_words
            if word.description
        ]

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
            description = raw_word.get("description")
            validated_words.append(
                TriggerWord(words=words, message=message, description=description)
            )

        validated_conf = TriggerWordsUserConfig(
            enabled=values.get("enabled"),
            trigger_words=validated_words,
            describe_words=values.get("describe_words"),
        )

        if not dry_run:
            set_user_config(TriggerWordsUserConfig.KEY(), validated_conf.model_dump())

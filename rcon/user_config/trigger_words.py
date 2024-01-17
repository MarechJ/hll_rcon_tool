import enum
import re
from functools import cached_property
from typing import Iterable, TypedDict

from pydantic import BaseModel, Field, field_validator

from rcon.types import MessageVariable, MessageVariableContext
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config

MESSAGE_VAR_RE = re.compile(r"\{(.*?)\}")
VALID_COMMAND_PREFIXES = ("!", "@")
HELP_PREFIX = "?"


def contains_triggering_word(
    chat_words: set[str], trigger_words: Iterable[str], help_words: Iterable[str]
) -> str | None:
    # Force deterministic results if a user puts two command words in the same chat message
    for word in sorted(chat_words):
        if word in trigger_words or word in help_words:
            return word

    return None


def is_command_word(
    word: str, prefixes: Iterable[str] = VALID_COMMAND_PREFIXES
) -> bool:
    return any(word.startswith(prefix) for prefix in prefixes)


def is_help_word(word: str, prefix: str = HELP_PREFIX) -> bool:
    return word.startswith(prefix)


def is_description_word(words: Iterable[str], description_words: Iterable[str]):
    return any(word in description_words for word in words)


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

    @cached_property
    def help_words(self) -> set[str]:
        return set(f"?{word[1:]}" for word in self.words)

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

    @field_validator("words")
    @classmethod
    def only_valid_command_prefixes(cls, vs: list[str]) -> list[str]:
        for word in vs:
            if word[0] not in VALID_COMMAND_PREFIXES:
                raise ValueError(
                    f"'{word}' command word must start with one of: {VALID_COMMAND_PREFIXES}"
                )

        return vs


class TriggerWordsUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    trigger_words: list[TriggerWord] = Field(default_factory=list)

    # Thes will trigger an automatic help command if `description`s are set on
    # `trigger_words`
    describe_words: list[str] = Field(default_factory=list)

    @field_validator("describe_words")
    @classmethod
    def only_valid_command_prefixes(cls, vs: list[str]) -> list[str]:
        for word in vs:
            if word[0] not in VALID_COMMAND_PREFIXES:
                raise ValueError(
                    f"'{word}' description command word must start with one of: {VALID_COMMAND_PREFIXES}"
                )

        return vs

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

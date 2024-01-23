import re
from functools import cached_property
from typing import Iterable, TypedDict

from pydantic import BaseModel, Field, field_validator

from rcon.types import MessageVariable, MessageVariableContext
from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config

MESSAGE_VAR_RE = re.compile(r"\{(.*?)\}")
VALID_COMMAND_PREFIXES = ("!", "@")
HELP_PREFIX = "?"


def chat_contains_command_word(
    chat_words: Iterable[str], command_words: Iterable[str], help_words: Iterable[str]
) -> str | None:
    # Force deterministic results if a user puts two command words in the same chat message
    for word in sorted(chat_words):
        if word in command_words or word in help_words:
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


class ChatCommandType(TypedDict):
    words: list[str]
    message: str
    description: str


class ChatCommandsType(TypedDict):
    enabled: bool
    command_words: list[ChatCommandType]
    describe_words: list[str]


class ChatCommand(BaseModel):
    words: list[str] = Field(default_factory=list)
    message: str = Field(default="")
    description: str | None = Field(default=None)

    @cached_property
    def help_words(self) -> set[str]:
        return set(f"?{word[1:]}" for word in self.words)

    @field_validator("message")
    @classmethod
    def only_valid_variables(cls, v: str) -> str:
        for match in re.findall(MESSAGE_VAR_RE, v):
            # Has to either be a valid MessageVariable or MessageVariableContext
            try:
                MessageVariable[match]
            except KeyError:
                try:
                    MessageVariableContext[match]
                except KeyError:
                    raise ValueError(f"{match} is not a valid message variable")

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


class ChatCommandsUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    command_words: list[ChatCommand] = Field(default_factory=list)

    # Thes will trigger an automatic help command if `description`s are set on
    # `command_words`
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

    def describe_chat_commands(self) -> list[str]:
        return [
            f"{', '.join(word.words)} | {word.description}"
            for word in self.command_words
            if word.description
        ]

    @staticmethod
    def save_to_db(values: ChatCommandsType, dry_run=False) -> None:
        key_check(ChatCommandsType.__required_keys__, values.keys())

        raw_command_words = values.get("command_words")
        _listType(values=raw_command_words)

        for obj in raw_command_words:
            key_check(ChatCommandType.__required_keys__, obj.keys())

        validated_words = []
        for raw_word in raw_command_words:
            words = raw_word.get("words")
            message = raw_word.get("message")
            description = raw_word.get("description")
            validated_words.append(
                ChatCommand(words=words, message=message, description=description)
            )

        validated_conf = ChatCommandsUserConfig(
            enabled=values.get("enabled"),
            command_words=validated_words,
            describe_words=values.get("describe_words"),
        )

        if not dry_run:
            set_user_config(ChatCommandsUserConfig.KEY(), validated_conf.model_dump())

import logging
import typing
from functools import cached_property

import pytz
from pydantic import Field, field_validator
from sqlalchemy.orm import Session

from rcon.conditions import Condition, create_condition
from rcon.models import PlayerID
from rcon.rcon import Rcon, get_rcon
from rcon.user_config.chat_commands import (
    BaseChatCommand,
    BaseChatCommandType,
    BaseChatCommandUserConfig,
)
from rcon.user_config.utils import _listType, _set_default, key_check, set_user_config

logger = logging.getLogger(__name__)


class RConChatCommandType(BaseChatCommandType):
    commands: dict[str, dict]
    conditions: dict[str, typing.Any]
    enabled: typing.NotRequired[bool]


class RConChatCommandsType(typing.TypedDict):
    enabled: bool
    command_words: list[RConChatCommandType]
    describe_words: list[str]


class RConChatCommand(BaseChatCommand):
    commands: dict[str, dict] | None = Field(default=None)
    enabled: bool = Field(default=True)
    conditions: dict[str, typing.Any] | None = Field(default=None)

    @cached_property
    def help_words(self) -> set[str]:
        return set(f"?{word[1:]}" for word in self.words)

    @field_validator("commands")
    @classmethod
    def only_valid_commands(cls, vs: dict[str, dict] | None) -> dict[str, dict] | None:
        if vs is None:
            return vs
        for name in vs:
            try:
                get_rcon().__getattribute__(name)
            except AttributeError:
                raise ValueError(f"'{name}' is not a valid RCon command.")
        return vs

    def conditions_fulfilled(
        self, rcon: Rcon, p: PlayerID, ctx: dict[str, str]
    ) -> bool:
        """
        Checks if the provided context meets the conditions defined in this command, if any.
        :param rcon: An instance of RCon to talk to the HLL server where the command was issued on
        :param p: The player who executed the command
        :param ctx: A dictionary of keys from MessageVariableContext, with their respective values.
        :return: True if the context meets all conditions, False otherwise
        """
        if self.conditions is None:
            return True
        conditions: list[Condition] = []
        for condition in self.conditions:
            params = self.conditions[condition]
            try:
                conditions.append(create_condition(condition, **params))
            except ValueError:
                logger.exception(
                    "Invalid condition %s %s, ignoring...", condition, params
                )
            except pytz.UnknownTimeZoneError:
                logger.exception(
                    "Invalid timezone for condition %s %s, ignoring...",
                    condition,
                    params,
                )
        return all(
            [
                c.is_valid(rcon=rcon, player_id=p, message_context=ctx)
                for c in conditions
            ]
        )


class RConChatCommandsUserConfig(BaseChatCommandUserConfig):
    command_words: list[RConChatCommand] = Field(
        default=[
            RConChatCommand(
                words=["!switch", "@switch"],
                enabled=False,
                description="Switch yourself in side",
                conditions={
                    "player_flag": {"flags": ["👍"]},
                    "player_count": {"max": 49, "min": 0},
                },
                commands={"switch_player_now": {"player_name": "{player_name}"}},
            ),
            RConChatCommand(
                words=["!admin"],
                enabled=False,
                conditions={"player_id": {"player_ids": ["765611...", "765612..."]}},
                description="Add yourself to admin cam list",
                commands={
                    "add_admin": {
                        "role": "junior",
                        "player_id": "{player_id}",
                        "description": "{player_name}",
                    }
                },
            ),
            RConChatCommand(
                words=["!redeploy"],
                enabled=False,
                conditions={"player_count": {"max": 49, "min": 0}},
                description="Punishes yourself to redeploy in 10s instead of 20s.",
                commands={
                    "punish": {
                        "player_name": "{player_name}",
                        "reason": "Executing redeploy command",
                    }
                },
            ),
        ]
    )

    @staticmethod
    def save_to_db(values: RConChatCommandsType, dry_run=False) -> None:
        key_check(
            RConChatCommandsType.__required_keys__,
            RConChatCommandsType.__optional_keys__,
            values.keys(),
        )

        raw_command_words = values.get("command_words")
        _listType(values=raw_command_words)

        for obj in raw_command_words:
            key_check(
                RConChatCommandType.__required_keys__,
                RConChatCommandType.__optional_keys__,
                obj.keys(),
            )

        validated_words = []
        for raw_word in raw_command_words:
            words = raw_word.get("words")
            commands = raw_word.get("commands")
            conditions = raw_word.get("conditions")
            description = raw_word.get("description")
            enabled = raw_word.get("enabled")
            validated_words.append(
                RConChatCommandType(
                    words=words,
                    commands=commands,
                    description=description,
                    enabled=enabled,
                    conditions=conditions,
                )
            )

        validated_conf = RConChatCommandsUserConfig(
            enabled=values.get("enabled"),
            command_words=validated_words,
            describe_words=values.get("describe_words"),
        )

        if not dry_run:
            set_user_config(RConChatCommandsUserConfig.KEY(), validated_conf)

from typing import ClassVar, Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer

from rcon.typedefs import Roles
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

WARNING_MESSAGE = "Warning, {player_name}! Your squad ({squad_name}) does not have an officer. Players of squads without an officer will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\nNext check will happen automatically in {next_check_seconds}s."
PUNISH_MESSAGE = "Your squad ({squad_name}) must have an officer.\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\nNext check in {next_check_seconds} seconds"
KICK_MESSAGE = "Your Squad ({squad_name}) must have an officer.\nYour grace period of {kick_grace_period}s has passed.\nYou failed to comply with the previous warnings."


WHITESPACE_NAMES_MESSAGE = "Your name contains a whitespace at the end (because it is truncated as it is too long). Because of a bug in the game, you might suffer auto-moderation actions as a false-positive. Please change your name and restart your game to avoid this."


class AutoModNoLeaderType(TypedDict):
    enabled: bool
    dry_run: bool
    discord_webhook_url: Optional[HttpUrl]

    number_of_notes: int
    notes_interval_seconds: int

    whitespace_message: str

    number_of_warnings: int
    warning_message: str
    warning_interval_seconds: int

    number_of_punishments: int
    punish_message: str
    punish_interval_seconds: int
    min_squad_players_for_punish: int
    min_server_players_for_punish: int

    kick_after_max_punish: bool
    min_squad_players_for_kick: int
    min_server_players_for_kick: int
    kick_grace_period_seconds: int
    kick_message: str

    immune_roles: list[Roles]
    immune_player_level: int


class AutoModNoLeaderUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "auto_mod_level_no_leader_config"

    enabled: bool = Field(default=False)
    dry_run: bool = Field(default=True)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)

    number_of_notes: int = Field(ge=0, default=1)
    notes_interval_seconds: int = Field(ge=1, default=10)

    whitespace_message: str = Field(default=WHITESPACE_NAMES_MESSAGE)

    number_of_warnings: int = Field(ge=-1, default=2)
    warning_message: str = Field(default=WARNING_MESSAGE)
    warning_interval_seconds: int = Field(ge=0, default=60)

    number_of_punishments: int = Field(ge=0, default=2)
    punish_message: str = Field(default=PUNISH_MESSAGE)
    punish_interval_seconds: int = Field(ge=0, default=40)
    min_squad_players_for_punish: int = Field(ge=0, default=3)
    min_server_players_for_punish: int = Field(ge=0, le=100, default=40)

    kick_after_max_punish: bool = Field(default=True)
    min_squad_players_for_kick: int = Field(ge=0, default=7)
    min_server_players_for_kick: int = Field(ge=0, le=100, default=6)
    kick_grace_period_seconds: int = Field(ge=0, default=120)
    kick_message: str = Field(default=KICK_MESSAGE)

    immune_roles: list[Roles] = Field(default_factory=list)
    immune_player_level: int = Field(ge=0, le=500, default=15)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @staticmethod
    def save_to_db(values: AutoModNoLeaderType, dry_run=False):
        key_check(AutoModNoLeaderType.__required_keys__, values.keys())

        validated_immune_roles: list[Roles] = []
        for raw_role in values.get("immune_roles"):
            validated_immune_roles.append(Roles(raw_role))

        validated_conf = AutoModNoLeaderUserConfig(
            enabled=values.get("enabled"),
            dry_run=values.get("dry_run"),
            discord_webhook_url=values.get("discord_webhook_url"),
            number_of_notes=values.get("number_of_notes"),
            notes_interval_seconds=values.get("notes_interval_seconds"),
            whitespace_message=values.get("whitespace_message"),
            number_of_warnings=values.get("number_of_warnings"),
            warning_message=values.get("warning_message"),
            warning_interval_seconds=values.get("warning_interval_seconds"),
            number_of_punishments=values.get("number_of_punishments"),
            punish_message=values.get("punish_message"),
            punish_interval_seconds=values.get("punish_interval_seconds"),
            min_squad_players_for_punish=values.get("min_squad_players_for_punish"),
            min_server_players_for_punish=values.get("min_server_players_for_punish"),
            kick_after_max_punish=values.get("kick_after_max_punish"),
            min_squad_players_for_kick=values.get("min_squad_players_for_kick"),
            min_server_players_for_kick=values.get("min_server_players_for_kick"),
            kick_grace_period_seconds=values.get("kick_grace_period_seconds"),
            kick_message=values.get("kick_message"),
            immune_roles=validated_immune_roles,
            immune_player_level=values.get("immune_player_level"),
        )

        if not dry_run:
            set_user_config(
                AutoModNoLeaderUserConfig.KEY(), validated_conf.model_dump()
            )

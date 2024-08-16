from typing import Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer, field_validator

from rcon.types import Roles
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


WARNING_MESSAGE = "Warning, {player_name}! Your squad ({squad_name}) does not have an officer. Players of squads without an officer will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\nNext check will happen automatically in {next_check_seconds}s."
PUNISH_MESSAGE = "Your squad ({squad_name}) must have an officer.\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\nNext check in {next_check_seconds} seconds"
KICK_MESSAGE = "Your Squad ({squad_name}) must have an officer.\nYour grace period of {kick_grace_period}s has passed.\nYou failed to comply with the previous warnings."


class AutoModNoLeaderType(TypedDict):
    enabled: bool
    dry_run: bool
    discord_webhook_url: Optional[HttpUrl]

    whitelist_flags: list[str]
    immune_roles: list[Roles]
    immune_player_level: int
    dont_do_anything_below_this_number_of_players: int

    number_of_notes: int
    notes_interval_seconds: int

    number_of_warnings: int
    warning_interval_seconds: int
    warning_message: str

    number_of_punishments: int
    min_squad_players_for_punish: int
    min_server_players_for_punish: int
    punish_interval_seconds: int
    punish_message: str

    kick_after_max_punish: bool
    min_squad_players_for_kick: int
    min_server_players_for_kick: int
    kick_grace_period_seconds: int
    kick_message: str


class AutoModNoLeaderUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    dry_run: bool = Field(default=False)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)

    whitelist_flags: list[str] = Field(default_factory=list)
    immune_roles: list[Roles] = Field(default_factory=list)
    immune_player_level: int = Field(ge=0, le=500, default=0)
    dont_do_anything_below_this_number_of_players: int = Field(ge=0, le=100, default=0)

    number_of_notes: int = Field(ge=0, default=1)
    notes_interval_seconds: int = Field(ge=1, default=10)

    number_of_warnings: int = Field(ge=-1, default=2)
    warning_interval_seconds: int = Field(ge=0, default=60)
    warning_message: str = Field(default=WARNING_MESSAGE)

    number_of_punishments: int = Field(ge=-1, default=2)
    min_squad_players_for_punish: int = Field(ge=0, le=6, default=0)
    min_server_players_for_punish: int = Field(ge=0, le=100, default=0)
    punish_interval_seconds: int = Field(ge=0, default=60)
    punish_message: str = Field(default=PUNISH_MESSAGE)

    kick_after_max_punish: bool = Field(default=True)
    min_squad_players_for_kick: int = Field(ge=0, le=6, default=0)
    min_server_players_for_kick: int = Field(ge=0, le=100, default=0)
    kick_grace_period_seconds: int = Field(ge=0, default=60)
    kick_message: str = Field(default=KICK_MESSAGE)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @field_validator("immune_roles")
    @classmethod
    def validate_roles(cls, vs):
        validated_immune_roles: list[Roles] = []
        for raw_role in vs:
            validated_immune_roles.append(Roles(raw_role))

        return validated_immune_roles

    @staticmethod
    def save_to_db(values: AutoModNoLeaderType, dry_run=False):
        key_check(AutoModNoLeaderType.__required_keys__, values.keys())

        validated_conf = AutoModNoLeaderUserConfig(
            enabled=values.get("enabled"),
            dry_run=values.get("dry_run"),
            discord_webhook_url=values.get("discord_webhook_url"),

            whitelist_flags=values.get("whitelist_flags"),
            immune_roles=values.get("immune_roles"),
            immune_player_level=values.get("immune_player_level"),
            dont_do_anything_below_this_number_of_players=values.get(
                "dont_do_anything_below_this_number_of_players"
            ),

            number_of_notes=values.get("number_of_notes"),
            notes_interval_seconds=values.get("notes_interval_seconds"),

            number_of_warnings=values.get("number_of_warnings"),
            warning_interval_seconds=values.get("warning_interval_seconds"),
            warning_message=values.get("warning_message"),

            number_of_punishments=values.get("number_of_punishments"),
            min_squad_players_for_punish=values.get("min_squad_players_for_punish"),
            min_server_players_for_punish=values.get("min_server_players_for_punish"),
            punish_interval_seconds=values.get("punish_interval_seconds"),
            punish_message=values.get("punish_message"),

            kick_after_max_punish=values.get("kick_after_max_punish"),
            min_squad_players_for_kick=values.get("min_squad_players_for_kick"),
            min_server_players_for_kick=values.get("min_server_players_for_kick"),
            kick_grace_period_seconds=values.get("kick_grace_period_seconds"),
            kick_message=values.get("kick_message"),
        )

        if not dry_run:
            set_user_config(AutoModNoLeaderUserConfig.KEY(), validated_conf)

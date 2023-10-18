from typing import Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

WARNING_MESSAGE = """Warning, {player_name} !

You can't play solo tank on this server !

You will be punished after {max_warnings} warnings
(you already received {received_warnings})

Next check will happen automatically in {next_check_seconds}s."""
PUNISH_MESSAGE = """You violated solo tank rule on this server.
You're being punished by a bot ({received_punishes}/{max_punishes}).
Next check in {next_check_seconds}s."""
KICK_MESSAGE = """You violated solo tank rule on this server.
Your grace period of {kick_grace_period}s has passed.
You failed to comply with the previous warnings."""


class AutoModNoSoloTankType(TypedDict):
    enabled: bool
    dry_run: bool
    discord_webhook_url: Optional[HttpUrl]

    whitelist_flags: list[str]
    number_of_notes: int
    notes_interval_seconds: int

    number_of_warnings: int
    warning_message: str
    warning_interval_seconds: int

    number_of_punishments: int
    punish_message: str
    punish_interval_seconds: int
    min_server_players_for_punish: int

    kick_after_max_punish: bool
    min_server_players_for_kick: int
    kick_grace_period_seconds: int
    kick_message: str


class AutoModNoSoloTankUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    dry_run: bool = Field(default=True)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)

    whitelist_flags: list[str] = Field(default_factory=list)

    number_of_notes: int = Field(ge=0, default=1)
    notes_interval_seconds: int = Field(ge=1, default=10)

    number_of_warnings: int = Field(ge=-1, default=2)
    warning_message: str = Field(default=WARNING_MESSAGE)
    warning_interval_seconds: int = Field(ge=0, default=60)

    number_of_punishments: int = Field(ge=0, default=2)
    punish_message: str = Field(default=PUNISH_MESSAGE)
    punish_interval_seconds: int = Field(ge=0, default=40)
    min_server_players_for_punish: int = Field(ge=0, le=100, default=40)

    kick_after_max_punish: bool = Field(default=True)
    min_server_players_for_kick: int = Field(ge=0, le=100, default=6)
    kick_grace_period_seconds: int = Field(ge=0, default=120)
    kick_message: str = Field(default=KICK_MESSAGE)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @staticmethod
    def save_to_db(values: AutoModNoSoloTankType, dry_run=False) -> None:
        key_check(AutoModNoSoloTankType.__required_keys__, values.keys())

        validated_conf = AutoModNoSoloTankUserConfig(
            enabled=values.get("enabled"),
            dry_run=values.get("dry_run"),
            discord_webhook_url=values.get("discord_webhook_url"),
            whitelist_flags=values.get("whitelist_flags"),
            number_of_notes=values.get("number_of_notes"),
            notes_interval_seconds=values.get("notes_interval_seconds"),
            number_of_warnings=values.get("number_of_warnings"),
            warning_message=values.get("warning_message"),
            warning_interval_seconds=values.get("warning_interval_seconds"),
            number_of_punishments=values.get("number_of_punishments"),
            punish_message=values.get("punish_message"),
            punish_interval_seconds=values.get("punish_interval_seconds"),
            min_server_players_for_punish=values.get("min_server_players_for_punish"),
            kick_after_max_punish=values.get("kick_after_max_punish"),
            min_server_players_for_kick=values.get("min_server_players_for_kick"),
            kick_grace_period_seconds=values.get("kick_grace_period_seconds"),
            kick_message=values.get("kick_message"),
        )

        if not dry_run:
            set_user_config(
                AutoModNoSoloTankUserConfig.KEY(), validated_conf.model_dump()
            )

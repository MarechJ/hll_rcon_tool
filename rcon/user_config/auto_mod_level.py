from typing import Optional, TypedDict

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, field_serializer
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from rcon.types import Roles
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

ANNOUNCE_MESSAGE = "This server is under level thresholds control.\n\n{min_level_msg}{max_level_msg}{level_thresholds_msg}\nThanks for understanding."
FORCEKICK_MESSAGE = "You violated level thresholds rules on this server: {violation}."
MIN_LEVEL_MESSAGE = "Access to this server is not allowed under level {level}"
MAX_LEVEL_MESSAGE = "Access to this server is not allowed over level {level}"
VIOLATION_MESSAGE = "{role} are not allowed under level {level}"
WARNING_MESSAGE = "Warning, {player_name}! You violate level thresholds rules on this server: {violation}\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\nNext check will happen automatically in {next_check_seconds}s."
PUNISH_MESSAGE = "You violated level thresholds rules on this server: {violation}.\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\nNext check in {next_check_seconds} seconds"
KICK_MESSAGE = "You violated level thresholds rules on this server: {violation}.\nYour grace period of {kick_grace_period}s has passed.\nYou failed to comply with the previous warnings."


class RoleType(TypedDict):
    label: str
    min_players: int
    min_level: int


class AutoModLevelType(TypedDict):
    enabled: bool
    discord_webhook_url: Optional[HttpUrl]
    announcement_enabled: bool
    only_announce_impacted_players: bool
    announcement_message: str
    force_kick_message: str
    min_level: int
    min_level_message: str
    max_level: int
    max_level_message: str
    violation_message: str
    levelbug_enabled: bool
    level_thresholds: dict[Roles, "Role"]

    number_of_warnings: int
    warning_message: str
    warning_interval_seconds: int

    number_of_punishments: int
    punish_message: str
    punish_interval_seconds: int

    kick_after_max_punish: bool
    kick_grace_period_seconds: int
    kick_message: str


class Role(BaseModel):
    label: str
    min_players: int = Field(ge=0, le=100)
    min_level: int = Field(ge=0, le=500)


def validate_level_thresholds(vs):
    """Required to prevent validation errors for empty values"""
    if not vs or vs == []:
        return dict()

    validated_level_threshholds: dict[Roles, Role] = {}
    for raw_role, obj in vs.items():
        validated_level_threshholds[Roles(raw_role)] = Role(
            label=obj.get("label"),
            min_players=obj.get("min_players"),
            min_level=obj.get("min_level"),
        )

    return validated_level_threshholds


class AutoModLevelUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)
    announcement_enabled: bool = Field(default=True)
    only_announce_impacted_players: bool = Field(default=False)
    announcement_message: str = Field(default=ANNOUNCE_MESSAGE)
    force_kick_message: str = Field(default=FORCEKICK_MESSAGE)
    min_level: int = Field(ge=0, le=500, default=0)
    min_level_message: str = Field(default=MIN_LEVEL_MESSAGE)
    max_level: int = Field(ge=0, le=500, default=0)
    max_level_message: str = Field(default=MAX_LEVEL_MESSAGE)
    violation_message: str = Field(default=VIOLATION_MESSAGE)
    levelbug_enabled: bool = Field(default=True)
    level_thresholds: Annotated[
        dict[Roles, Role], BeforeValidator(validate_level_thresholds)
    ] = Field(default_factory=dict)

    number_of_warnings: int = Field(ge=-1, default=2)
    warning_message: str = Field(default=WARNING_MESSAGE)
    warning_interval_seconds: int = Field(ge=1, default=60)

    number_of_punishments: int = Field(ge=-1, default=2)
    punish_message: str = Field(default=PUNISH_MESSAGE)
    punish_interval_seconds: int = Field(ge=1, default=60)

    kick_after_max_punish: bool = Field(default=True)
    kick_grace_period_seconds: int = Field(ge=1, default=120)
    kick_message: str = Field(default=KICK_MESSAGE)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @staticmethod
    def save_to_db(values: AutoModLevelType, dry_run=False):
        key_check(AutoModLevelType.__required_keys__, values.keys())

        validated_conf = AutoModLevelUserConfig(
            enabled=values.get("enabled"),
            discord_webhook_url=values.get("discord_webhook_url"),
            announcement_enabled=values.get("announcement_enabled"),
            only_announce_impacted_players=values.get("only_announce_impacted_players"),
            announcement_message=values.get("announcement_message"),
            force_kick_message=values.get("force_kick_message"),
            min_level=values.get("min_level"),
            min_level_message=values.get("min_level_message"),
            max_level=values.get("max_level"),
            max_level_message=values.get("max_level_message"),
            violation_message=values.get("violation_message"),
            levelbug_enabled=values.get("levelbug_enabled"),
            level_thresholds=values.get("level_thresholds"),
            number_of_warnings=values.get("number_of_warnings"),
            warning_message=values.get("warning_message"),
            warning_interval_seconds=values.get("warning_interval_seconds"),
            number_of_punishments=values.get("number_of_punishments"),
            punish_message=values.get("punish_message"),
            punish_interval_seconds=values.get("punish_interval_seconds"),
            kick_after_max_punish=values.get("kick_after_max_punish"),
            kick_grace_period_seconds=values.get("kick_grace_period_seconds"),
            kick_message=values.get("kick_message"),
        )

        if not dry_run:
            set_user_config(AutoModLevelUserConfig.KEY(), validated_conf.model_dump())

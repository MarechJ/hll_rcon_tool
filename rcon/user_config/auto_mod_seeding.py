from typing import ClassVar, Optional, TypedDict

from pydantic import BaseModel, Field

from rcon.types import Roles
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

DISALLOWED_ROLES_VIOLATION_MESSAGE = "{role} are not allowed when server is seeding"
DISALLOWED_WEAPONS_VIOLATION_MESSAGE = "{weapon} are not allowed when server is seeding"
ENFORCE_CAP_FIGHT_VIOLATION_MESSAGE = "Attacking 4th cap while seeding is not allowed"


class DisallowedRolesType(TypedDict):
    min_players: int
    max_players: int
    roles: dict[Roles, str]
    violation_message: str


class DisallowedWeaponsType(TypedDict):
    min_players: int
    max_players: int
    weapons: dict[str, str]
    violation_message: str


class EnforceCapFightType(TypedDict):
    min_players: int
    max_players: int
    max_caps: int
    skip_warning: bool
    violation_message: str


class AutoModSeedingType(TypedDict):
    enabled: bool
    discord_webhook_url: Optional[str]
    announcement_enabled: bool
    announcement_message: str

    number_of_warnings: int
    warning_message: str
    warning_interval_seconds: int

    number_of_punishments: int
    punish_message: str
    punish_interval_seconds: int

    kick_after_max_punish: bool
    kick_grace_period_seconds: int
    kick_message: str

    disallowed_roles: DisallowedRolesType
    disallowed_weapons: DisallowedWeaponsType
    enforce_cap_fight: EnforceCapFightType


class DisallowedRoles(BaseModel):
    min_players: int = Field(ge=0, le=50, default=5)
    max_players: int = Field(ge=0, le=50, default=30)
    roles: dict[Roles, str] = Field(default_factory=dict)
    violation_message: str = Field(default=DISALLOWED_ROLES_VIOLATION_MESSAGE)


class DisallowedWeapons(BaseModel):
    min_players: int = Field(ge=0, le=50, default=5)
    max_players: int = Field(ge=0, le=50, default=30)
    weapons: dict[str, str] = Field(default_factory=dict)
    violation_message: str = Field(DISALLOWED_WEAPONS_VIOLATION_MESSAGE)


class EnforceCapFight(BaseModel):
    min_players: int = Field(ge=0, le=50, default=5)
    max_players: int = Field(ge=0, le=50, default=30)
    max_caps: int = Field(ge=2, le=4, default=3)
    skip_warning: bool = Field(default=False)
    violation_message: str = Field(default=ENFORCE_CAP_FIGHT_VIOLATION_MESSAGE)


class AutoModSeedingUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "auto_mod_seeding"

    enabled: bool = Field(default=False)
    discord_webhook_url: Optional[str] = Field(default=None)
    announcement_enabled: bool
    announcement_message: str

    number_of_warnings: int
    warning_message: str
    warning_interval_seconds: int

    number_of_punishments: int
    punish_message: str
    punish_interval_seconds: int

    kick_after_max_punish: bool
    kick_grace_period_seconds: int
    kick_message: str

    disallowed_roles: DisallowedRoles
    disallowed_weapons: DisallowedWeapons
    enforce_cap_fight: EnforceCapFight

    @staticmethod
    def save_to_db(values: AutoModSeedingType, dry_run=False):
        key_check(AutoModSeedingType.__required_keys__, values.keys())

        disallowed_roles = DisallowedRoles(
            min_players=values.get("disallowed_roles").get("min_players"),
            max_players=values.get("disallowed_roles").get("max_players"),
            roles=values.get("disallowed_roles").get("roles"),
            violation_message=values.get("disallowed_roles").get("violation_message"),
        )

        disallowed_weapons = DisallowedWeapons(
            min_players=values.get("disallowed_weapons").get("min_players"),
            max_players=values.get("disallowed_weapons").get("max_players"),
            weapons=values.get("disallowed_weapons").get("weapons"),
            violation_message=values.get("disallowed_weapons").get("violation_message"),
        )

        enforce_cap_fight = EnforceCapFight(
            min_players=values.get("enforce_cap_fight").get("min_players"),
            max_players=values.get("enforce_cap_fight").get("max_players"),
            max_caps=values.get("enforce_cap_fight").get("max_caps"),
            skip_warning=values.get("enforce_cap_fight").get("skip_warning"),
            violation_message=values.get("enforce_cap_fight").get("violation_message"),
        )

        validated_conf = AutoModSeedingUserConfig(
            enabled=values.get("enabled"),
            discord_webhook_url=values.get("discord_webhook_url"),
            announcement_enabled=values.get("announcement_enabled"),
            announcement_message=values.get("announcement_message"),
            number_of_warnings=values.get("number_of_warnings"),
            warning_message=values.get("warning_message"),
            warning_interval_seconds=values.get("warning_interval_seconds"),
            number_of_punishments=values.get("number_of_punishments"),
            punish_message=values.get("punish_message"),
            punish_interval_seconds=values.get("punish_interval_seconds"),
            kick_after_max_punish=values.get("kick_after_max_punish"),
            kick_grace_period_seconds=values.get("kick_grace_period_seconds"),
            kick_message=values.get("kick_message"),
            disallowed_roles=disallowed_roles,
            disallowed_weapons=disallowed_weapons,
            enforce_cap_fight=enforce_cap_fight,
        )

        if not dry_run:
            set_user_config(AutoModSeedingUserConfig.KEY(), validated_conf.model_dump())

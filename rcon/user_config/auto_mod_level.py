import enum
from typing import ClassVar, Optional, TypedDict

from pydantic import BaseModel, Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

ANNOUNCE_MESSAGE = "This server is under level thresholds control.\n\n{min_level_msg}{max_level_msg}{level_thresholds_msg}\nThanks for understanding."
FORCEKICK_MESSAGE = "You violated level thresholds rules on this server: {violation}."
MIN_LEVEL_MESSAGE = "Access to this server is not allowed under level {level}"
MAX_LEVEL_MESSAGE = "Access to this server is not allowed over level {level}"
VIOLATION_MESSAGE = "{role} are not allowed under level {level}"
WARNING_MESSAGE = "Warning, {player_name}! You violate level thresholds rules on this server: {violation}\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\nNext check will happen automatically in {next_check_seconds}s."
PUNISH_MESSAGE = "You violated level thresholds rules on this server: {violation}.\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\nNext check in {next_check_seconds} seconds"
KICK_MESSAGE = "You violated level thresholds rules on this server: {violation}.\nYour grace period of {kick_grace_period}s has passed.\nYou failed to comply with the previous warnings."


class Roles(enum.Enum):
    commander = "commander"
    squad_lead = "officer"
    rifleman = "rifleman"
    engineer = "engineer"
    medic = "medic"
    anti_tank = "antitank"
    automatic_rifleman = "automaticrifleman"
    assault = "assault"
    machine_gunner = "heavyachinegunner"
    support = "support"
    spotter = "spotter"
    sniper = "sniper"
    tank_commander = "tankcommander"
    crewman = "crewman"


ROLES_TO_LABELS = {
    Roles.commander: "Commander",
    Roles.squad_lead: "Squad Lead",
    Roles.rifleman: "Rifleman",
    Roles.engineer: "Engineer",
    Roles.medic: "Medic",
    Roles.anti_tank: "Anti-Tank",
    Roles.automatic_rifleman: "Automatic Rifleman",
    Roles.assault: "Assault",
    Roles.machine_gunner: "Machinegunner",
    Roles.support: "Support",
    Roles.spotter: "Spotter",
    Roles.sniper: "Sniper",
    Roles.tank_commander: "Tank Commander",
    Roles.crewman: "Crewman",
}


class RoleType(TypedDict):
    role: Roles
    label: str
    min_players: int
    min_level: int


class AutoModLevelType(TypedDict):
    enabled: bool
    discord_webhook_url: str
    announcement_enabled: bool
    announcement_message: str
    force_kick_message: str
    min_level: int
    min_level_message: str
    max_level: int
    max_level_message: str
    violation_message: str
    level_thresholds: dict[Roles, RoleType]

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
    role: Roles
    label: str
    min_players: int = Field(ge=0, le=50)
    min_level: int = Field(ge=0, le=500)


class AutoModLevelUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "auto_mod_level"

    enabled: bool = Field(default=False)
    discord_webhook_url: Optional[str]
    announcement_enabled: bool = Field(default=True)
    announcement_message: str = Field(default=ANNOUNCE_MESSAGE)
    force_kick_message: str = Field(default=FORCEKICK_MESSAGE)
    min_level: int = Field(ge=0, le=500, default=0)
    min_level_message: str = Field(default=MIN_LEVEL_MESSAGE)
    max_level: int = Field(ge=0, le=500, default=0)
    max_level_message: str = Field(default=MAX_LEVEL_MESSAGE)
    violation_message: str = Field(default=VIOLATION_MESSAGE)
    level_thresholds: dict[Roles, Role] = Field(default_factory=dict)

    number_of_warnings: int = Field(ge=-1, default=2)
    warning_message: str = Field(default=WARNING_MESSAGE)
    warning_interval_seconds: int = Field(ge=1, default=60)

    number_of_punishments: int = Field(ge=0, default=2)
    punish_message: str = Field(default=PUNISH_MESSAGE)
    punish_interval_seconds: int = Field(ge=1, default=60)

    kick_after_max_punish: bool = Field(default=True)
    kick_grace_period_seconds: int = Field(ge=1, default=120)
    kick_message: str = Field(default=KICK_MESSAGE)

    @staticmethod
    def save_to_db(values: AutoModLevelType, dry_run=False):
        key_check(AutoModLevelType.__required_keys__, values.keys())

        validated_level_threshholds: list[Role] = []
        for raw_role in values.get("level_thresholds"):
            pass

        validated_conf = AutoModLevelUserConfig(
            enabled=values.get("enabled"),
            discord_webhook_url=values.get("discord_webhook_url"),
            announcement_enabled=values.get("announcement_enabled"),
            announcement_message=values.get("announcement_message"),
            force_kick_message=values.get("force_kick_message"),
            min_level=values.get("min_level"),
            min_level_message=values.get("min_level_message"),
            max_level=values.get("max_level"),
            max_level_message=values.get("max_level_message"),
            violation_message=values.get("violation_message"),
            level_thresholds=validated_level_threshholds,
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

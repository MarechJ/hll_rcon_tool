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
    dry_run: bool
    discord_webhook_url: Optional[HttpUrl]

    whitelist_flags: list[str]
    dont_do_anything_below_this_number_of_players: int

    announcement_enabled: bool
    only_announce_impacted_players: bool
    announcement_message: str

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

    force_kick_message: str
    min_level: int
    min_level_message: str
    max_level: int
    max_level_message: str
    violation_message: str
    levelbug_enabled: bool
    level_thresholds: dict[Roles, "Role"]


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
    enabled: bool = Field(default=False, title="Enable", description="Whether the Level Automod is enabled or not")
    dry_run: bool = Field(default=False, title="Dry-Run", description="If checked and if the Level Automod is enabled, no actions are done to the players. You can observe what actions the Automod would've done in the audit logs")
    discord_webhook_url: Optional[HttpUrl] = Field(default=None, title="Discord Webhook URL", description="A webhook URL for a Discord channel to write audit messages (what the Automod did) to")

    whitelist_flags: list[str] = Field(default_factory=list, title="Whitelist Flags", description="Players having one of the flags will be excluded from action sof the Automod")
    dont_do_anything_below_this_number_of_players: int = Field(ge=0, le=100, default=0, title="Min Player Threshold", description="If the player count of the server is beneath this threshold, it will not do anything")

    announcement_enabled: bool = Field(default=False, title="Enable Announcements", description="Send an announcement message to players, who connect to the server, that it is under level threshold enforcement")
    only_announce_impacted_players: bool = Field(default=True, title="Restrict Announcement", description="If checked, announcement messages (if enabled) are only sent to players who are affected by the level Automod")
    announcement_message: str = Field(default=ANNOUNCE_MESSAGE, title="Announcement Message", description="The announcement message to send to players")

    number_of_warnings: int = Field(ge=-1, default=2, title="Number of warnings", description="The number of warning messages to an impacted player, before the Automod transitions to the next stage")
    warning_interval_seconds: int = Field(ge=1, default=60, title="Warning Interval", description="The interval in seconds in which warning messages should be send, if the player did not remediate the level threshold")
    warning_message: str = Field(default=WARNING_MESSAGE, title="Warning Message", description="The warning message send to a player who violates level requirements")

    number_of_punishments: int = Field(ge=-1, default=2, title="Number of punishments", description="The number of punishes to an impacted player, before the Automod transitions to the next stage")
    min_squad_players_for_punish: int = Field(ge=0, le=6, default=0, title="Punishment minimum squad players", description="Minimum number of players in the squad of an impacted player to punish")
    min_server_players_for_punish: int = Field(ge=0, le=100, default=0, title="Punishment minimum server players", description="Minimum number of players on the server for an impacted player to punish")
    punish_interval_seconds: int = Field(ge=1, default=60, title="Punish Interval", description="The interval in seconds in which the player is punished, if they did not remediate the level threshold")
    punish_message: str = Field(default=PUNISH_MESSAGE, title="Punish message", description="The message the player sees when they are punished by the level Automod")

    kick_after_max_punish: bool = Field(default=True, title="Enable Kick", description="Whether kicking a player is enabled as a stage of the level Automod after all punishments are exhausted")
    min_squad_players_for_kick: int = Field(ge=0, le=6, default=0, title="Kick minimum squad players", description="Minimum number of players in the squad of an impacted player to be kicked")
    min_server_players_for_kick: int = Field(ge=0, le=100, default=0, title="Kick minimum server players", description="Minimum number of players on the server for an impacted player to be kicked")
    kick_grace_period_seconds: int = Field(ge=1, default=60, title="Kick Grace Period", description="A grace period in seconds since the last punishment the player has time to remediate the level violation before they are kicked")
    kick_message: str = Field(default=KICK_MESSAGE, title="Kick message", description="The message the player sees when they are kicked by the level Automod")

    force_kick_message: str = Field(default=FORCEKICK_MESSAGE, title="Server Level Kick Message", description="The message the player sees when they are kicked because they do not meet the server level requirement")
    min_level: int = Field(ge=0, le=500, default=0, title="Server Minimum Level", description="The minimum level a player needs to have to join the server")
    min_level_message: str = Field(default=MIN_LEVEL_MESSAGE, title="Server Minimum Level Message", description="A message template for Server Level Kick Message when the player violated the minimum server level requirement")
    max_level: int = Field(ge=0, le=500, default=0, title="Server Maximum Level", description="The maximum level a player needs to have to join the server")
    max_level_message: str = Field(default=MAX_LEVEL_MESSAGE, title="Server Maximum Level Message", description="A message template for Server Level Kick Message when the player violated the maximum server level requirement")
    violation_message: str = Field(default=VIOLATION_MESSAGE, title="Violation Message", description="A message the player sees when they violate the level requirement for a specific role")
    levelbug_enabled: bool = Field(default=False, title="Exclude Players with Level-Bug", description="Hell Let Loose players may suffer a level bug, meaning the game presents them with level 1, even though they've another level. Enabling this flag will exclude all level 1 players from level requirements enforced by the level Automod")
    level_thresholds: Annotated[
        dict[Roles, Role], BeforeValidator(validate_level_thresholds)
    ] = Field(default_factory=dict, title="Role Level Thresholds", description="Level thresholds for specific roles")

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
            dry_run=values.get("dry_run"),
            discord_webhook_url=values.get("discord_webhook_url"),
            whitelist_flags=values.get("whitelist_flags"),
            dont_do_anything_below_this_number_of_players=values.get(
                "dont_do_anything_below_this_number_of_players"
            ),
            announcement_enabled=values.get("announcement_enabled"),
            only_announce_impacted_players=values.get("only_announce_impacted_players"),
            announcement_message=values.get("announcement_message"),
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
            force_kick_message=values.get("force_kick_message"),
            min_level=values.get("min_level"),
            min_level_message=values.get("min_level_message"),
            max_level=values.get("max_level"),
            max_level_message=values.get("max_level_message"),
            violation_message=values.get("violation_message"),
            levelbug_enabled=values.get("levelbug_enabled"),
            level_thresholds=values.get("level_thresholds"),
        )

        if not dry_run:
            set_user_config(AutoModLevelUserConfig.KEY(), validated_conf)

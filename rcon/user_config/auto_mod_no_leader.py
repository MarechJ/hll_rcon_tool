from typing import Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer, field_validator
from steam.protobufs.steammessages_unified_base_pb2 import description

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
    enabled: bool = Field(default=False, title="Enable", description="Whether the Automod is enabled or not")
    dry_run: bool = Field(default=False, title="Dry-Run", description="If checked and if the Automod is enabled, no actions are done to the players. You can observe what actions the Automod would've done in the audit logs")
    discord_webhook_url: Optional[HttpUrl] = Field(default=None, title="Discord Webhook URL", description="A webhook URL for a Discord channel to write audit messages (what the Automod did) to")

    whitelist_flags: list[str] = Field(default_factory=list, title="Whitelist Flags", description="Players having one of the flags will be excluded from actions of the Automod")
    immune_roles: list[Roles] = Field(default_factory=list, title="Immune Roles", description="Players playing these roles are exempted from actions done by the Automod")
    immune_player_level: int = Field(ge=0, le=500, default=0, title="Minimum Level", description="Player having a level lower or equal than this level are exempted from actions done by the Automod")
    dont_do_anything_below_this_number_of_players: int = Field(ge=0, le=100, default=0, title="Minimum Players", description="The minimum number of players that need to be on the server. If less players are online, the Automod does not do any action")

    number_of_notes: int = Field(ge=0, default=1, title="Number of notes", description="The amount of 'notes' the Automod does before transitioning to the next punishment level. Notes do not have any visible action to the player")
    notes_interval_seconds: int = Field(ge=1, default=10, title="Notes interval", description="The time in seconds between the same player is 'noted' by the Automod")

    number_of_warnings: int = Field(ge=-1, default=2, title="Number of warnings", description="The amount the Automod sends a warning message to the player before transitioning to the next punishment level")
    warning_interval_seconds: int = Field(ge=0, default=60, title="Warning interval", description="The time in seconds between the same player is warned by the Automod")
    warning_message: str = Field(default=WARNING_MESSAGE, title="Warning message", description="The message that is send to a player as a warning")

    number_of_punishments: int = Field(ge=-1, default=2, title="Number of punishes", description="The amount the Automod punishes the player before transitioning to the next punishment level")
    min_squad_players_for_punish: int = Field(ge=0, le=6, default=0, title="Punishment minimum squad players", description="Minimum number of players in the squad of an impacted player to punish")
    min_server_players_for_punish: int = Field(ge=0, le=100, default=0, title="Punishment minimum server players", description="Minimum number of players on the server for an impacted player to punish")
    punish_interval_seconds: int = Field(ge=0, default=60, title="Punish Interval", description="The interval in seconds in which the player is punished")
    punish_message: str = Field(default=PUNISH_MESSAGE, title="Punish message", description="The message that the player sees when punished")

    kick_after_max_punish: bool = Field(default=True, title="Enable Kick", description="Whether kicking a player is enabled as a stage of the Automod after all punishments are exhausted")
    min_squad_players_for_kick: int = Field(ge=0, le=6, default=0, title="Kick minimum squad players", description="Minimum number of players in the squad of an impacted player to be kicked")
    min_server_players_for_kick: int = Field(ge=0, le=100, default=0, title="Kick minimum server players", description="Minimum number of players on the server for an impacted player to be kicked")
    kick_grace_period_seconds: int = Field(ge=0, default=60, title="Kick Grace Period", description="A grace period in seconds since the last punishment the player has time to remediate the missing squad leader violation before they are kicked")
    kick_message: str = Field(default=KICK_MESSAGE, title="Kick message", description="The message the player sees when they are kicked by the Automod")

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

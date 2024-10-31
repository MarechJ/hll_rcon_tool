from typing import Optional, TypedDict

from pydantic import BaseModel, Field, HttpUrl, field_serializer, field_validator

from rcon.types import Roles
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


WARNING_MESSAGE = """Warning, {player_name}! You violate seeding rules on this server: {violation}
You will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.
Next check will happen automatically in {next_check_seconds}s."""
KICK_MESSAGE = """You violated seeding rules on this server.
Your grace period of {kick_grace_period}s has passed.
You failed to comply with the previous warnings."""
PUNISH_MESSAGE = """You violated seeding rules on this server: {violation}.
You're being punished by a bot ({received_punishes}/{max_punishes}).
Next check in {next_check_seconds} seconds"""
ANNOUNCEMENT_MESSAGE = """We are trying to populate the server! That means special rules apply.

- {disallowed_roles} are not allowed (until {disallowed_roles_max_players} players are online)
- {disallowed_weapons} are not allowed (until {disallowed_weapons_max_players} players are online)

Thanks for understanding and helping us seed!"""
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
    dry_run: bool
    discord_webhook_url: Optional[HttpUrl]

    whitelist_flags: list[str]
    immune_roles: list[Roles]
    immune_player_level: int
    dont_do_anything_below_this_number_of_players: int

    announcement_enabled: bool
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

    disallowed_roles: DisallowedRolesType
    disallowed_weapons: DisallowedWeaponsType
    enforce_cap_fight: EnforceCapFightType


class DisallowedRoles(BaseModel):
    min_players: int = Field(ge=0, le=100, default=0, title="Minimum Players", description="The minimum players on the server to enforce this rule")
    max_players: int = Field(ge=0, le=100, default=100, title="Maximum Players", description="The maximum players on the server to enforce this rule")
    roles: dict[Roles, str] = Field(default_factory=dict, title="Disallowed Roles", description="The list of roles that are not allowed while server is seeding")
    violation_message: str = Field(default=DISALLOWED_ROLES_VIOLATION_MESSAGE, title="Violation Message", description="The message send to the player when they use one of the disallowed roles")


class DisallowedWeapons(BaseModel):
    min_players: int = Field(ge=0, le=100, default=0, title="Minimum Players", description="The minimum players on the server to enforce this rule")
    max_players: int = Field(ge=0, le=100, default=100, title="Maximum Players", description="The maximum players on the server to enforce this rule")
    weapons: dict[str, str] = Field(default_factory=dict, title="Disallowed Weapons", description="The list of weapons that are not allowed while server is seeding")
    violation_message: str = Field(default=DISALLOWED_WEAPONS_VIOLATION_MESSAGE, title="Violation Message", description="The message send to the player when they use one of the disallowed roles")


class EnforceCapFight(BaseModel):
    min_players: int = Field(ge=0, le=100, default=0, title="Minimum Players", description="The minimum players on the server to enforce this rule")
    max_players: int = Field(ge=0, le=100, default=100, title="Maximum Players", description="The maximum players on the server to enforce this rule")
    max_caps: int = Field(ge=2, le=4, default=3, title="Maximum capped Points", description="The maximum number of cap points that can be capped by one team. Starting to cap another point will violate this rule")
    skip_warning: bool = Field(default=False, title="Skip Warning", description="If set to true the Automod will skip the warning punishment level and directly continue to punish when this rule is violated. Enable this, if capping more points than allowed should absolutely be prevented. The game will report that a point is being capped no later than 60 seconds after the cap begins to cap, which could mean that the Automod may reach a corrective measure (punish, kick) too late (if warning is, e.g., set to 60 seconds)")
    violation_message: str = Field(default=ENFORCE_CAP_FIGHT_VIOLATION_MESSAGE, title="Violation Message", description="The message send to the player when they use one of the disallowed roles")


class AutoModSeedingUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False, title="Enable", description="Whether the Level Automod is enabled or not")
    dry_run: bool = Field(default=False, title="Dry-Run", description="If checked and if the Automod is enabled, no actions are done to the players. You can observe what actions the Automod would've done in the audit logs")
    discord_webhook_url: Optional[HttpUrl] = Field(default=None, title="Discord Webhook URL", description="A webhook URL for a Discord channel to write audit messages (what the Automod did) to")

    whitelist_flags: list[str] = Field(default_factory=list, title="Whitelist Flags", description="Players having one of the flags will be excluded from actions of the Automod")
    immune_roles: list[Roles] = Field(default_factory=list, title="Immune Roles", description="Players playing these roles are exempted from actions done by the Automod")
    immune_player_level: int = Field(ge=0, le=500, default=0, title="Minimum Level", description="Player having a level lower or equal than this level are exempted from actions done by the Automod")
    dont_do_anything_below_this_number_of_players: int = Field(ge=0, le=100, default=0, title="Minimum Players", description="The minimum number of players that need to be on the server. If less players are online, the Automod does not do any action")

    announcement_enabled: bool = Field(default=False, title="Enable Announcement Message", description="Whether connecting players get a notification that the server is currently seeding")
    announcement_message: str = Field(default=ANNOUNCEMENT_MESSAGE, title="Announcement Message", description="The message to send to players connecting to the server when it is seeding")

    number_of_warnings: int = Field(default=2, title="Number of warnings", description="The amount the Automod sends a warning message to the player before transitioning to the next punishment level")
    warning_interval_seconds: int = Field(default=60, title="Warning interval", description="The time in seconds between the same player is warned by the Automod")
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

    disallowed_roles: DisallowedRoles = Field(default_factory=DisallowedRoles, title="Disallowed Roles", description="Player Role-based rules to enforce while seeding")
    disallowed_weapons: DisallowedWeapons = Field(default_factory=DisallowedWeapons, title="Disallowed Weapons", description="Weapons-based rules to enforce while seeding")
    enforce_cap_fight: EnforceCapFight = Field(default_factory=EnforceCapFight, title="Cap Fight Enforcement", description="Cap-based rules to enforce while seeding")

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
            dry_run=values.get("dry_run"),
            discord_webhook_url=values.get("discord_webhook_url"),
            whitelist_flags=values.get("whitelist_flags"),
            immune_roles=values.get("immune_roles"),
            immune_player_level=values.get("immune_player_level"),
            dont_do_anything_below_this_number_of_players=values.get(
                "dont_do_anything_below_this_number_of_players"
            ),
            announcement_enabled=values.get("announcement_enabled"),
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
            disallowed_roles=disallowed_roles,
            disallowed_weapons=disallowed_weapons,
            enforce_cap_fight=enforce_cap_fight,
        )

        if not dry_run:
            set_user_config(AutoModSeedingUserConfig.KEY(), validated_conf)

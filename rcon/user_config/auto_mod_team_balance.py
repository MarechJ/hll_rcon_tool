from typing import Optional, TypedDict

from pydantic import Field, HttpUrl, field_serializer

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

SWITCH_MESSAGE = """You have been switched to balance the teams after a steamroll.

Your whole squad was moved together. Thanks for helping keep the match fair!"""


class AutoModTeamBalanceType(TypedDict):
    enabled: bool
    dry_run: bool
    discord_webhook_url: Optional[HttpUrl]

    # Steamroll trigger (duration based, never margin based)
    fast_match_minutes: int
    win_streak_threshold: int

    # Seeding guard
    skip_when_seeding: bool
    seeding_player_threshold: int

    # Armor category (balanced separately)
    balance_armor: bool
    max_armor_squad_delta: int
    armor_score_gap_threshold: int

    # Infantry / headcount balance
    min_players_for_balance: int
    max_players_per_team_delta: int
    score_gap_threshold: int
    weight_combat: float
    weight_offense: float
    weight_defense: float
    weight_support: float
    exclude_recon: bool
    max_players_to_switch: int

    switch_message: str


class AutoModTeamBalanceUserConfig(BaseUserConfig):
    """Move whole squads at match end to rebalance the teams after a steamroll.

    A steamroll is defined by match DURATION (fast matches) or repeated same-team
    wins (swap aware), never by score margin. Armor squads are balanced as their
    own category; infantry squads are balanced by headcount and combat score.
    """

    enabled: bool = Field(default=False)
    dry_run: bool = Field(default=False)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)

    # --- Steamroll trigger ---
    fast_match_minutes: int = Field(
        ge=1,
        le=180,
        default=30,
        title="Fast match minutes",
        description=(
            "A match that ended in fewer minutes than this is treated as a "
            "steamroll. Duration based only - a long decisive win is NOT a "
            "steamroll."
        ),
    )
    win_streak_threshold: int = Field(
        ge=0,
        le=20,
        default=3,
        title="Win streak threshold",
        description=(
            "Trigger when the same effective team (swap aware) has won this many "
            "matches in a row. 0 disables the streak trigger."
        ),
    )

    # --- Seeding guard ---
    skip_when_seeding: bool = Field(
        default=True,
        title="Skip when seeding",
        description="Never rebalance while the server is still seeding.",
    )
    seeding_player_threshold: int = Field(
        ge=0,
        le=100,
        default=50,
        title="Seeding player threshold",
        description=(
            "Population at or below this count is considered seeding and is "
            "skipped when 'Skip when seeding' is enabled."
        ),
    )

    # --- Armor category (balanced separately) ---
    balance_armor: bool = Field(
        default=True,
        title="Balance armor",
        description="Balance armor squads as their own category before infantry.",
    )
    max_armor_squad_delta: int = Field(
        ge=0,
        le=10,
        default=0,
        title="Max armor squad delta",
        description=(
            "Allowed difference in the number of armor squads between teams. "
            "0 means armor squad counts must be equal."
        ),
    )
    armor_score_gap_threshold: int = Field(
        ge=0,
        default=0,
        title="Armor score gap threshold",
        description=(
            "Maximum acceptable armor combat-effectiveness gap between teams. When "
            "greater than 0, an armor score gap above this value also triggers armor "
            "balancing (requires headroom in 'Max armor squad delta' to actually move). "
            "0 balances armor by squad count only."
        ),
    )

    # --- Infantry / headcount balance ---
    min_players_for_balance: int = Field(
        ge=0,
        le=100,
        default=40,
        title="Minimum players for balance",
        description="Do nothing unless at least this many players are online.",
    )
    max_players_per_team_delta: int = Field(
        ge=0,
        le=50,
        default=2,
        title="Max players per team delta",
        description="Allowed difference in team headcount after balancing.",
    )
    score_gap_threshold: int = Field(
        ge=0,
        default=0,
        title="Infantry score gap threshold",
        description=(
            "Maximum acceptable infantry combat-effectiveness gap between teams. "
            "0 always tries to close the gap."
        ),
    )
    weight_combat: float = Field(
        ge=0,
        default=1.0,
        title="Combat weight",
        description="Weight of the combat score.",
    )
    weight_offense: float = Field(
        ge=0,
        default=1.0,
        title="Offense weight",
        description="Weight of the offense score.",
    )
    weight_defense: float = Field(
        ge=0,
        default=1.0,
        title="Defense weight",
        description="Weight of the defense score.",
    )
    weight_support: float = Field(
        ge=0,
        default=1.0,
        title="Support weight",
        description="Weight of the support score.",
    )
    exclude_recon: bool = Field(
        default=True,
        title="Exclude recon",
        description="Never move recon squads (Commander is always excluded).",
    )
    max_players_to_switch: int = Field(
        ge=0,
        le=100,
        default=0,
        title="Max players to switch",
        description="Cap on total players moved per match (0 means no cap).",
    )

    switch_message: str = Field(
        default=SWITCH_MESSAGE,
        title="Switch message",
        description="Message sent to players who are switched.",
    )

    @field_serializer("discord_webhook_url")
    def serialize_webhook_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @staticmethod
    def save_to_db(values: AutoModTeamBalanceType, dry_run=False) -> None:
        key_check(
            AutoModTeamBalanceType.__required_keys__,
            AutoModTeamBalanceType.__optional_keys__,
            values.keys(),
        )

        validated_conf = AutoModTeamBalanceUserConfig(
            enabled=values.get("enabled"),
            dry_run=values.get("dry_run"),
            discord_webhook_url=values.get("discord_webhook_url"),
            fast_match_minutes=values.get("fast_match_minutes"),
            win_streak_threshold=values.get("win_streak_threshold"),
            skip_when_seeding=values.get("skip_when_seeding"),
            seeding_player_threshold=values.get("seeding_player_threshold"),
            balance_armor=values.get("balance_armor"),
            max_armor_squad_delta=values.get("max_armor_squad_delta"),
            armor_score_gap_threshold=values.get("armor_score_gap_threshold"),
            min_players_for_balance=values.get("min_players_for_balance"),
            max_players_per_team_delta=values.get("max_players_per_team_delta"),
            score_gap_threshold=values.get("score_gap_threshold"),
            weight_combat=values.get("weight_combat"),
            weight_offense=values.get("weight_offense"),
            weight_defense=values.get("weight_defense"),
            weight_support=values.get("weight_support"),
            exclude_recon=values.get("exclude_recon"),
            max_players_to_switch=values.get("max_players_to_switch"),
            switch_message=values.get("switch_message"),
        )

        if not dry_run:
            set_user_config(AutoModTeamBalanceUserConfig.KEY(), validated_conf)

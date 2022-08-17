from dataclasses import dataclass, field  # TODO: replace with pydantic data classes
from typing import List, Callable

VALID_AUTOBALANCE_METHODS = ("random", "arrival_most_recent", "arrival_least_recent")


@dataclass
class AutoBalanceConfig:
    """Represents the config options in config/config.yml"""

    discord_webhook_url: str = ""
    min_players_for_balance: int = 0
    min_seconds_between_team_balances: int = 0
    min_seconds_between_player_swaps: int = 0
    player_count_threshold: int = 0
    auto_rebalance_method: str = "arrival_most_recent"  # TODO: add field validation
    swap_on_death: bool = True
    include_teamless_players: bool = False
    immuned_level_up_to: int = 0
    immuned_roles: Callable[[], List[str]] = field(
        default_factory=tuple
    )  # TODO: fix type annotation

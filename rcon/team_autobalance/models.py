# TODO: replace with pydantic data classes
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, NewType

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


DetailedPlayerInfo = NewType("DetailedPlayerInfo", Dict[str, Any])
"""
        rcon.extended_commands.get_detailed_player_info()
        
        Name: T17 Scott
        steamID64: 01234567890123456
        Team: Allies            # "None" when not in team
        Role: Officer           
        Unit: 0 - Able          # Absent when not in unit
        Loadout: NCO            # Absent when not in team
        Kills: 0 - Deaths: 0
        Score: C 50, O 0, D 40, S 10
        Level: 34

        """

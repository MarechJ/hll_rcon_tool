"""For moving players from the larger team to the smaller team when team sizes are unequal"""

import logging
import random
from datetime import datetime, timezone

import redis

from rcon.recorded_commands import RecordedRcon
from rcon.team_shuffle.constants import (
    ALLIED_TEAM,
    AXIS_TEAM,
    EMPTY_TEAM,
    SWAP_TYPE_EVEN_TEAMS,
)
from rcon.team_shuffle.models import BalanceAPIRequest, TeamShuffleConfig
from rcon.team_shuffle.utils import (
    check_swap_rate_limit,
    get_player_last_swap_timestamp,
    get_player_session,
    get_players_on_team,
    get_team_player_count,
    select_players_randomly,
    swap_players,
    swap_teamless_players,
)
from rcon.types import TeamViewPlayerType, TeamViewType

logger = logging.getLogger("rcon.team_shuffle")


def even_teams(
    rcon_hook: RecordedRcon,
    redis_store: redis.StrictRedis,
    config: TeamShuffleConfig,
    rebalance_method: str = "random",
    immune_level: int = 0,
    immune_roles: list[str] | None = None,
    immune_seconds: int = 0,
    include_teamless: bool = True,
    swap_on_death: bool = False,
) -> tuple[
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
]:
    """Verify if criteria for balancing has been met and then swap players.

    Returns
    original axis players, swapped axis players,
    original allied players, swapped allied players
    original teamless players, swapped teamless players
    """

    # Creating this model validates all of the input arguments or raises a ValueError
    args = BalanceAPIRequest(
        rebalance_method=rebalance_method,
        immune_level=immune_level,
        immune_roles=immune_roles,
        immune_seconds=immune_seconds,
        include_teamless=include_teamless,
        swap_on_death=swap_on_death,
    )

    # raises SwapRateLimitError if conditions not met
    check_swap_rate_limit(redis_store, config.rate_limit_sec)

    # Only making one team_view call and passing it down to all the sub functions
    # so if one more players changes teams, roles, etc. during a balance we don't
    # end up in some weird inconsistent state

    # This does mean that a player might still be swapped or not swapped if their
    # info has changed since the request was made

    team_view: TeamViewType = rcon_hook.get_team_view()

    larger_team_name = find_larger_team_name(team_view)
    smaller_team_name = ALLIED_TEAM if larger_team_name == AXIS_TEAM else AXIS_TEAM

    larger_team_players = get_players_on_team(team_view, larger_team_name)
    smaller_team_players = get_players_on_team(team_view, smaller_team_name)
    teamless_players = get_players_on_team(team_view, EMPTY_TEAM)

    if larger_team_name == AXIS_TEAM:
        axis_players = larger_team_players
        allied_players = smaller_team_players
    else:
        axis_players = smaller_team_players
        allied_players = larger_team_players

    # Bail out early with error messages if we can't balance due to team sizes
    if len(larger_team_players) == 0 and len(smaller_team_players) == 0:
        if not args.include_teamless:
            logger.info(
                f"Both teams were empty and `({len(teamless_players)})` teamless players aren't being considered, unable to balance."
            )
            return axis_players, [], allied_players, [], teamless_players, []
        elif args.include_teamless and len(teamless_players) == 0:
            logger.info(
                f"Both teams were empty and there are no teamless players, unable to balance."
            )
            return axis_players, [], allied_players, [], teamless_players, []

    if len(larger_team_players) == len(smaller_team_players):
        if not args.include_teamless:
            logger.info(
                f"Both teams were the same size `{len(axis_players)}`-`{len(allied_players)}` and `({len(teamless_players)})` unassigned players aren't being considered, unable to balance."
            )
            return axis_players, [], allied_players, [], teamless_players, []

    swappable_players = collect_swappable_players(
        redis_store,
        larger_team_players,
        args.immune_roles,
        args.immune_seconds,
        args.immune_level,
    )

    # Shouldn't need to use the absolute value here or check for no difference since we've determined the larger team
    team_size_delta = get_team_player_count(
        team_view, larger_team_name
    ) - get_team_player_count(team_view, smaller_team_name)

    # Even/empty team sizes is checked earlier
    if team_size_delta == 1:
        logger.info(
            "Difference between team sizes is only `1` player, unable to balance."
        )

    # Use integer division so it rounds down (swaps the fewest number of people)
    # If teamless players are included any eligible teamless player is distributed
    # even if the teams are equal size
    num_players_to_switch = team_size_delta // 2

    if len(swappable_players) < num_players_to_switch:
        logger.warning(
            f"Only `{num_players_to_switch}` players are currently swappable, missing `{(num_players_to_switch - len(swappable_players))}` players."
        )

    players_to_swap: list[TeamViewPlayerType] = []
    if args.rebalance_method == "random":
        players_to_swap = select_players_randomly(
            swappable_players, num_players_to_switch
        )
    elif args.rebalance_method == "arrival_most_recent":
        players_to_swap = select_players_arrival_time(
            swappable_players, num_players_to_switch, most_recent=True
        )
    elif args.rebalance_method == "arrival_least_recent":
        players_to_swap = select_players_arrival_time(
            swappable_players, num_players_to_switch, most_recent=False
        )

    # Perform a swap action on each selected player who was on a team to begin with
    swapped_axis_players: list[TeamViewPlayerType]
    swapped_allied_players: list[TeamViewPlayerType]
    swapped_axis_players, swapped_allied_players = swap_players(
        rcon_hook,
        redis_store,
        config,
        players_to_swap=players_to_swap,
        swap_type=SWAP_TYPE_EVEN_TEAMS,
        swap_message=config.even_teams_swap_message,
        swap_on_death=args.swap_on_death,
    )

    # Distribute teamless players to each team, choosing which team to start with at random
    alternating_teams = (AXIS_TEAM, ALLIED_TEAM)
    if random.choice(alternating_teams) == ALLIED_TEAM:
        alternating_teams = (ALLIED_TEAM, AXIS_TEAM)

    teamless_players_to_swap: list[TeamViewPlayerType] = []
    if args.include_teamless:
        teamless_players_to_swap = teamless_players
        swap_teamless_players(
            rcon_hook,
            redis_store,
            config,
            teamless_players_to_swap=teamless_players_to_swap,
            swap_type=SWAP_TYPE_EVEN_TEAMS,
            swap_message=config.even_teams_swap_message,
            swap_on_death=swap_on_death,
        )

    return (
        axis_players,
        swapped_axis_players,
        allied_players,
        swapped_allied_players,
        teamless_players,
        teamless_players_to_swap,
    )


def is_player_swappable(
    detailed_player_info: TeamViewPlayerType,
    redis_store: redis.StrictRedis,
    immune_roles: list[str] | None,
    immune_swap_time_threshold_secs: int = 0,
    immune_level: int = 0,
) -> bool:
    """Test if a player can be swapped based on the time of their last swap, their level and role."""

    # If any of these fail we can't proceed and should abort, so not checking for missing keys
    player_name = detailed_player_info["name"]
    steam_id_64 = detailed_player_info["steam_id_64"]
    level = detailed_player_info["level"]
    role = detailed_player_info["role"]

    # If they are not on a team their role defaults to rifleman
    # maybe a problem if someone immunes riflemen but wants to swap teamless players
    # TODO: Investigate

    last_swap = get_player_last_swap_timestamp(
        redis_store, steam_id_64=steam_id_64, swap_type=SWAP_TYPE_EVEN_TEAMS
    )

    is_swappable = True
    not_swapped_reasons: list[str] = []

    if immune_roles is None:
        immune_roles = []

    if role in immune_roles:
        is_swappable = False
        not_swapped_reasons.append(f"player is playing an immune role ({role})")

    if level <= immune_level:
        is_swappable = False
        not_swapped_reasons.append(
            f"player level {level} is below immune level of {immune_level}"
        )

    seconds_since_last_swap = int(
        (datetime.now(timezone.utc) - last_swap).total_seconds()
    )
    if seconds_since_last_swap < immune_swap_time_threshold_secs:
        is_swappable = False
        not_swapped_reasons.append(
            f"player was swapped too recently {seconds_since_last_swap} seconds ago, configured limit is {immune_swap_time_threshold_secs} seconds"
        )

    if not_swapped_reasons:
        message = f"steam_id: `{steam_id_64}` player: `{player_name}` not balanced due to: `{', '.join(not_swapped_reasons)}`."
        logger.warning(message)

    return is_swappable


def find_larger_team_name(team_view: TeamViewType) -> str:
    """Return the team name of the team that has more players (axis if tied)."""
    axis_player_count = get_team_player_count(team_view, AXIS_TEAM)
    allied_player_count = get_team_player_count(team_view, ALLIED_TEAM)

    if axis_player_count >= allied_player_count:
        return AXIS_TEAM
    else:
        return ALLIED_TEAM


def select_players_arrival_time(
    players: list[TeamViewPlayerType],
    num_to_select: int,
    *,
    most_recent: bool = True,
) -> list[TeamViewPlayerType]:
    """Select up to num_to_select players based on arrival time to the server."""
    ordered_players: list[TeamViewPlayerType] = sorted(
        players,
        key=lambda p: get_player_session(p, most_recent),
        reverse=most_recent,
    )

    # If we don't have enough possible players to swap, use as many as possible
    if num_to_select > len(ordered_players):
        return ordered_players

    # Otherwise grab only the desired number of players
    return ordered_players[0:num_to_select]


def collect_swappable_players(
    redis_store: redis.StrictRedis,
    players: list[TeamViewPlayerType],
    immune_roles: list[str] | None,
    immune_seconds: int,
    immune_level: int,
) -> list[TeamViewPlayerType]:
    """Return a list of swappable players from the given list of players."""

    players = [
        player
        for player in players
        if is_player_swappable(
            player,
            redis_store,
            immune_roles,
            immune_seconds,
            immune_level,
        )
    ]

    return players


if __name__ == "__main__":
    pass

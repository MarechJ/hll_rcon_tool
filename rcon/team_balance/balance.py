import logging
import random
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence, Tuple

import redis

from rcon.recorded_commands import RecordedRcon
from rcon.team_balance.constants import (
    ALLIED_TEAM,
    AXIS_TEAM,
    DISCORD_BALANCE_SHUFFLE_WEBHOOK,
    EMPTY_TEAM,
    INSUFFICIENT_SWAPPABLE_PLAYERS_WARN_MSG,
    NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG,
    NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG,
    NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG,
    PLAYER_BALANCE_NOT_SWAPPED_MSG,
    SWAP_TYPE_BALANCE,
)
from rcon.team_balance.models import BalanceAPIRequest, DetailedPlayerInfo, RCONTeamView
from rcon.team_balance.utils import (
    audit,
    check_rate_limit,
    get_player_last_swap_timestamp,
    get_player_session,
    get_players_on_team,
    get_team_player_count,
    select_players_randomly,
    swap_players,
    swap_teamless_players,
)

logger = logging.getLogger(__name__)


def autobalance_teams(
    rcon_hook: RecordedRcon,
    redis_store: redis.StrictRedis,
    rebalance_method: str,
    immune_level: int = 0,
    immune_roles: Optional[Sequence[str]] = None,
    immune_seconds: int = 0,
    include_teamless: bool = True,
    swap_on_death: bool = False,
) -> Tuple[
    List[DetailedPlayerInfo],
    List[DetailedPlayerInfo],
    List[DetailedPlayerInfo],
    List[DetailedPlayerInfo],
    List[DetailedPlayerInfo],
    List[DetailedPlayerInfo],
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

    check_rate_limit(redis_store)

    # Only making one team_view call and passing it down to all the sub functions
    # so if one more players changes teams, roles, etc. during a balance we don't
    # end up in some weird inconsistent state

    # This does mean that a player might still be swapped or not swapped if their
    # info has changed since the request was made, but this shouldn't blow up

    team_view: RCONTeamView = rcon_hook.get_team_view_fast()

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
            message = f"Both teams were empty and `({len(teamless_players)})` teamless players aren't being considered, unable to balance."
            logger.info(message)
            audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)
            return axis_players, [], allied_players, [], teamless_players, []
        elif args.include_teamless and len(teamless_players) == 0:
            message = f"Both teams were empty and there are no teamless players, unable to balance."
            logger.info(message)
            audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)
            return axis_players, [], allied_players, [], teamless_players, []

    if len(larger_team_players) == len(smaller_team_players):
        if not args.include_teamless:
            message = f"Both teams were the same size `{len(axis_players)}`-`{len(allied_players)}` and `({len(teamless_players)})` unassigned players aren't being considered, unable to balance."
            logger.info(message)
            audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)
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
        message = "Difference between team sizes is only `1` player, unable to balance."
        logger.info(message)
        audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)

    # Use integer division so it rounds down (swaps the fewest number of people)
    # If teamless players are included any eligible teamless player is distributed
    # even if the teams are equal size
    num_players_to_switch = team_size_delta // 2

    if len(swappable_players) < num_players_to_switch:
        message = INSUFFICIENT_SWAPPABLE_PLAYERS_WARN_MSG.format(
            num_players_to_switch, (num_players_to_switch - len(swappable_players))
        )
        logger.warning(message)
        audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)

    players_to_swap: List[DetailedPlayerInfo] = []
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
    swapped_axis_players: List[DetailedPlayerInfo]
    swapped_allied_players: List[DetailedPlayerInfo]
    swapped_axis_players, swapped_allied_players = swap_players(
        rcon_hook, redis_store, players_to_swap, SWAP_TYPE_BALANCE, args.swap_on_death
    )

    # Distribute teamless players to each team, choosing which team to start with at random
    alternating_teams: Tuple[str, str] = (AXIS_TEAM, ALLIED_TEAM)
    if random.choice(alternating_teams) == ALLIED_TEAM:
        alternating_teams = (ALLIED_TEAM, AXIS_TEAM)

    teamless_players_to_swap: List[DetailedPlayerInfo] = []
    if args.include_teamless:
        teamless_players_to_swap = teamless_players
        swap_teamless_players(
            rcon_hook,
            redis_store,
            teamless_players_to_swap,
            SWAP_TYPE_BALANCE,
            swap_on_death,
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
    detailed_player_info: DetailedPlayerInfo,  # Player info from rcon.extended_commands.get_team_view()
    redis_store: redis.StrictRedis,
    immune_roles: Iterable[str],
    immune_swap_time_threshold_secs: int = 0,
    immune_level: int = 0,
) -> bool:
    """Test if a player can be swapped based on the time of their last swap, their level and role."""

    # If any of these fail we can't proceed and should abort, so not checking for missing keys
    player_name: str = detailed_player_info["name"]
    steam_id_64: str = detailed_player_info["steam_id_64"]
    level: int = detailed_player_info["level"]
    role: str = detailed_player_info["role"]

    logger.info(f"{player_name=} {role=}")

    # If they are not on a team their role defaults to rifleman
    # maybe a problem if someone immunes riflemen but wants to swap teamless players
    # TODO: Investigate

    last_swap: datetime = get_player_last_swap_timestamp(
        redis_store, steam_id_64=steam_id_64, swap_type=SWAP_TYPE_BALANCE
    )

    is_swappable = True
    not_swapped_reasons: List[str] = []

    if role in immune_roles:
        is_swappable = False
        not_swapped_reasons.append(NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG.format(role))

    if level <= immune_level:
        is_swappable = False
        not_swapped_reasons.append(
            NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG.format(level, immune_level)
        )

    seconds_since_last_swap = int(
        (datetime.now(timezone.utc) - last_swap).total_seconds()
    )
    if seconds_since_last_swap < immune_swap_time_threshold_secs:
        is_swappable = False
        not_swapped_reasons.append(
            NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG.format(
                seconds_since_last_swap, immune_swap_time_threshold_secs
            )
        )

    if not_swapped_reasons:
        message = PLAYER_BALANCE_NOT_SWAPPED_MSG.format(
            steam_id_64, player_name, ", ".join(not_swapped_reasons)
        )
        logger.warning(message)

    return is_swappable


def find_larger_team_name(team_view: RCONTeamView) -> str:
    """Return the team name of the team that has more players (axis if tied)."""
    axis_player_count = get_team_player_count(team_view, AXIS_TEAM)
    allied_player_count = get_team_player_count(team_view, ALLIED_TEAM)

    if axis_player_count >= allied_player_count:
        return AXIS_TEAM
    else:
        return ALLIED_TEAM


def select_players_arrival_time(
    players: Sequence[DetailedPlayerInfo],
    num_to_select: int,
    *,
    most_recent: bool = True,
) -> List[DetailedPlayerInfo]:
    """Select up to num_to_select players based on arrival time to the server."""
    ordered_players: List[DetailedPlayerInfo] = sorted(
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
    players: Iterable[DetailedPlayerInfo],
    immune_roles: List[str],
    immune_seconds: int,
    immune_level: int,
) -> List[DetailedPlayerInfo]:
    """Return a list of swappable players from the given list of players."""
    return [
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


if __name__ == "__main__":
    pass

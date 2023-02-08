"""For shuffling players between teams"""

import logging
import random

import redis

from rcon.recorded_commands import RecordedRcon
from rcon.team_shuffle.constants import (
    ALLIED_TEAM,
    AXIS_TEAM,
    EMPTY_TEAM,
    SHUFFLE_METHOD_PLAYER_LEVEL,
    SHUFFLE_METHOD_RANDOMLY,
    SHUFFLE_METHOD_SPLIT_SHUFFLE,
    SWAP_TYPE_SHUFFLE,
)
from rcon.team_shuffle.models import ShuffleAPIRequest, TeamShuffleConfig
from rcon.team_shuffle.utils import (
    audit,
    check_swap_rate_limit,
    get_players_on_team,
    select_players_randomly,
    swap_players,
    swap_teamless_players,
)
from rcon.types import TeamViewPlayerType, TeamViewType

logger = logging.getLogger("rcon.team_shuffle")


def shuffle_teams(
    rcon_hook: RecordedRcon,
    redis_store: redis.StrictRedis,
    config: TeamShuffleConfig,
    shuffle_method: str,
) -> tuple[
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
    list[TeamViewPlayerType],
]:
    """Shuffle teams by the given shuffle_method while maintaining even team sizes."""
    args = ShuffleAPIRequest(shuffle_method=shuffle_method)

    # raises SwapRateLimitError if conditions not met
    check_swap_rate_limit(redis_store, config.rate_limit_sec)

    team_view: TeamViewType = rcon_hook.get_team_view()

    axis_players = get_players_on_team(team_view, AXIS_TEAM)
    allied_players = get_players_on_team(team_view, ALLIED_TEAM)
    teamless_players = get_players_on_team(team_view, EMPTY_TEAM)

    all_players = axis_players + allied_players + teamless_players
    if len(all_players) == 0:
        message = "Both teams were empty, team shuffling is not possible."
        logger.info(message)
        return axis_players, [], allied_players, [], teamless_players, []

    # Randomly select which team is team one or two so we aren't always biased towards
    # shuffling extra players onto one faction
    team_one: list[TeamViewPlayerType]
    team_two: list[TeamViewPlayerType]
    if random.choice((AXIS_TEAM, ALLIED_TEAM)) == AXIS_TEAM:
        team_one, team_two = axis_players, allied_players
    else:
        team_one, team_two = allied_players, axis_players

    team_one_players_to_swap: list[TeamViewPlayerType] = []
    team_two_players_to_swap: list[TeamViewPlayerType] = []
    teamless_players_to_swap: list[TeamViewPlayerType] = teamless_players
    if args.shuffle_method == SHUFFLE_METHOD_RANDOMLY:
        (
            team_one_players_to_swap,
            team_two_players_to_swap,
        ) = find_players_to_swap_randomly(team_one, team_two)
    elif args.shuffle_method == SHUFFLE_METHOD_PLAYER_LEVEL:
        (
            team_one_players_to_swap,
            team_two_players_to_swap,
        ) = find_players_to_swap_player_level(team_one, team_two)
    elif args.shuffle_method == SHUFFLE_METHOD_SPLIT_SHUFFLE:
        (
            team_one_players_to_swap,
            team_two_players_to_swap,
        ) = find_players_to_swap_split_shuffle(team_one, team_two)

    if (
        len(
            team_one_players_to_swap
            + team_two_players_to_swap
            + teamless_players_to_swap
        )
        == 0
    ):
        # Shouldn't get here unless we have players available to shuffle but don't select them for some reason
        # This is possible (even likely) if you try to shuffle with really low player numbers
        message = "No players selected to shuffle."
        logger.info(message)
        audit(config.discord_webhook_url, message, by=config.discord_audit_service_name)

    swap_players(
        rcon_hook,
        redis_store,
        config,
        team_one_players_to_swap + team_two_players_to_swap,
        SWAP_TYPE_SHUFFLE,
    )
    swap_teamless_players(
        rcon_hook, redis_store, config, teamless_players, SWAP_TYPE_SHUFFLE
    )

    return (
        team_one,
        team_one_players_to_swap,
        team_two,
        team_two_players_to_swap,
        teamless_players,
        teamless_players_to_swap,
    )


def find_players_to_swap_split_shuffle(
    team_one: list[TeamViewPlayerType],
    team_two: list[TeamViewPlayerType],
) -> tuple[list[TeamViewPlayerType], list[TeamViewPlayerType]]:
    """Randomly swaps half of each team while maintaining even team sizes.

    Swapping half of each team is a more 'fair' shuffle than a true random shuffle
    when one team is much better than the other since it enforces half of each team
    being swapped.
    """
    team_one_num_to_swap = len(team_one) // 2
    team_two_num_to_swap = len(team_two) // 2

    # Round up odd sized teams
    if len(team_one) % 2 == 1:
        team_one_num_to_swap += 1

    if len(team_two) % 2 == 1:
        team_two_num_to_swap += 1

    team_one_to_swap = select_players_randomly(team_one, team_one_num_to_swap)

    team_two_to_swap = select_players_randomly(team_two, team_two_num_to_swap)

    return team_one_to_swap, team_two_to_swap


def find_players_to_swap_player_level(
    team_one: list[TeamViewPlayerType],
    team_two: list[TeamViewPlayerType],
) -> tuple[list[TeamViewPlayerType], list[TeamViewPlayerType]]:
    """Shuffle by level to the team with the lowest mean level while maintaining even team sizes."""
    original_team_one_players = set(player["steam_id_64"] for player in team_one)
    original_team_two_players = set(player["steam_id_64"] for player in team_two)

    all_players: list[TeamViewPlayerType] = sorted(
        team_one + team_two, key=lambda p: p["level"], reverse=True
    )

    new_team_one: list[TeamViewPlayerType] = []
    new_team_two: list[TeamViewPlayerType] = []

    # Assign the highest level player to the team with the lowest mean player level
    # Unless one team is behind a player, then the smallest team gets that player
    team_one_mean: float = 0.0
    team_two_mean: float = 0.0
    for player in all_players:
        if len(new_team_one) > len(new_team_two):
            new_team_two.append(player)
        elif len(new_team_two) > len(new_team_one):
            new_team_one.append(player)
        else:
            if team_one_mean <= team_two_mean:
                new_team_one.append(player)
            else:
                new_team_two.append(player)

        if (divisor := len(new_team_one)) == 0:
            divisor = 1

        team_one_mean = sum(player["level"] for player in new_team_one) / divisor

        if (divisor := len(new_team_two)) == 0:
            divisor = 1

        team_two_mean = sum(player["level"] for player in new_team_two) / divisor

    # Each player might already be on their 'new' team and doesn't need to be swapped
    team_one_to_swap: list[TeamViewPlayerType] = []
    team_two_to_swap: list[TeamViewPlayerType] = []
    for player in new_team_one:
        if player["steam_id_64"] not in original_team_one_players:
            team_two_to_swap.append(player)

    for player in new_team_two:
        if player["steam_id_64"] not in original_team_two_players:
            team_one_to_swap.append(player)

    return team_one_to_swap, team_two_to_swap


def find_players_to_swap_randomly(
    team_one: list[TeamViewPlayerType],
    team_two: list[TeamViewPlayerType],
) -> tuple[list[TeamViewPlayerType], list[TeamViewPlayerType]]:
    """Shuffles the entire server randomly while maintaining even team sizes."""
    original_team_one_players = set(player["steam_id_64"] for player in team_one)
    original_team_two_players = set(player["steam_id_64"] for player in team_two)

    all_players = team_one + team_two
    shuffled_players = select_players_randomly(all_players, len(all_players))

    new_team_one = shuffled_players[0 : len(shuffled_players) // 2]
    new_team_two = shuffled_players[len(shuffled_players) // 2 :]

    # Each player might already be on their 'new' team and doesn't need to be swapped
    team_one_to_swap: list[TeamViewPlayerType] = []
    team_two_to_swap: list[TeamViewPlayerType] = []
    for player in new_team_one:
        if player["steam_id_64"] not in original_team_one_players:
            team_two_to_swap.append(player)

    for player in new_team_two:
        if player["steam_id_64"] not in original_team_two_players:
            team_one_to_swap.append(player)

    return team_one_to_swap, team_two_to_swap

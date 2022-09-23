# Looking up players based on their steam ID rather than player name to handle the edge case where someone has changed their name during the current session

import logging
import pickle
import random
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

import redis

import rcon.team_autobalance.constants as constants
from rcon.cache_utils import get_redis_client
from rcon.commands import HLLServerError
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.player_history import get_player_profile
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.team_autobalance.models import AutoBalanceConfig, DetailedPlayerInfo

logger = logging.getLogger(__name__)


def get_player_name_by_steam_id_64(
    rcon_hook: RecordedRcon, steam_id_64: str
) -> Optional[str]:
    """Return the player name for the given steam_id_64 if it exists."""
    # TODO: Move this up to the RCON API layer?
    players = rcon_hook.get_playerids()
    player_name: Optional[str] = None

    try:
        player_name = [name for name, _id in players if _id == steam_id_64][0]
    except IndexError:
        logger.exception(constants.STEAM_ID_64_NOT_FOUND_ERROR_MSG.format(steam_id_64))

    return player_name


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def set_player_autobalance_timestamp(
    redis_store: redis.StrictRedis,
    time_stamp: Optional[datetime] = None,
    *,
    steam_id_64: str,
) -> None:
    """Set the given player's last autobalance swap time to the given time_stamp or current time by default."""
    redis_key = f"player_autobalance_timestamp{steam_id_64}"
    # TODO: Standardize on whatever timezone method RCON uses
    time_stamp = time_stamp or datetime.now()

    # TODO: check for failed sets
    redis_store.set(redis_key, pickle.dumps(time_stamp))


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def get_player_last_autobalance_timestamp(
    redis_store: redis.StrictRedis, *, steam_id_64: str
) -> datetime:
    """Track persistent state for the last time a player was swapped by steam_id_64."""
    # Blatantly ripped off from squad_automod.watch_state

    # TODO: Change this to a redis hash or something so we don't pollute the store with a ton of key/value pairs
    redis_key = f"player_autobalance_timestamp{steam_id_64}"

    # Use January 1st of year 1 as a sentinel date if this player hasn't been swapped before
    impossibly_old_datetime = datetime(1, 1, 1)

    # TODO: check for failed gets
    last_swap = redis_store.get(redis_key)
    if last_swap:
        last_swap = pickle.loads(last_swap)
    else:
        # Haven't seen this player before, store the sentinel value
        set_player_autobalance_timestamp(
            redis_store, time_stamp=impossibly_old_datetime, steam_id_64=steam_id_64
        )
        last_swap = impossibly_old_datetime

    return last_swap


def set_last_autobalance_timestamp(
    redis_store: redis.StrictRedis, time_stamp: datetime = None
) -> None:
    """Store the timestamp of the last time the autobalance command was ran."""
    # TODO: Pretty much duplicates the get/set player_autobalance_timestamp methods, refactor this down

    redis_key = f"player_autobalance_timestamp:last_swap"
    # TODO: Standardize on whatever timezone method RCON uses

    time_stamp = time_stamp or datetime.now()
    redis_store.set(redis_key, pickle.dumps(time_stamp))


def get_last_autobalance_timestamp(redis_store: redis.StrictRedis) -> datetime:
    """Get the timestamp of the last time the autobalance command was ran."""
    # TODO: Pretty much duplicates the get/set player_autobalance_timestamp methods, refactor this down
    redis_key = f"player_autobalance_timestamp:last_swap"

    # Use January 1st of year 1 as a sentinel date if the swap command hasn't been run before
    impossibly_old_datetime = datetime(1, 1, 1)

    last_swap = redis_store.get(redis_key)
    if last_swap:
        last_swap = pickle.loads(last_swap)
    else:
        # Haven't autobalanced before, store the sentinel value
        set_last_autobalance_timestamp(redis_store, time_stamp=impossibly_old_datetime)
        last_swap = impossibly_old_datetime

    return last_swap


def is_valid_role(role: str, valid_roles=constants.VALID_ROLES) -> bool:
    """This should never fail, including it as a sanity check."""
    if role not in valid_roles:
        logger.error(constants.INVALID_ROLE_ERROR_MSG.format(role))
        return False

    return True


# Force the steam_id_64 and player_name to be keyword only to prevent player name/steam ID confusion when calling
def get_player_role(
    rcon_hook, *, player_name: Optional[str], steam_id_64: str
) -> Optional[str]:
    """Look up a players current role given their steam_id_64 or player name."""

    player_found = False
    player_role: Optional[str] = None

    if not player_name and not steam_id_64:
        # Failed to provide a player name or steam_id_64
        logger.error(constants.NO_PLAYER_OR_STEAM_ID_64_ERROR_MSG.format(player_name))

    if steam_id_64:
        player_name = get_player_name_by_steam_id_64(rcon_hook, steam_id_64)

    try:
        detailed_player: DetailedPlayerInfo = rcon_hook.get_detailed_player_info(
            player_name
        )
        player_found = True
        player_role = detailed_player["role"]
    except HLLServerError:
        logger.exception(constants.PLAYER_NOT_FOUND_ERROR_MSG.format(player_name))

    if player_found:
        return player_role
    else:
        pass
        logger.error(
            f"Unable to determine player role for steam_id:{steam_id_64} player:{player_name}"
        )

    return None  # Make mypy happy


def is_player_swappable(
    detailed_player_info: DetailedPlayerInfo,  # Player info from rcon.extended_commands.get_team_view()
    redis_store: redis.StrictRedis,
    time_between_swaps_threshold: int = 0,
    immune_roles: Iterable[str] = None,
    immune_level: int = 0,
):
    """Test if a player can be swapped based on the time of the last swap, their level and role."""

    # If either of these fail it's a real problem, so not checking for missing keys
    player_name: str = detailed_player_info["name"]
    steam_id_64: str = detailed_player_info["steam_id_64"]

    # Should always return a valid date/time
    last_swap: datetime = get_player_last_autobalance_timestamp(
        redis_store, steam_id_64=steam_id_64
    )

    is_swappable = True

    # I don't think these two keys can ever not be in the dict?
    level: int = detailed_player_info["level"]

    # If they are not on a team this defaults to rifleman, maybe a problem if someone immunes riflemen
    # but wants to swap teamless players
    role: str = detailed_player_info["role"]

    not_swapped_reasons: List[str] = []

    if role in immune_roles:
        is_swappable = False
        not_swapped_reasons.append(
            constants.NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG.format(role)
        )

    if level < immune_level:
        is_swappable = False
        not_swapped_reasons.append(
            constants.NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG.format(level, immune_level)
        )

    seconds_since_last_swap = int((datetime.now() - last_swap).total_seconds())
    if seconds_since_last_swap < time_between_swaps_threshold:
        is_swappable = False
        not_swapped_reasons.append(
            constants.NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG.format(
                seconds_since_last_swap, time_between_swaps_threshold
            )
        )

    if not_swapped_reasons:
        logger.warning(
            f"steam_id: {steam_id_64} player: {player_name} not swapped due to: {' '.join(not_swapped_reasons)}"
        )

    return is_swappable


def get_team_player_count(team_view, team_name: str) -> int:
    """Return the number of players on the specified team."""
    # TODO: Move this up to the RCON API layer?
    player_count: int = 0

    # Skip using .get() here because of the nested dicts
    # Will blow up if we pass in an invalid team name of course
    # I don't think this should ever fail though even if the teams are empty
    try:
        player_count = team_view[team_name]["count"]
    except KeyError:
        pass

    return player_count


def is_min_player_count_exceeded(
    team_view, min_count: int = 0, include_teamless_players: bool = False
) -> bool:
    """Return the total number of players on both teams, plus teamless players if chosen."""
    total = get_team_player_count(
        team_view, constants.AXIS_TEAM
    ) + get_team_player_count(team_view, constants.ALLIED_TEAM)

    if include_teamless_players:
        total += get_team_player_count(team_view, constants.EMPTY_TEAM)

    return total > min_count


def is_time_between_autobalances_exceeded(
    redis_store: redis.StrictRedis, min_time_seconds: int
) -> Tuple[bool, int]:
    """Test if the number of seconds since the last swap was attempted is larger than our configured minimum and also return the number of seconds since the last balance."""
    # This only knows the time of the last time a swap was attempted and possible, if it was attempted but failed due to other conditions the time never updates
    # This should be fine since I included the time between auto balances in case someone gets click happy in the rcon gui and if the balance attempt fails for some other reason the result is the same

    last_swap = get_last_autobalance_timestamp(redis_store)
    time_delta = int((datetime.now() - last_swap).total_seconds())

    return (time_delta > min_time_seconds), time_delta


def is_team_player_delta_exceeded(team_view, threshold: int = 0) -> bool:
    """Test if the player number difference between teams exceeds (not inclusive) the given threshold."""

    # Shouldn't need to use .get() here, I don't think this can ever fail
    axis_team_count = get_team_player_count(team_view, constants.AXIS_TEAM)
    allied_team_count = get_team_player_count(team_view, constants.ALLIED_TEAM)

    delta = abs(axis_team_count - allied_team_count)

    return delta > threshold


def find_larger_team_name(team_view) -> str:
    """Return the team name of the team that has more players (axis if tied)."""
    axis_player_count = get_team_player_count(team_view, constants.AXIS_TEAM)
    allied_player_count = get_team_player_count(team_view, constants.ALLIED_TEAM)

    if axis_player_count >= allied_player_count:
        return constants.AXIS_TEAM
    else:
        return constants.ALLIED_TEAM


def get_players_on_team(
    rcon_hook: RecordedRcon, team_name: str
) -> List[DetailedPlayerInfo]:
    """Return a list of detailed_player_info results for all the players on the given team name"""

    # Getting inconsistent results when using team_view
    all_players = rcon_hook.get_playerids()

    team_players: List[DetailedPlayerInfo] = []
    for name, steam_id_64 in all_players:
        player: DetailedPlayerInfo = rcon_hook.get_detailed_player_info(name)
        if player["team"] == team_name:
            team_players.append(player)

    return team_players


def select_players_randomly(players: Iterable[DetailedPlayerInfo], num_to_select: int):
    """Select up to num_to_select players randomly from the given list of players"""
    shuffled_players = players[:]
    random.shuffle(shuffled_players)

    # If we don't have enough possible players to swap, use as many as possible
    if num_to_select > len(shuffled_players):
        logger.warning(
            f"Tried to swap {num_to_select} players, was only able to swap {len(shuffled_players)} players"
        )

        return shuffled_players

    # Otherwise grab only the desired number of players
    return shuffled_players[0:num_to_select]


# Force the selection method to be keyword only to avoid confusion when calling
def select_players_arrival_time(
    players: Iterable[DetailedPlayerInfo],
    num_to_select: int,
    *,
    most_recent: bool = True,
):
    # returns DetailedPlayerInfo but augmented with their most recent session
    """Select up to num_to_select players based on arrival time to the server."""

    # TODO: Should probably move this to the DB layer

    player_sessions = {
        p["steam_id_64"]: get_player_profile(p["steam_id_64"], 1) for p in players
    }

    # Update each DetailedPlayerInfo player to include their most recent session
    for p in players:
        p["history"] = player_sessions[p["steam_id_64"]]

    ordered_players = sorted(
        players,
        key=lambda p: p["history"]["sessions"][0]["start"],
        reverse=most_recent,
    )

    # If we don't have enough possible players to swap, use as many as possible
    if num_to_select > len(ordered_players):
        delta = num_to_select - len(ordered_players)
        logger.warning(
            f"Tried to swap {num_to_select} players, was only able to swap {delta} players"
        )
        return ordered_players

    # Otherwise grab only the desired number of players
    return ordered_players[0:num_to_select]


def autobalance_teams(rcon_hook: RecordedRcon):
    """Verify if criteria for autobalancing has been met and then swap players."""
    try:
        config = get_config()
        config = AutoBalanceConfig(**config[constants.AUTOBALANCE_CONFIG_KEY])
    except Exception:
        logger.exception(constants.INVALID_CONFIG_ERROR_MSG)
        raise

    redis_store = get_redis_client()
    team_view = rcon_hook.get_team_view_fast()

    audit(config, "Attempting to autobalance")

    # Should not need to check for empty teams, should be covered by the config setting `min_players_for_balance`
    autobalance_possible = True
    not_balanceable_reasons = []

    # Does the server exceed the minimum player count for balancing?
    if not is_min_player_count_exceeded(
        team_view,
        min_count=config.min_players_for_balance,
        include_teamless_players=config.include_teamless_players,
    ):
        autobalance_possible = False
        not_balanceable_reasons.append(
            f"Minimum player count of {config.min_players_for_balance} was not exceeded."
        )

    # Is the player count difference large enough to trigger balancing?
    if not is_team_player_delta_exceeded(
        team_view, threshold=config.player_count_threshold
    ):
        autobalance_possible = False
        # TODO: pull this up to the top as a constant
        not_balanceable_reasons.append(
            f"Difference between team players of {config.player_count_threshold} was not exceeded."
        )

    (
        min_time_since_last_swap_exceeded,
        seconds_since_last_swap,
    ) = is_time_between_autobalances_exceeded(
        redis_store, config.min_seconds_between_team_balances
    )
    if not min_time_since_last_swap_exceeded:
        autobalance_possible = False
        # TODO: pull this up to the top as a constant
        not_balanceable_reasons.append(
            f"{seconds_since_last_swap} seconds since last swap was attempted does not exceed the minimum time of {config.min_seconds_between_team_balances} seconds."
        )

    if autobalance_possible:
        # Time to autobalance some players!
        audit(config, "Autobalance starting")

        # Only update the time autobalance was run if it's possible to swap players
        set_last_autobalance_timestamp(redis_store)

        larger_team_name = find_larger_team_name(team_view)
        smaller_team_name = (
            constants.ALLIED_TEAM
            if larger_team_name == constants.AXIS_TEAM
            else constants.AXIS_TEAM
        )

        larger_team_players = get_players_on_team(rcon_hook, larger_team_name)
        swappable_players = [
            player
            for player in larger_team_players
            if is_player_swappable(
                player,
                redis_store,
                config.min_seconds_between_player_swaps,
                config.immuned_roles,
                config.immuned_level_up_to,
            )
        ]

        # Shouldn't need to use the absolute value here or check for no difference since we've determined the larger team
        team_size_delta = get_team_player_count(
            team_view, larger_team_name
        ) - get_team_player_count(team_view, smaller_team_name)

        # Use integer division so it rounds down (swaps the fewest number of people)
        num_players_to_switch = team_size_delta // 2

        num_swappable_players = len(swappable_players)
        if num_swappable_players < num_players_to_switch:
            # TODO: pull this up to the top as a constant
            logger.warning(
                f"Only {num_swappable_players} players are currently swappable, missing {num_players_to_switch-num_swappable_players} players."
            )

        if config.auto_rebalance_method == "random":
            players_to_swap = select_players_randomly(
                swappable_players, num_players_to_switch
            )
        elif config.auto_rebalance_method == "arrival_most_recent":
            players_to_swap = select_players_arrival_time(
                swappable_players, num_players_to_switch, most_recent=True
            )
        elif config.auto_rebalance_method == "arrival_least_recent":
            players_to_swap = select_players_arrival_time(
                swappable_players, num_players_to_switch, most_recent=False
            )
        else:
            # Should never happen unless config.yml is wrong
            logger.warning(
                constants.INVALID_BALANCE_METHOD_ERROR_MSG.format(
                    config.auto_rebalance_method
                )
            )
            raise ValueError(
                constants.INVALID_BALANCE_METHOD_ERROR_MSG.format(
                    config.auto_rebalance_method
                )
            )

        # Perform a swap action on each selected player
        switch_function = (
            rcon_hook.do_switch_player_on_death
            if config.swap_on_death
            else rcon_hook.do_switch_player_now
        )
        for player in players_to_swap:
            switch_function(
                player["name"], None
            )  # this function has a unused 'by' argument
            set_player_autobalance_timestamp(
                redis_store, steam_id_64=player["steam_id_64"]
            )

            if config.swap_on_death:
                switch_type = "on death"
            else:
                switch_type = "immediately"

            audit(config, f"Swapping {player['name']} {switch_type}")
            logger.info(
                f"player {player['name']}/{player['steam_id_64']} was autobalanced ({switch_type})."
            )

    else:
        logger.warning(
            f"Autobalance was attempted but not possible: {', '.join(not_balanceable_reasons)}"
        )


# Snagged right out of squad_automod, did not test it as I don't have a discord set up
def audit(cfg: AutoBalanceConfig, msg: str):
    webhook_url = None
    if cfg.discord_webhook_url is not None and cfg.discord_webhook_url != "":
        webhook_url = cfg.discord_webhook_url
        send_to_discord_audit(
            msg, by="TeamAutoBalance", webhookurl=webhook_url, silent=False
        )


def run():
    rcon_hook = RecordedRcon(SERVER_INFO)
    autobalance_teams(rcon_hook)


if __name__ == "__main__":
    pass

# When configured and enabled team auto balance should automatically move players to even them
#
# Looking up players based on their steam ID rather than player name to handle the edge case where someone has changed their name during the current session

import logging
import pickle
from datetime import datetime
from pprint import pprint
from typing import Iterable, List, Tuple

import redis
from rcon.cache_utils import get_redis_client
from rcon.commands import HLLServerError
from rcon.config import get_config
from rcon.player_history import get_player
from rcon.recorded_commands import RecordedRcon
from rcon.squad_automod.automod import _get_team_count
from rcon.team_autobalance.models import AutoBalanceConfig

# TODO: Move these to some shared constants file
AXIS_TEAM = "axis"
ALLIED_TEAM = "allies"

EMPTY_TEAM = "none"

AUTOBALANCE_CONFIG_KEY = "TEAM_AUTOBALANCE"

# TODO: put all these error messages in one container
INVALID_CONFIG_ERROR_MSG = (
    f"Invalid {AUTOBALANCE_CONFIG_KEY} check your config/config.yml"
)
INVALID_ROLE_ERROR_MSG = "{0} is not a valid role."
PLAYER_NOT_FOUND_ERROR_MSG = "{0} was not found."
STEAM_ID_64_NOT_FOUND_ERROR_MSG = "{0} was not found."
NO_PLAYER_OR_STEAM_ID_64_ERROR_MSG = "Failed to provide a player name or steam_id_64"
AUTOBALANCE_DISABLED_MSG = "Team auto-balancing is disabled."
NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG = "player is below immune level (%0)"
NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG = "player is playing an immune role (%0)"
NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG = (
    "player was swapped too recently (%0) seconds ago."
)
VALID_ROLES = (
    "armycommander",
    "tankcommander",
    "crewman",
    "spotter",
    "sniper",
    "officer",
    "rifleman",
    "assault",
    "automaticrifleman",
    "medic",
    "support",
    "heavymachinegunner",
    "antitank",
    "engineer",
)
VALID_TEAMS = (AXIS_TEAM, ALLIED_TEAM)


logger = logging.getLogger(__name__)


def get_player_name_by_steam_id_64(rcon: RecordedRcon, steam_id_64: str) -> str:
    """Return the player name for the given steam_id_64."""
    # TODO: Move this up to the RCON API layer?
    players = rcon.get_playerids()
    player_name: str = None

    try:
        player_name = [name for name, _id in players if _id == steam_id_64][0]
    except IndexError:
        logger.exception(STEAM_ID_64_NOT_FOUND_ERROR_MSG.format(steam_id_64))

    return player_name


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def set_player_autobalance_timestamp(
    redis_store: redis.StrictRedis, *, time_stamp=None, steam_id_64: str
):
    """Set the given player's last autobalance swap time to the given time_stamp or current time by default."""
    redis_key = f"player_autobalance_timestamp{steam_id_64}"
    # TODO: Standardize on whatever timezone method RCON uses
    time_stamp = time_stamp or datetime.now()
    redis_store.set(redis_key, pickle.dumps(time_stamp))


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def get_player_last_autobalance_timestamp(
    redis_store: redis.StrictRedis, *, steam_id_64: str
):
    """Track persistent state for the last time a player was swapped by steam_id_64."""
    # Blatantly ripped off from squad_automod.watch_state

    # TODO: Change this to a redis hash so we don't pollute the store
    redis_key = f"player_autobalance_timestamp{steam_id_64}"

    # Use January 1st of year 1 as a sentinel date if this player hasn't been swapped before
    impossibly_old_datetime = datetime(1, 1, 1)

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


def is_valid_role(role: str, valid_roles=VALID_ROLES) -> bool:
    """This should never fail, including it as a sanity check."""
    if role not in valid_roles:
        logger.exception(INVALID_ROLE_ERROR_MSG.format(role))
        return False

    return True


def get_player_role(rcon, *player_name: str, steam_id_64: str) -> str:
    """Look up a players current role given their steam_id_64 or player name."""

    player_found = False
    player_role = None

    if not player_name and not steam_id_64:
        # Failed to provide a player name or steam_id_64
        logger.error(NO_PLAYER_OR_STEAM_ID_64_ERROR_MSG.format(player_name))

    if steam_id_64:
        player_name = get_player_name_by_steam_id_64(rcon, steam_id_64)

    try:
        detailed_player = rcon.get_detailed_player_info(player_name)
        player_found = True
        player_role = detailed_player["role"]
    except HLLServerError:
        logger.exception(PLAYER_NOT_FOUND_ERROR_MSG.format(player_name))

    if player_found:
        return player_role
    else:
        pass
        logger.error(
            f"Unable to determine player role for steam_id:{steam_id_64} player:{player_name}"
        )


def is_player_swappable(
    detailed_player_info,  # Player info from rcon.extended_commands.get_team_view()
    redis_store,
    time_between_swaps_threshold: int = 0,
    immune_roles: Iterable[str] = None,
    immune_level: int = 0,
):
    """Test if a player can be swapped based on the time of the last swap, their level and role."""

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
    # # but wants to swap teamless players
    role: str = detailed_player_info["role"]

    not_swapped_reasons: list[str] = []
    if level < immune_level:
        is_swappable = False
        not_swapped_reasons.append(NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG.format(level))

    if role in immune_roles:
        is_swappable = False
        not_swapped_reasons.append(NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG.format(role))

    if not is_swappable:
        for reason in not_swapped_reasons:
            logger.debug(reason)

    seconds_since_last_swap = (datetime.now() - last_swap).seconds

    if seconds_since_last_swap < time_between_swaps_threshold:
        is_swappable = False
        not_swapped_reasons.append(
            NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG.format(seconds_since_last_swap)
        )

    logger.warning(
        f"steam_id: {steam_id_64} player: {player_name} not swapped due to: {' '.join(not_swapped_reasons)}"
    )

    return is_swappable


def get_team_player_count(team_view, team_name: str) -> int:
    """Return the number of players on the specified team."""
    # TODO: Move this up to the RCON API layer?
    player_count = 0

    # Skip using .get() here because of the nested dicts
    try:
        player_count = team_view[team_name]["count"]
    except KeyError:
        pass

    return player_count


def is_min_player_count_exceeded(
    team_view, min_count: int = 0, include_teamless_players: bool = False
) -> bool:
    """Return the total number of players on both teams, plus teamless players if chosen."""
    total = get_team_player_count(team_view, AXIS_TEAM) + get_team_player_count(
        team_view, ALLIED_TEAM
    )

    if include_teamless_players:
        total += get_team_player_count(team_view, EMPTY_TEAM)

    return total > min_count


def is_team_player_delta_exceeded(team_view, threshold: int = 0) -> bool:
    """Test if the player number difference between teams exceeds (not inclusive) the given threshold."""

    # Shouldn't need to use .get() here, I don't think this can ever fail
    axis_team_count = get_team_player_count(team_view, AXIS_TEAM)
    allied_team_count = get_team_player_count(team_view, ALLIED_TEAM)

    delta = abs(axis_team_count - allied_team_count)

    return delta > threshold


def find_larger_team_name(team_view) -> str:
    """Return the team name of the team that has more players (axis if tied)."""
    axis_player_count = get_team_player_count(team_view, AXIS_TEAM)
    allied_player_count = get_team_player_count(team_view, ALLIED_TEAM)

    if axis_player_count >= allied_player_count:
        return AXIS_TEAM
    else:
        return ALLIED_TEAM


def get_players_on_team(team) -> List[Tuple[str, str]]:
    squads = [team["squads"][squad] for squad in team.get("squads", dict).keys()]
    players: List[Tuple[str, str]] = [
        player for squad in squads for player in squad["players"]
    ]

    return players


def select_players_randomly(players, num_to_select):
    pass


# Force the selection method to be keyword only to avoid confusion when calling
def select_players_arrival_time(players, num_to_select, *, most_recent=True):
    """Select num_to_select players based on arrival time to the server."""

    # Looks like we can rely on snagging the first session start time
    # to find when they most recently joined the server

    # print(f"{len(players)} players are swappable.")
    # print(f"looking to swap {num_to_select} players.")

    pprint(players)

    # TODO: Should probably move this to the DB layer
    ordered_players = sorted(
        players,
        key=lambda p: p["profile"]["sessions"][0]["start"],
        reverse=not most_recent,
    )

    # print("*****")
    # pprint(ordered_players[0])

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
        config = AutoBalanceConfig(**config[AUTOBALANCE_CONFIG_KEY])
    except Exception:
        logger.exception(INVALID_CONFIG_ERROR_MSG)
        raise

    # Is auto balancing turned on?
    if not config.enabled:
        logger.debug(AUTOBALANCE_DISABLED_MSG)
        return

    redis_store = get_redis_client()
    team_view = rcon_hook.get_team_view_fast()

    # Does the server exceed the minimum player count for balancing?
    # Is the player count difference large enough to trigger balancing?
    autobalance_possible = True
    not_balanceable_reasons = []

    if not is_min_player_count_exceeded(
        team_view,
        min_count=config.min_players_for_balance,
        include_teamless_players=config.include_teamless_players,
    ):
        autobalance_possible = False
        not_balanceable_reasons.append(
            f"Minimum player count of {config.min_players_for_balance} was not exceeded."
        )

    if not is_team_player_delta_exceeded(
        team_view, threshold=config.player_count_threshold
    ):
        autobalance_possible = False
        not_balanceable_reasons.append(
            f"Difference between team players of {config.player_count_threshold} was not exceeded."
        )

    if autobalance_possible:
        # Time to autobalance some players!
        larger_team_name = find_larger_team_name(team_view)
        smaller_team_name = ALLIED_TEAM if larger_team_name == AXIS_TEAM else AXIS_TEAM

        larger_team = team_view.get(larger_team_name, dict)
        smaller_team = team_view.get(smaller_team_name, dict)

        larger_team_players = get_players_on_team(larger_team)
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

        # Shouldn't need to use the absolute value here or check for no difference
        team_size_delta = get_team_player_count(
            team_view, larger_team_name
        ) - get_team_player_count(team_view, smaller_team_name)
        num_players_to_switch = team_size_delta // 2

        # If we can't make the teams an even number, preference the team that was smaller originally
        # TODO: make this an config.yml option
        if team_size_delta % 2 == 1:
            num_players_to_switch += 1

        num_swappable_players = len(swappable_players)
        if num_swappable_players < num_players_to_switch:
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
                f"{config.auto_rebalance_method} is not a valid rebalance method."
            )
            # TODO: not sure we want an exception here?
            raise ValueError(
                f"{config.auto_rebalance_method} is not a valid rebalance method."
            )

        # Perform a swap action on each selected player
        switch_function = (
            rcon_hook.do_switch_player_on_death
            if config.swap_on_death
            else rcon_hook.do_switch_player_now
        )
        for player in players_to_swap:
            switch_function(player["name"])
            logger.info(
                f"player {player['name']}/{player['steam_id_64']} was autobalanced."
            )

    else:
        logger.warning(
            f"Autobalance was attempted but not possible: {' '.join(not_balanceable_reasons)}"
        )


def run():
    pass


if __name__ == "__main__":
    pass

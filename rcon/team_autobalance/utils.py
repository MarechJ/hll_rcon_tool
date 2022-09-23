import logging
import pickle
from datetime import datetime
from typing import Optional, List

import redis

from rcon.recorded_commands import RecordedRcon
import rcon.team_autobalance.constants as constants
from rcon.team_autobalance.models import DetailedPlayerInfo
from rcon.commands import HLLServerError


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


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def set_player_swap_timestamp(
    redis_store: redis.StrictRedis,
    time_stamp: Optional[datetime] = None,
    *,
    steam_id_64: str,
    swap: str,
) -> None:
    """Set the given player's last autobalance swap time to the given time_stamp or current time by default."""
    if swap not in constants.SWAP_TYPES:
        raise ValueError(f"Invalid swap type for redis key {swap}")

    redis_key = f"player_balance_timestamp:{swap}:{steam_id_64}"
    # TODO: Standardize on whatever timezone method RCON uses
    time_stamp = time_stamp or datetime.now()

    # TODO: check for failed sets
    redis_store.set(redis_key, pickle.dumps(time_stamp))


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def get_player_last_swap_timestamp(
    redis_store: redis.StrictRedis, *, steam_id_64: str, swap: str
) -> datetime:
    """Track persistent state for the last time a player was swapped by steam_id_64."""
    # Blatantly ripped off from squad_automod.watch_state
    if swap not in constants.SWAP_TYPES:
        raise ValueError(f"Invalid swap type for redis key {swap}")

    # TODO: Change this to a redis hash or something so we don't pollute the store with a ton of key/value pairs
    redis_key = f"player_balance_timestamp{swap}:{steam_id_64}"

    # Use January 1st of year 1 as a sentinel date if this player hasn't been swapped before
    impossibly_old_datetime = datetime(1, 1, 1)

    # TODO: check for failed gets
    last_swap = redis_store.get(redis_key)
    if last_swap:
        last_swap = pickle.loads(last_swap)
    else:
        # Haven't seen this player before, store the sentinel value
        set_player_swap_timestamp(
            redis_store,
            time_stamp=impossibly_old_datetime,
            steam_id_64=steam_id_64,
            swap=swap,
        )
        last_swap = impossibly_old_datetime

    return last_swap

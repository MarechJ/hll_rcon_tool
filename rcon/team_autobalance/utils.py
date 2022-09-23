import logging
from typing import Optional, List

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

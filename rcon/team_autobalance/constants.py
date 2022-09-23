# TODO: Move these to some shared constants file
AXIS_TEAM = "axis"
ALLIED_TEAM = "allies"

EMPTY_TEAM = "none"

AUTOBALANCE_CONFIG_KEY = "TEAM_AUTOBALANCE"

SWAP_TYPE_BALANCE = "balance"
SWAP_TYPE_SHUFFLE = "shuffle"
SWAP_TYPES = (SWAP_TYPE_SHUFFLE, SWAP_TYPE_BALANCE)

# TODO: put all these error messages in one container
INVALID_CONFIG_ERROR_MSG = (
    f"Invalid {AUTOBALANCE_CONFIG_KEY} check your config/config.yml"
)
INVALID_ROLE_ERROR_MSG = "{0} is not a valid role."
INVALID_BALANCE_METHOD_ERROR_MSG = "{0} is not a valid rebalance method."
PLAYER_NOT_FOUND_ERROR_MSG = "{0} was not found."
STEAM_ID_64_NOT_FOUND_ERROR_MSG = "{0} was not found."
NO_PLAYER_OR_STEAM_ID_64_ERROR_MSG = "Failed to provide a player name or steam_id_64"
AUTOBALANCE_DISABLED_MSG = "Team auto-balancing is disabled."
NOT_SWAPPED_TOO_RECENT_ERROR_MSG = "player was swapped {0} seconds ago"
NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG = "player level {0} is below immune level of {1}"
NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG = "player is playing an immune role {0}"
NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG = (
    "player was swapped too recently {0} seconds ago, configured limit is {1} seconds."
)

TEAM_NAME_NOT_FOUND_ERROR_MSG = "{0} was not a valid team name."
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

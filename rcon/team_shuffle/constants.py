from typing import Final

API_COMMAND_EVEN_TEAM_SIZES: Final = "do_even_teams"
API_COMMAND_SHUFFLE: Final = "do_shuffle_teams"
REDIS_PLAYER_KEY: Final = "player_shuffle_timestamp:{0}"
REDIS_TEAM_SHUFFLE_KEY: Final = "player_shuffle_timestamp:rate_limit"

# Team Names
AXIS_TEAM: Final = "axis"
ALLIED_TEAM: Final = "allies"
EMPTY_TEAM: Final = "none"

# Swap Types
SWAP_TYPE_EVEN_TEAMS: Final = "even_teams"
SWAP_TYPE_SHUFFLE: Final = "shuffle"
SWAP_TYPES: Final = (SWAP_TYPE_SHUFFLE, SWAP_TYPE_EVEN_TEAMS)

EVEN_TEAMS_METHODS: Final = ("arrival_most_recent", "arrival_least_recent", "random")

# Random: Every player has an equal chance of being shuffle
# Split shuffle: Shuffle half of each time
# Player level: 'Even' division of players by level between teams
SHUFFLE_METHOD_RANDOMLY: Final = "random_shuffle"
SHUFFLE_METHOD_PLAYER_LEVEL: Final = "player_level"
SHUFFLE_METHOD_SPLIT_SHUFFLE: Final = "split_shuffle"
SHUFFLE_METHODS: Final = (
    SHUFFLE_METHOD_RANDOMLY,
    SHUFFLE_METHOD_SPLIT_SHUFFLE,
    SHUFFLE_METHOD_PLAYER_LEVEL,
)

# Error messages


UNABLE_TO_SET_REDIS_KEY_ERROR_MSG: Final = "Unable to set Redis key: {0}"
COMMAND_FAILED_ERROR_MSG = "{0} FAILED. (Check your server logs for more details)."

INVALID_SWAP_TYPE_ERROR_MSG: Final = "Invalid swap type for redis key {0}."
INVALID_EVEN_TEAMS_METHOD_ERROR_MSG: Final = "{0} is not a valid even_teams method."
INVALID_SHUFFLE_METHOD_ERROR_MSG: Final = "{0} is not a valid shuffle method."

# Info Messages
SWAP_SUCCESSFUL_MSG: Final = "{0} SUCCESSFUL. {1} of {2} Axis players swapped {3} of {4} Allied players swapped {5} of {6} teamless players swapped."

VALID_ROLES: Final = (
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

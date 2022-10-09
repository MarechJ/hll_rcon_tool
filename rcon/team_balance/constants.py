import os
from typing import Final

API_COMMAND_BALANCE: Final = "do_balance_teams"
API_COMMAND_SHUFFLE: Final = "do_shuffle_teams"
REDIS_PLAYER_KEY: Final = "player_balance_timestamp:{0}"
REDIS_BALANCE_KEY: Final = "player_balance_timestamp:rate_limit"
DISCORD_BALANCE_SHUFFLE_WEBHOOK: Final = os.getenv("DISCORD_BALANCE_SHUFFLE_WEBHOOK")
RCON_TEAM_SWAP_DELAY_MS: Final = 0
# TODO: Better in a config file
TEAM_BALANCE_RATE_LIMIT_SEC: Final = 5

# Team Names
AXIS_TEAM: Final = "axis"
ALLIED_TEAM: Final = "allies"
EMPTY_TEAM: Final = "none"

# Swap Types
SWAP_TYPE_BALANCE: Final = "balance"
SWAP_TYPE_SHUFFLE: Final = "shuffle"
SWAP_TYPES: Final = (SWAP_TYPE_SHUFFLE, SWAP_TYPE_BALANCE)

SWAP_ON_DEATH_DESCRIPTION: Final = "on death"
SWAP_IMMEDIATELY_DESCRIPTION: Final = "immediately"

BALANCE_METHODS: Final = ("arrival_most_recent", "arrival_least_recent", "random")

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
BALANCE_RATE_LIMIT_EXCEEDED_ERROR_MSG = (
    "Balance/Shuffle attempted {0} seconds ago, configured limit is {1} seconds."
)
RCON_SWAP_FAILED_ERROR_MSG: Final = (
    "Game server failed to swap player `{0}` (`{1}`/`{2}`)."
)
UNABLE_TO_SET_REDIS_KEY_ERROR_MSG: Final = "Unable to set Redis key: {0}"
COMMAND_FAILED_ERROR_MSG = "{0} FAILED. (Check your server logs for more details)."

INVALID_SWAP_TYPE_ERROR_MSG: Final = "Invalid swap type for redis key {0}."
INVALID_ROLE_ERROR_MSG: Final = "{0} is not a valid role."
INVALID_BALANCE_METHOD_ERROR_MSG: Final = "{0} is not a valid rebalance method."
INVALID_SHUFFLE_METHOD_ERROR_MSG: Final = "{0} is not a valid shuffle method."
# NO_PLAYER_OR_STEAM_ID_64_ERROR_MSG: Final = (
#     "Failed to provide a player name or steam_id_64."
# )
NOT_SWAPPED_IMMUNE_LEVEL_ERROR_MSG: Final = (
    "player level {0} is below immune level of {1}"
)
NOT_SWAPPED_IMMUNE_ROLE_ERROR_MSG: Final = "player is playing an immune role ({0})"
NOT_SWAPPED_SWAPPED_RECENTLY_ERROR_MSG: Final = (
    "player was swapped too recently {0} seconds ago, configured limit is {1} seconds"
)
# Warning Messages
INSUFFICIENT_SWAPPABLE_PLAYERS_WARN_MSG: Final = (
    "Only `{0}` players are currently swappable, missing `{1}` players."
)

# Info Messages
PLAYER_BALANCE_SWAP_MSG: Final = (
    "player `{0}` (`{1}`/`{2}`) was balanced `{1}` > `{3}` ({4})."
)
PLAYER_SHUFFLE_SWAP_MSG: Final = "player `{0}` (`{1}/{2}`) was shuffled `{1}` > `{3}`."
PLAYER_BALANCE_NOT_SWAPPED_MSG: Final = (
    "steam_id: `{0}` player: `{1}` not balanced due to: `{2}`."
)
EMPTY_TEAMS_MSG: Final = "Both teams were empty, no `{0}` possible."
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

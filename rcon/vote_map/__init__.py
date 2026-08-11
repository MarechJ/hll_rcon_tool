"""Public API for the votemap package.

Imports are lazy so cache migrations can import ``vote_map.storage`` without
loading the RCON, database, and user-configuration layers.
"""

from importlib import import_module
from typing import Any

_PUBLIC_SYMBOLS = {
    "ActionOutcome": ("rcon.vote_map.service", "ActionOutcome"),
    "ActionResult": ("rcon.vote_map.service", "ActionResult"),
    "InvalidMapParam": ("rcon.vote_map.exceptions", "InvalidMapParam"),
    "InvalidVoteError": ("rcon.vote_map.exceptions", "InvalidVoteError"),
    "MapSelectionBuilder": ("rcon.vote_map.selection", "MapSelectionBuilder"),
    "MapSelectionCriteria": ("rcon.vote_map.selection", "MapSelectionCriteria"),
    "PlayerChoiceNotAllowed": (
        "rcon.vote_map.exceptions",
        "PlayerChoiceNotAllowed",
    ),
    "PlayerNotFound": ("rcon.vote_map.exceptions", "PlayerNotFound"),
    "PlayerVoteNotAllowed": ("rcon.vote_map.exceptions", "PlayerVoteNotAllowed"),
    "RestrictiveFilterError": (
        "rcon.vote_map.exceptions",
        "RestrictiveFilterError",
    ),
    "SelectionLimitExceeded": (
        "rcon.vote_map.exceptions",
        "SelectionLimitExceeded",
    ),
    "VoteMap": ("rcon.vote_map.service", "VoteMap"),
    "VoteMapCommandHandler": ("rcon.vote_map.service", "VoteMapCommandHandler"),
    "VoteMapException": ("rcon.vote_map.exceptions", "VoteMapException"),
    "VoteMapNoInitialised": (
        "rcon.vote_map.exceptions",
        "VoteMapNoInitialised",
    ),
    "VoteMapUserConfig": ("rcon.user_config.vote_map", "VoteMapUserConfig"),
    "VotemapPermissions": ("rcon.vote_map.service", "VotemapPermissions"),
    "VotemapState": ("rcon.vote_map.state", "VotemapState"),
    "validate_maps": ("rcon.vote_map.service", "validate_maps"),
}

__all__ = list(_PUBLIC_SYMBOLS)


def __getattr__(name: str) -> Any:
    try:
        module_name, symbol_name = _PUBLIC_SYMBOLS[name]
    except KeyError as error:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from error

    value = getattr(import_module(module_name), symbol_name)
    globals()[name] = value
    return value

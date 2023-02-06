from typing import Any, Dict, NewType, Optional, Sequence

from pydantic import BaseModel, conint, validator

from rcon.team_shuffle.constants import (
    BALANCE_METHODS,
    INVALID_BALANCE_METHOD_ERROR_MSG,
    INVALID_ROLE_ERROR_MSG,
    INVALID_SHUFFLE_METHOD_ERROR_MSG,
    SHUFFLE_METHODS,
    VALID_ROLES,
)


class SwapRateLimitError(BaseException):
    pass


class ShuffleAPIRequest(BaseModel):
    shuffle_method: str

    @validator("shuffle_method")
    def only_valid_shuffle_methods(cls, v):
        if v not in SHUFFLE_METHODS:
            raise ValueError(INVALID_SHUFFLE_METHOD_ERROR_MSG.format(v))

        return v


class BalanceAPIRequest(BaseModel):
    rebalance_method: str
    immune_level: conint(ge=0, le=500)
    immune_roles: list[str] | None = []
    immune_seconds: conint(ge=0)
    include_teamless: bool
    swap_on_death: bool

    @validator("rebalance_method")
    def only_valid_balance_methods(cls, v):
        if v not in BALANCE_METHODS:
            raise ValueError(INVALID_BALANCE_METHOD_ERROR_MSG.format(v))

        return v

    @validator("immune_roles")
    def only_valid_roles(cls, v):
        if not v:
            return tuple()

        for role in v:
            if role not in VALID_ROLES:
                raise ValueError(INVALID_ROLE_ERROR_MSG.format(role))

        return v


DetailedPlayerInfo = NewType("DetailedPlayerInfo", Dict[str, Any])
"""
        rcon.extended_commands.get_detailed_player_info()

        Name: T17 Scott
        steamID64: 01234567890123456
        Team: Allies            # "None" when not in team
        Role: Officer
        Unit: 0 - Able          # Absent when not in unit
        Loadout: NCO            # Absent when not in team
        Kills: 0 - Deaths: 0
        Score: C 50, O 0, D 40, S 10
        Level: 34

        """

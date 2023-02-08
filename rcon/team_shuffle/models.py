from pydantic import BaseModel, conint, validator

from rcon.team_shuffle.constants import (
    EVEN_TEAMS_METHODS,
    INVALID_EVEN_TEAMS_METHOD_ERROR_MSG,
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
        if v not in EVEN_TEAMS_METHODS:
            raise ValueError(INVALID_EVEN_TEAMS_METHOD_ERROR_MSG.format(v))

        return v

    @validator("immune_roles")
    def only_valid_roles(cls, v):
        if not v:
            return tuple()

        for role in v:
            if role not in VALID_ROLES:
                raise ValueError(f"{role} is not a valid role.")

        return v


class TeamShuffleConfig(BaseModel):
    rate_limit_sec: int
    discord_webhook_url: str
    discord_audit_swaps: bool
    discord_audit_service_name: str
    even_teams_swap_message: str
    team_shuffle_swap_message: str
    swap_on_death_description: str
    swap_immediately_description: str
    even_teams_logger_message: str
    shuffle_teams_logger_message: str
    failed_swap_logger_message: str

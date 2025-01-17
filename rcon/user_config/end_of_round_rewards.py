from datetime import timedelta
from logging import getLogger
from typing import TypedDict
from typing_extensions import Annotated

import pydantic
from pydantic import Field, AfterValidator

import discord

logger = getLogger(__name__)

from rcon.user_config.utils import BaseUserConfig, _listType, key_check, set_user_config
from rcon.user_config.webhooks import DiscordWebhook, WebhookType
from rcon.user_config.seed_vip import (
    Reward,
    RewardTimeFrame,
    RawRewardTimeFrameType,
    RawRewardType,
)
from rcon.types import Roles
import tokenize
import ast
from functools import cached_property

# all top N per team? make it configurable

# top N roles
# top N score category
# top N kills
# top N squads

# command to view current top

# TODO: extract these out into constants
ALLOWED_VARIABLES = set(
    [
        "kills",
        "kills_streak",
        "deaths",
        "deaths_streak",
        "deaths_without_kill_streak",
        "teamkills",
        "teamkills_streak",
        "deaths_by_tk",
        "deaths_by_tk_streak",
        "nb_vote_started",
        "nb_voted_yes",
        "nb_voted_no",
        "longest_life_secs",
        "shortest_life_secs",
        "combat",
        "offense",
        "defense",
        "support",
        "kills_per_minute",
        "deaths_per_minute",
        "kill_death_ratio",
    ]
)

ALLOWED_TOKENS = ALLOWED_VARIABLES | set(
    [
        "+",
        "-",
        "*",
        "/",
        "%",
        "(",
        ")",
        "",  # Will always appear in the token list
    ]
)


def validate_formula(value: str, allowed_tokens: set[str] = ALLOWED_TOKENS) -> str:
    """Check the given formula for syntax validity and safety (only allowed tokens)"""

    value = "".join(value.split()).lower()

    # If Python can parse it, it has valid syntax
    ast.parse(value)

    # Strip out any non allowed operators/variables so it is safe to eval()
    tokens = list(tokenize.generate_tokens(iter([value]).__next__))
    for token in tokens:
        if token.string not in allowed_tokens and not token.string.isdigit():
            raise ValueError(f"Invalid token: {token.string}")

    return value


class RoleReward(pydantic.BaseModel):
    roles: list[Roles] = Field(default_factory=list)
    top_n: int = Field(default=3)
    formula: Annotated[str, AfterValidator(validate_formula)] = Field(min_length=1)
    reward: Reward = Field(default_factory=Reward)
    reward_message: str = Field(default="")

    @cached_property
    def substituable_formula(self):
        tokens = list(tokenize.generate_tokens(iter([self.formula]).__next__))
        processed_tokens: list[str] = []

        for token in tokens:
            if token.string in ALLOWED_VARIABLES:
                processed_tokens.append("{" + token.string + "}")
            else:
                processed_tokens.append(token.string)

        return "".join(processed_tokens)


class EndOfRoundRewardsUserConfig(BaseUserConfig):
    # TODO: set this to false
    enabled: bool = Field(default=True)
    role_rewards: list[RoleReward] = Field(default_factory=list)


a = RoleReward(formula="offense + defense * 3 + support / 4", reward_message="")

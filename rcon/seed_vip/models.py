from datetime import datetime, timedelta
from logging import getLogger

import pydantic

from rcon.maps import Layer

logger = getLogger(__name__)


class BaseCondition(pydantic.BaseModel):
    def is_met(self):
        raise NotImplementedError


class PlayerCountCondition(BaseCondition):
    faction: str
    min_players: int = pydantic.Field(ge=0, le=50)
    max_players: int = pydantic.Field(ge=0, le=50)

    current_players: int = pydantic.Field(ge=0, le=50)

    def is_met(self):
        return self.min_players <= self.current_players <= self.max_players


class PlayTimeCondition(BaseCondition):
    # This is constrained on the user config side
    min_time_secs: int = pydantic.Field()
    # This should be constrained to ge=0 but CRCON will sometimes
    # report players with negative play time
    current_time_secs: int = pydantic.Field()

    def is_met(self):
        return self.current_time_secs >= self.min_time_secs


class GameState(pydantic.BaseModel):
    num_allied_players: int
    num_axis_players: int
    allied_score: int
    axis_score: int
    raw_time_remaining: str
    time_remaining: timedelta
    current_map: Layer
    next_map: Layer


class Player(pydantic.BaseModel):
    name: str
    player_id: str
    current_playtime_seconds: int


class VipPlayer(pydantic.BaseModel):
    player: Player
    expiration_date: datetime | None


class ServerPopulation(pydantic.BaseModel):
    players: dict[str, Player]

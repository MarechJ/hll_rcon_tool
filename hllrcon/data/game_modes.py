# ruff: noqa: N802

from enum import StrEnum

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    class_cached_property,
)


class GameModeScale(StrEnum):
    LARGE = "large"
    SMALL = "small"


class GameMode(CaseInsensitiveIndexedBaseModel):
    scale: GameModeScale

    def is_large(self) -> bool:
        return self.scale == GameModeScale.LARGE

    def is_small(self) -> bool:
        return self.scale == GameModeScale.SMALL

    @class_cached_property
    @classmethod
    def WARFARE(cls) -> "GameMode":
        return cls(id="warfare", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def OFFENSIVE(cls) -> "GameMode":
        return cls(id="offensive", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def SKIRMISH(cls) -> "GameMode":
        return cls(id="skirmish", scale=GameModeScale.SMALL)

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from rcon.maps import GameMode, Layer, Map, Team
from rcon.types import GameEnum
from rcon.weapons import WeaponType


@dataclass(frozen=True)
class GameProfile:
    """Game-specific reference data and parsing behind a stable interface."""

    game: GameEnum
    maps: Mapping[str, Map]
    layers: Mapping[str, Layer]
    layer_parser: Callable[[str | Layer], Layer]
    roles: frozenset[str] = field(default_factory=frozenset)
    role_labels: Mapping[str, str] = field(default_factory=dict)
    weapons: Mapping[str, WeaponType] = field(default_factory=dict)
    weapon_sides: Mapping[str, Team] = field(default_factory=dict)
    supported_game_modes: frozenset[GameMode] = field(default_factory=frozenset)

    def parse_layer(self, layer_name: str | Layer) -> Layer:
        return self.layer_parser(layer_name)

    def parse_layer_or_unknown(self, layer_name: str | Layer) -> Layer:
        try:
            return self.parse_layer(layer_name)
        except (KeyError, TypeError, ValueError):
            return self.layers["unknown"]

    def parse_game_mode(self, game_mode: str | GameMode) -> GameMode:
        # HLL Vietnam prefixes offensive modes with the attacking faction,
        # e.g. "US Offensive" / "NVA Offensive". Every GameMode value is a
        # single word, so match on the final token.
        mode = (
            game_mode
            if isinstance(game_mode, GameMode)
            else GameMode(game_mode.strip().lower().rsplit(None, 1)[-1])
        )
        if mode not in self.supported_game_modes:
            raise ValueError(
                f"Game mode {mode.value!r} is not supported by the '{self.game.value}' game profile"
            )
        return mode

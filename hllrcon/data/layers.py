# mypy: disable-error-code="prop-decorator"
# ruff: noqa: N802

import re
from enum import StrEnum
from functools import cached_property

from pydantic import computed_field

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    class_cached_property,
)
from .factions import Faction
from .game_modes import GameMode
from .maps import Map, Orientation, Sector, Sectors, Strongpoint
from .teams import Team

__all__ = (
    "Layer",
    "TimeOfDay",
    "Weather",
)


RE_LAYER_NAME_SMALL = re.compile(
    r"^(?P<tag>[A-Z]{3,5})_S_(?P<year>\d{4})_(?:(?P<environment>\w+)_)?P_(?P<game_mode>\w+)$",
)
RE_LAYER_NAME_LARGE = re.compile(
    r"^(?P<tag>[A-Z]{3,5})_L_(?P<year>\d{4})_(?P<game_mode>\w+?)(?P<attackers>[A-Z]\w*?)?(?:_(?P<environment>\w+))?$",
)
RE_LEGACY_LAYER_NAME = re.compile(
    r"^(?P<name>[a-z0-9]+)_(?P<game_mode>(?!off)[a-z]+)(?:_V2)?(?:_(?P<environment>[a-z]+))?$",
)
RE_LEGACY_LAYER_NAME_OFFENSIVE = re.compile(
    r"^(?P<name>[a-z0-9]+)_(?P<game_mode>off(?:ensive)?)_?(?P<attackers>[a-zA-Z]+)(?:_(?P<environment>\w+))?$",
)


class TimeOfDay(StrEnum):
    DAWN = "dawn"
    DAY = "day"
    DUSK = "dusk"
    NIGHT = "night"


class Weather(StrEnum):
    CLEAR = "clear"
    OVERCAST = "overcast"
    RAIN = "rain"
    SNOW = "snow"


LAYER_GAME_MODE_MAP: dict[str, GameMode] = {
    "warfare": GameMode.WARFARE,
    "offensive": GameMode.OFFENSIVE,
    "off": GameMode.OFFENSIVE,
    "skirmish": GameMode.SKIRMISH,
}

LAYER_ATTACKERS_MAP: dict[str, Faction] = {
    "us": Faction.US,
    "ger": Faction.GER,
    "dak": Faction.DAK,
    "sov": Faction.SOV,
    "soviet": Faction.SOV,
    "rus": Faction.SOV,
    "russian": Faction.SOV,
    "ussr": Faction.SOV,
    "cw": Faction.CW,
    "gb": Faction.CW,
    "com": Faction.CW,
    "brit": Faction.CW,
    "british": Faction.CW,
    "b8a": Faction.CW,
}

LAYER_ENVIRONMENT_MAP: dict[str, tuple[TimeOfDay, Weather]] = {
    "day": (TimeOfDay.DAY, Weather.CLEAR),
    "dawn": (TimeOfDay.DAWN, Weather.CLEAR),
    "morning": (TimeOfDay.DAWN, Weather.CLEAR),
    "dusk": (TimeOfDay.DUSK, Weather.CLEAR),
    "evening": (TimeOfDay.DUSK, Weather.CLEAR),
    "night": (TimeOfDay.NIGHT, Weather.CLEAR),
    "clear": (TimeOfDay.DAY, Weather.CLEAR),
    "overcast": (TimeOfDay.DAY, Weather.OVERCAST),
    "rain": (TimeOfDay.DAY, Weather.RAIN),
    "snow": (TimeOfDay.DAY, Weather.SNOW),
}


class Layer(CaseInsensitiveIndexedBaseModel):
    map: Map
    game_mode: GameMode
    time_of_day: TimeOfDay
    weather: Weather
    attacking_team: Team | None = None

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id!r}, map={self.map!r},"
            f" attackers={self.attacking_team!r}, time_of_day={self.time_of_day!r},"
            f" weather={self.weather!r})"
        )

    def __hash__(self) -> int:
        return hash(self.id.lower())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Layer, str)):
            return str(self).lower() == str(other).lower()
        return NotImplemented

    @classmethod
    def _parse_id(cls, id_: str) -> "Layer":
        exc = ValueError(f"Could not parse layer ID: {id_}")

        for pattern in (
            RE_LAYER_NAME_SMALL,
            RE_LAYER_NAME_LARGE,
            RE_LEGACY_LAYER_NAME,
            RE_LEGACY_LAYER_NAME_OFFENSIVE,
        ):
            if match := pattern.match(id_):
                break
        else:
            raise exc

        groups = match.groupdict("")

        map_id: str
        map_tag: str
        if groups.get("name"):
            map_id = groups["name"]
            map_tag = groups.get("tag") or map_id[:3].upper()
        elif groups.get("tag"):
            map_id = groups["tag"]
            map_tag = map_id
        else:  # pragma: no cover
            raise exc

        game_mode = LAYER_GAME_MODE_MAP.get(groups["game_mode"].lower())
        if game_mode is None:
            raise exc

        if groups.get("attackers"):
            attackers = LAYER_ATTACKERS_MAP.get(groups["attackers"].lower())
        else:
            attackers = None

        time_of_day, weather = LAYER_ENVIRONMENT_MAP.get(
            groups["environment"].lower(),
            (TimeOfDay.DAY, Weather.CLEAR),
        )

        try:
            map_ = Map.by_id(map_id)
        except ValueError:
            map_ = Map(
                id=map_id,
                name=map_id.capitalize(),
                pretty_name=map_id.capitalize(),
                short_name=map_id.capitalize(),
                tag=map_tag,
                allies=(
                    attackers
                    if attackers and attackers.team == Team.ALLIES
                    else Faction.US
                ),
                axis=(
                    attackers
                    if attackers and attackers.team == Team.AXIS
                    else Faction.GER
                ),
                orientation=Orientation.HORIZONTAL,
                sectors=Sectors(
                    Sector(
                        Strongpoint(name="Sector 1"),
                        Strongpoint(name="Sector 1"),
                        Strongpoint(name="Sector 1"),
                    ),
                    Sector(
                        Strongpoint(name="Sector 2"),
                        Strongpoint(name="Sector 2"),
                        Strongpoint(name="Sector 2"),
                    ),
                    Sector(
                        Strongpoint(name="Sector 3"),
                        Strongpoint(name="Sector 3"),
                        Strongpoint(name="Sector 3"),
                    ),
                    Sector(
                        Strongpoint(name="Sector 4"),
                        Strongpoint(name="Sector 4"),
                        Strongpoint(name="Sector 4"),
                    ),
                    Sector(
                        Strongpoint(name="Sector 5"),
                        Strongpoint(name="Sector 5"),
                        Strongpoint(name="Sector 5"),
                    ),
                ),
                mirror_factions=False,
            )

        return Layer(
            id=id_,
            map=map_,
            game_mode=game_mode,
            time_of_day=time_of_day,
            weather=weather,
            attacking_team=attackers.team if attackers else None,
        )

    @classmethod
    def by_id(cls, id_: str, *, strict: bool = True) -> "Layer":
        """Look up a layer by its identifier.

        Parameters
        ----------
        id_ : str
            The identifier of the layer to look up.
        strict : bool, optional
            Whether to raise an exception if no such layer is known. If set to `False`,
            will attempt to generate a fallback value based on the ID. By default
            `True`.

        Returns
        -------
        Layer
            The layer with the given identifier.

        Raises
        ------
        ValueError
            If no layer with the given identifier exists.
        ValueError
            No reasonable fallback value could be generated.

        """
        try:
            return super().by_id(id_)
        except ValueError:
            if strict:
                raise

            return cls._parse_id(id_)

    @computed_field
    @cached_property
    def pretty_name(self) -> str:
        out = self.map.pretty_name
        if self.game_mode == GameMode.OFFENSIVE:
            out += " Off."
            if self.attacking_faction:
                out += f" {self.attacking_faction.short_name}"
        else:
            out += f" {self.game_mode.id.capitalize()}"

        environment: list[str] = []

        if self.time_of_day != TimeOfDay.DAY:
            environment.append(self.time_of_day.value.title())
        if self.weather != Weather.CLEAR:
            environment.append(self.weather.value.title())

        if environment:
            out += f" ({', '.join(environment)})"

        return out

    @computed_field
    @cached_property
    def attacking_faction(self) -> Faction | None:
        if self.attacking_team == Team.ALLIES:
            return self.map.allies
        if self.attacking_team == Team.AXIS:
            return self.map.axis
        return None

    @computed_field
    @cached_property
    def defending_team(self) -> Team | None:
        if self.attacking_team == Team.ALLIES:
            return Team.AXIS
        if self.attacking_team == Team.AXIS:
            return Team.ALLIES
        return None

    @computed_field
    @cached_property
    def defending_faction(self) -> Faction | None:
        if self.attacking_team == Team.ALLIES:
            return self.map.axis
        if self.attacking_team == Team.AXIS:
            return self.map.allies
        return None

    @class_cached_property
    @classmethod
    def SME_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="stmereeglise_warfare",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="stmereeglise_warfare_night",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="stmereeglise_offensive_us",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def SME_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="stmereeglise_offensive_ger",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def SME_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="SME_S_1944_Day_P_Skirmish",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="SME_S_1944_Morning_P_Skirmish",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="SME_S_1944_Night_P_Skirmish",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="stmariedumont_warfare",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="stmariedumont_warfare_night",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="stmariedumont_off_us",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def SMDM_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="stmariedumont_off_ger",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def UTAH_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="utahbeach_warfare",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def UTAH_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="utahbeach_warfare_night",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def UTAH_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="utahbeach_offensive_us",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def UTAH_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="utahbeach_offensive_ger",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def OMAHA_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="omahabeach_warfare",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def OMAHA_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="omahabeach_warfare_night",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def OMAHA_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="omahabeach_offensive_us",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def OMAHA_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="omahabeach_offensive_ger",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def PHL_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_Warfare",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def PHL_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_Warfare_Night",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def PHL_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_OffensiveUS",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def PHL_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_OffensiveGER",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def PHL_SKIRMISH_RAIN(cls) -> "Layer":
        return cls(
            id="PHL_S_1944_Rain_P_Skirmish",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.RAIN,
        )

    @class_cached_property
    @classmethod
    def PHL_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="PHL_S_1944_Morning_P_Skirmish",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def PHL_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="PHL_S_1944_Night_P_Skirmish",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_WARFARE(cls) -> "Layer":
        return cls(
            id="carentan_warfare",
            map=Map.CARENTAN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="carentan_warfare_night",
            map=Map.CARENTAN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="carentan_offensive_us",
            map=Map.CARENTAN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="carentan_offensive_ger",
            map=Map.CARENTAN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="CAR_S_1944_Day_P_Skirmish",
            map=Map.CARENTAN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_SKIRMISH_RAIN(cls) -> "Layer":
        return cls(
            id="CAR_S_1944_Rain_P_Skirmish",
            map=Map.CARENTAN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.RAIN,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="CAR_S_1944_Dusk_P_Skirmish",
            map=Map.CARENTAN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="hurtgenforest_warfare_V2",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="hurtgenforest_warfare_V2_night",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="hurtgenforest_offensive_US",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="hurtgenforest_offensive_ger",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def HILL400_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="hill400_warfare",
            map=Map.HILL_400,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="hill400_warfare_night",
            map=Map.HILL_400,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="hill400_offensive_US",
            map=Map.HILL_400,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def HILL400_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="hill400_offensive_ger",
            map=Map.HILL_400,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def HILL400_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="HIL_S_1944_Day_P_Skirmish",
            map=Map.HILL_400,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="HIL_S_1944_Dusk_P_Skirmish",
            map=Map.HILL_400,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="HIL_S_1944_Night_P_Skirmish",
            map=Map.HILL_400,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="foy_warfare",
            map=Map.FOY,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="foy_warfare_night",
            map=Map.FOY,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="foy_offensive_us",
            map=Map.FOY,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def FOY_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="foy_offensive_ger",
            map=Map.FOY,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def FOY_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="FOY_S_1944_P_Skirmish",
            map=Map.FOY,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="FOY_S_1944_Night_P_Skirmish",
            map=Map.FOY,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KURSK_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="kursk_warfare",
            map=Map.KURSK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KURSK_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="kursk_warfare_night",
            map=Map.KURSK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KURSK_OFFENSIVE_SOV_DAY(cls) -> "Layer":
        return cls(
            id="kursk_offensive_rus",
            map=Map.KURSK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def KURSK_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="kursk_offensive_ger",
            map=Map.KURSK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="stalingrad_warfare",
            map=Map.STALINGRAD,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="stalingrad_warfare_night",
            map=Map.STALINGRAD,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_OFFENSIVE_SOV_DAY(cls) -> "Layer":
        return cls(
            id="stalingrad_offensive_rus",
            map=Map.STALINGRAD,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="stalingrad_offensive_ger",
            map=Map.STALINGRAD,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="remagen_warfare",
            map=Map.REMAGEN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="remagen_warfare_night",
            map=Map.REMAGEN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="remagen_offensive_us",
            map=Map.REMAGEN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="remagen_offensive_ger",
            map=Map.REMAGEN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="kharkov_warfare",
            map=Map.KHARKOV,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="kharkov_warfare_night",
            map=Map.KHARKOV,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_OFFENSIVE_SOV_DAY(cls) -> "Layer":
        return cls(
            id="kharkov_offensive_rus",
            map=Map.KHARKOV,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="kharkov_offensive_ger",
            map=Map.KHARKOV,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="KHA_S_1944_P_Skirmish",
            map=Map.KHARKOV,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="KHA_S_1944_Night_P_Skirmish",
            map=Map.KHARKOV,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="driel_warfare",
            map=Map.DRIEL,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="driel_warfare_night",
            map=Map.DRIEL,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_OFFENSIVE_CW_DAY(cls) -> "Layer":
        return cls(
            id="driel_offensive_us",
            map=Map.DRIEL,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def DRIEL_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="driel_offensive_ger",
            map=Map.DRIEL,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def DRIEL_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="DRL_S_1944_P_Skirmish",
            map=Map.DRIEL,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="DRL_S_1944_Night_P_Skirmish",
            map=Map.DRIEL,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="DRL_S_1944_Day_P_Skirmish",
            map=Map.DRIEL,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="elalamein_warfare",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="elalamein_warfare_night",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_OFFENSIVE_B8A_DAY(cls) -> "Layer":
        return cls(
            id="elalamein_offensive_CW",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_OFFENSIVE_DAK_DAY(cls) -> "Layer":
        return cls(
            id="elalamein_offensive_ger",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="ELA_S_1942_P_Skirmish",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="ELA_S_1942_Night_P_Skirmish",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="SMDM_S_1944_Day_P_Skirmish",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="SMDM_S_1944_Night_P_Skirmish",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_SKIRMISH_RAIN(cls) -> "Layer":
        return cls(
            id="SMDM_S_1944_Rain_P_Skirmish",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.RAIN,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="mortain_warfare_day",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_warfare_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_warfare_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_warfare_night",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_day",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_night",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_day",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_night",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_day",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_night",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_warfare_day",
            map=Map.TOBRUK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_warfare_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_WARFARE_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_warfare_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_B8A_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_offensivebritish_day",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_DAK_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_offensiveger_day",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_B8A_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_offensivebritish_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_DAK_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_offensiveger_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_B8A_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_offensivebritish_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_DAK_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_offensiveger_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_skirmish_day",
            map=Map.TOBRUK,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_skirmish_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_skirmish_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

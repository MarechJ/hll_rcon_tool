import re
from enum import Enum
from logging import getLogger
from typing import TYPE_CHECKING, Any, Iterable, Literal, Sequence, Union

import pydantic
import typing_extensions
from requests.structures import CaseInsensitiveDict
from typing_extensions import Literal

logger = getLogger(__name__)

RE_LAYER_NAME = re.compile(
    r"^(?P<tag>[A-Z]{3,5})_(?P<size>S|L)_(?P<year>\d{4})_(?:(?P<environment>\w+)_)?P_(?P<game_mode>\w+)$"
)
RE_LEGACY_LAYER_NAME = re.compile(
    r"^(?P<name>[a-z0-9]+)_(?:(?P<offensive>off(?:ensive)?)_?(?P<attackers>[a-zA-Z]+)|(?P<game_mode>[a-z]+)(?:_V2)?)(?:_(?P<environment>[a-z]+))?$"
)

UNKNOWN_MODE = "unknown"
UNKNOWN_MAP_NAME = "unknown"
UNKNOWN_MAP_TAG = "UNK"


# TypedDicts to represent the serialized output from the API and
# pydantic model dumps to python dicts
class MapType(typing_extensions.TypedDict):
    id: str
    name: str
    tag: str
    pretty_name: str
    shortname: str
    allies: "Faction"
    axis: "Faction"


class LayerType(typing_extensions.TypedDict):
    id: str
    map: MapType
    game_mode: str
    attackers: str | None
    environment: str
    pretty_name: str
    image_name: str
    image_url: str | None


class FactionType(typing_extensions.TypedDict):
    name: str
    team: str


# Sourced with some minor modifications from https://github.com/timraay/Gamewatch/blob/master/


# These pydantic models/enums can easily be copied in whole when writing Python code that
# interacts with the CRCON API and enables much easier parsing of results
# for example where result is a plain python dictionary containing a serialized Layer:
# Layer.model_validate(result)
class GameMode(str, Enum):
    WARFARE = "warfare"
    OFFENSIVE = "offensive"
    CONTROL = "control"
    PHASED = "phased"
    MAJORITY = "majority"

    @classmethod
    def large(cls):
        return (
            cls.WARFARE,
            cls.OFFENSIVE,
        )

    @classmethod
    def small(cls):
        return (
            cls.CONTROL,
            cls.PHASED,
            cls.MAJORITY,
        )

    def is_large(self):
        return self in GameMode.large()

    def is_small(self):
        return self in GameMode.small()


class Team(str, Enum):
    ALLIES = "allies"
    AXIS = "axis"


class Environment(str, Enum):
    DAWN = "dawn"
    DAY = "day"
    DUSK = "dusk"
    NIGHT = "night"
    OVERCAST = "overcast"
    RAIN = "rain"


class FactionName(Enum):
    CW = "cw"
    GB = "gb"
    GER = "ger"
    RUS = "rus"
    US = "us"


class Faction(pydantic.BaseModel):
    name: str
    team: Team


class Map(pydantic.BaseModel):
    id: str
    name: str
    tag: str
    pretty_name: str
    shortname: str
    allies: "Faction"
    axis: "Faction"

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, (Map, str)):
            return str(self) == str(other)
        return NotImplemented


class Layer(pydantic.BaseModel):
    id: str
    map: Map
    game_mode: GameMode
    attackers: Union[Team, None] = None
    environment: Environment = Environment.DAY

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"{self.__class__}(id={self.id}, map={self.map}, attackers={self.attackers}, environment={self.environment})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, (Layer, str)):
            return str(self) == str(other)
        return NotImplemented

    if TYPE_CHECKING:
        # Ensure type checkers see the correct return type
        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
        ) -> LayerType: ...

    else:

        def model_dump(self, **kwargs):
            return super().model_dump(**kwargs)

    @property
    def attacking_faction(self):
        if self.attackers == Team.ALLIES:
            return self.map.allies
        elif self.attackers == Team.AXIS:
            return self.map.axis
        return None

    @pydantic.computed_field
    @property
    def pretty_name(self) -> str:
        out = self.map.pretty_name
        if self.game_mode == GameMode.OFFENSIVE:
            out += " Off."
            if self.attackers and self.attacking_faction:
                out += f" {self.attacking_faction.name.upper()}"
        elif self.game_mode.is_small():
            # TODO: Remove once more Skirmish modes release
            out += " Skirmish"
        else:
            out += f" {self.game_mode.value.capitalize()}"
        if self.environment != Environment.DAY:
            out += f" ({self.environment.value.title()})"
        return out

    @property
    def opposite_side(self) -> Literal[Team.AXIS, Team.ALLIES] | None:
        if self.attackers:
            return get_opposite_side(self.attackers)

    @pydantic.computed_field
    @property
    def image_name(self) -> str:
        return f"{self.map.id}-{self.environment.value}.webp".lower()


MAPS = {
    m.id: m
    for m in (
        Map(
            id=UNKNOWN_MAP_NAME,
            name=UNKNOWN_MAP_NAME,
            tag="",
            pretty_name=UNKNOWN_MAP_NAME,
            shortname=UNKNOWN_MAP_NAME,
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="stmereeglise",
            name="SAINTE-MÈRE-ÉGLISE",
            tag="SME",
            pretty_name="St. Mere Eglise",
            shortname="SME",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="stmariedumont",
            name="ST MARIE DU MONT",
            tag="BRC",
            pretty_name="St. Marie Du Mont",
            shortname="SMDM",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="utahbeach",
            name="UTAH BEACH",
            tag="UTA",
            pretty_name="Utah Beach",
            shortname="Utah",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="omahabeach",
            name="OMAHA BEACH",
            tag="OMA",
            pretty_name="Omaha Beach",
            shortname="Omaha",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="purpleheartlane",
            name="PURPLE HEART LANE",
            tag="PHL",
            pretty_name="Purple Heart Lane",
            shortname="PHL",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="carentan",
            name="CARENTAN",
            tag="CAR",
            pretty_name="Carentan",
            shortname="Carentan",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="hurtgenforest",
            name="HÜRTGEN FOREST",
            tag="HUR",
            pretty_name="Hurtgen Forest",
            shortname="Hurtgen",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="hill400",
            name="HILL 400",
            tag="HIL",
            pretty_name="Hill 400",
            shortname="Hill 400",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="foy",
            name="FOY",
            tag="FOY",
            pretty_name="Foy",
            shortname="Foy",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="kursk",
            name="KURSK",
            tag="KUR",
            pretty_name="Kursk",
            shortname="Kursk",
            allies=Faction(name=FactionName.RUS.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="stalingrad",
            name="STALINGRAD",
            tag="STA",
            pretty_name="Stalingrad",
            shortname="Stalingrad",
            allies=Faction(name=FactionName.RUS.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="remagen",
            name="REMAGEN",
            tag="REM",
            pretty_name="Remagen",
            shortname="Remagen",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="kharkov",
            name="Kharkov",
            tag="KHA",
            pretty_name="Kharkov",
            shortname="Kharkov",
            allies=Faction(name=FactionName.RUS.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="driel",
            name="DRIEL",
            tag="DRL",
            pretty_name="Driel",
            shortname="Driel",
            allies=Faction(name=FactionName.GB.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="elalamein",
            name="EL ALAMEIN",
            tag="ELA",
            pretty_name="El Alamein",
            shortname="Alamein",
            allies=Faction(name=FactionName.GB.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
        Map(
            id="mortain",
            name="MORTAIN",
            tag="MOR",
            pretty_name="Mortain",
            shortname="MOR",
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        ),
    )
}

LAYERS = {
    l.id: l
    for l in (
        # In older versions (prior to v9.8.0) map names could be recorded as bla_
        # if the map name could not be retrieved from the game server
        Layer(id="bla_", map=MAPS[UNKNOWN_MAP_NAME], game_mode=GameMode.WARFARE),
        Layer(
            id=UNKNOWN_MAP_NAME, map=MAPS[UNKNOWN_MAP_NAME], game_mode=GameMode.WARFARE
        ),
        Layer(
            id="stmereeglise_warfare",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="stmereeglise_warfare_night",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="stmereeglise_offensive_us",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="stmereeglise_offensive_ger",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="SME_S_1944_Day_P_Skirmish",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DAY,
        ),
        Layer(
            id="SME_S_1944_Morning_P_Skirmish",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DAWN,
        ),
        Layer(
            id="SME_S_1944_Night_P_Skirmish",
            map=MAPS["stmereeglise"],
            game_mode=GameMode.CONTROL,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="stmariedumont_warfare",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="stmariedumont_warfare_night",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="stmariedumont_off_us",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="stmariedumont_off_ger",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="utahbeach_warfare",
            map=MAPS["utahbeach"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="utahbeach_warfare_night",
            map=MAPS["utahbeach"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="utahbeach_offensive_us",
            map=MAPS["utahbeach"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="utahbeach_offensive_ger",
            map=MAPS["utahbeach"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="omahabeach_warfare",
            map=MAPS["omahabeach"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="omahabeach_warfare_night",
            map=MAPS["omahabeach"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="omahabeach_offensive_us",
            map=MAPS["omahabeach"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="omahabeach_offensive_ger",
            map=MAPS["omahabeach"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="purpleheartlane_warfare",
            map=MAPS["purpleheartlane"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="purpleheartlane_warfare_night",
            map=MAPS["purpleheartlane"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="purpleheartlane_offensive_us",
            map=MAPS["purpleheartlane"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="purpleheartlane_offensive_ger",
            map=MAPS["purpleheartlane"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="carentan_warfare",
            map=MAPS["carentan"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="carentan_warfare_night",
            map=MAPS["carentan"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="carentan_offensive_us",
            map=MAPS["carentan"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="carentan_offensive_ger",
            map=MAPS["carentan"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="CAR_S_1944_Day_P_Skirmish",
            map=MAPS["carentan"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DAY,
        ),
        Layer(
            id="CAR_S_1944_Rain_P_Skirmish",
            map=MAPS["carentan"],
            game_mode=GameMode.CONTROL,
            environment=Environment.RAIN,
        ),
        Layer(
            id="CAR_S_1944_Dusk_P_Skirmish",
            map=MAPS["carentan"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DUSK,
        ),
        Layer(
            id="hurtgenforest_warfare_V2",
            map=MAPS["hurtgenforest"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="hurtgenforest_warfare_V2_night",
            map=MAPS["hurtgenforest"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="hurtgenforest_offensive_US",
            map=MAPS["hurtgenforest"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="hurtgenforest_offensive_ger",
            map=MAPS["hurtgenforest"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="hill400_warfare",
            map=MAPS["hill400"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="hill400_warfare_night",
            map=MAPS["hill400"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="hill400_offensive_US",
            map=MAPS["hill400"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="hill400_offensive_ger",
            map=MAPS["hill400"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="foy_warfare",
            map=MAPS["foy"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="foy_warfare_night",
            map=MAPS["foy"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="foy_offensive_us",
            map=MAPS["foy"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="foy_offensive_ger",
            map=MAPS["foy"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="kursk_warfare",
            map=MAPS["kursk"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="kursk_warfare_night",
            map=MAPS["kursk"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="kursk_offensive_rus",
            map=MAPS["kursk"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="kursk_offensive_ger",
            map=MAPS["kursk"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="stalingrad_warfare",
            map=MAPS["stalingrad"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="stalingrad_warfare_night",
            map=MAPS["stalingrad"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="stalingrad_offensive_rus",
            map=MAPS["stalingrad"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="stalingrad_offensive_ger",
            map=MAPS["stalingrad"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="remagen_warfare",
            map=MAPS["remagen"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="remagen_warfare_night",
            map=MAPS["remagen"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="remagen_offensive_us",
            map=MAPS["remagen"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="remagen_offensive_ger",
            map=MAPS["remagen"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="kharkov_warfare",
            map=MAPS["kharkov"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="kharkov_warfare_night",
            map=MAPS["kharkov"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="kharkov_offensive_rus",
            map=MAPS["kharkov"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="kharkov_offensive_ger",
            map=MAPS["kharkov"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="driel_warfare",
            map=MAPS["driel"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="driel_warfare_night",
            map=MAPS["driel"],
            game_mode=GameMode.WARFARE,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="driel_offensive_us",
            map=MAPS["driel"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="driel_offensive_ger",
            map=MAPS["driel"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="DRL_S_1944_P_Skirmish",
            map=MAPS["driel"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DAWN,
        ),
        Layer(
            id="DRL_S_1944_Night_P_Skirmish",
            map=MAPS["driel"],
            game_mode=GameMode.CONTROL,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="DRL_S_1944_Day_P_Skirmish",
            map=MAPS["driel"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DAY,
        ),
        Layer(
            id="elalamein_warfare",
            map=MAPS["elalamein"],
            game_mode=GameMode.WARFARE,
        ),
        Layer(
            id="elalamein_warfare_night",
            map=MAPS["elalamein"],
            game_mode=GameMode.WARFARE,
            environment=Environment.DUSK,
        ),
        Layer(
            id="elalamein_offensive_CW",
            map=MAPS["elalamein"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="elalamein_offensive_ger",
            map=MAPS["elalamein"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="ELA_S_1942_P_Skirmish",
            map=MAPS["elalamein"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DAY,
        ),
        Layer(
            id="ELA_S_1942_Night_P_Skirmish",
            map=MAPS["elalamein"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DUSK,
        ),
        Layer(
            id="SMDM_S_1944_Day_P_Skirmish",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.CONTROL,
        ),
        Layer(
            id="SMDM_S_1944_Night_P_Skirmish",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.CONTROL,
            environment=Environment.NIGHT,
        ),
        Layer(
            id="SMDM_S_1944_Rain_P_Skirmish",
            map=MAPS["stmariedumont"],
            game_mode=GameMode.CONTROL,
            environment=Environment.RAIN,
        ),
        Layer(
            id="mortain_warfare_day", map=MAPS["mortain"], game_mode=GameMode.WARFARE
        ),
        Layer(
            id="mortain_warfare_evening",
            map=MAPS["mortain"],
            game_mode=GameMode.WARFARE,
            environment=Environment.DUSK,
        ),
        Layer(
            id="mortain_warfare_overcast",
            map=MAPS["mortain"],
            game_mode=GameMode.WARFARE,
            environment=Environment.OVERCAST,
        ),
        Layer(
            id="mortain_offensiveUS_day",
            map=MAPS["mortain"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
        ),
        Layer(
            id="mortain_offensiveUS_overcast",
            map=MAPS["mortain"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
            environment=Environment.OVERCAST,
        ),
        Layer(
            id="mortain_offensiveUS_evening",
            map=MAPS["mortain"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.ALLIES,
            environment=Environment.DUSK,
        ),
        Layer(
            id="mortain_offensiveger_day",
            map=MAPS["mortain"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
        ),
        Layer(
            id="mortain_offensiveger_overcast",
            map=MAPS["mortain"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
            environment=Environment.OVERCAST,
        ),
        Layer(
            id="mortain_offensiveger_evening",
            map=MAPS["mortain"],
            game_mode=GameMode.OFFENSIVE,
            attackers=Team.AXIS,
            environment=Environment.DUSK,
        ),
        Layer(
            id="mortain_skirmish_day",
            map=MAPS["mortain"],
            game_mode=GameMode.CONTROL,
        ),
        Layer(
            id="mortain_skirmish_overcast",
            map=MAPS["mortain"],
            game_mode=GameMode.CONTROL,
            environment=Environment.OVERCAST,
        ),
        Layer(
            id="mortain_skirmish_evening",
            map=MAPS["mortain"],
            game_mode=GameMode.CONTROL,
            environment=Environment.DUSK,
        ),
    )
}


def parse_layer(layer_name: str | Layer) -> Layer:
    if isinstance(layer_name, Layer):
        layer_name = str(layer_name)
    elif is_server_loading_map(map_name=layer_name):
        return LAYERS[UNKNOWN_MAP_NAME]

    layer = LAYERS.get(layer_name)
    if layer:
        return layer

    getLogger().warning("Unknown layer %s", layer_name)

    layer_match = RE_LAYER_NAME.match(layer_name)
    if not layer_match:
        return _parse_legacy_layer(layer_name)

    layer_data = layer_match.groupdict()

    tag = layer_data["tag"]
    map_ = None
    for m in MAPS.values():
        if m.tag == tag:
            map_ = m
            break
    if map_ is None:
        map_ = Map(
            id=tag.lower(),
            name=tag,
            tag=tag,
            pretty_name=tag.capitalize(),
            shortname=tag,
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        )

    try:
        game_mode = GameMode[layer_data["game_mode"].upper()]
    except KeyError:
        game_mode = GameMode.WARFARE
    else:
        if game_mode == GameMode.OFFENSIVE:
            attackers = Team.ALLIES
        else:
            attackers = None

    if layer_data["environment"]:
        try:
            environment = Environment[layer_data["environment"].upper()]
        except KeyError:
            environment = Environment.DAY
    else:
        environment = Environment.DAY

    return Layer(
        id=layer_name,
        map=map_,
        game_mode=game_mode,
        attackers=attackers,
        environment=environment,
    )


def _parse_legacy_layer(layer_name: str):
    layer_match = RE_LEGACY_LAYER_NAME.match(layer_name)
    if not layer_match:
        raise ValueError("Unparsable layer '%s'" % layer_name)

    layer_data = layer_match.groupdict()

    name = layer_data["name"]
    map_ = MAPS.get(layer_data["name"])
    if not map_:
        map_ = Map(
            id=name,
            name=name.capitalize(),
            tag=name.upper(),
            pretty_name=name.capitalize(),
            shortname=name.capitalize(),
            allies=Faction(name=FactionName.US.value, team=Team.ALLIES),
            axis=Faction(name=FactionName.GER.value, team=Team.AXIS),
        )

    result = Layer(id=layer_name, map=map_, game_mode=GameMode.WARFARE)

    if layer_data["offensive"]:
        result.game_mode = GameMode.OFFENSIVE
        try:
            result.attackers = Team[FactionName[layer_data["attackers"].upper()].value]
        except KeyError:
            pass

    elif layer_data["game_mode"]:
        try:
            result.game_mode = GameMode[layer_data["game_mode"].upper()]
        except KeyError:
            pass

    environment = layer_data["environment"]
    if environment:
        try:
            result.environment = Environment[environment.upper()]
        except KeyError:
            pass

    return result


def get_opposite_side(team: Team) -> Literal[Team.AXIS, Team.ALLIES]:
    return Team.AXIS if team == Team.ALLIES else Team.ALLIES


def sort_maps_by_gamemode(maps: Sequence[Layer]) -> list[Layer]:
    warfare = [m for m in maps if m.game_mode == GameMode.WARFARE]
    offensive = [m for m in maps if m.game_mode == GameMode.OFFENSIVE]
    control = [m for m in maps if m.game_mode == GameMode.CONTROL]
    phased = [m for m in maps if m.game_mode == GameMode.PHASED]
    majority = [m for m in maps if m.game_mode == GameMode.MAJORITY]

    return warfare + offensive + control + phased + majority


def numbered_maps(maps: list[Layer]) -> dict[str, Layer]:
    # Control the order of the maps so they present in a sensible fashion in messages
    ordered_maps = sort_maps_by_gamemode(maps)
    return {str(idx): map_ for idx, map_ in enumerate(ordered_maps)}


def categorize_maps(maps: Iterable[Layer]) -> dict[GameMode, list[Layer]]:
    categories = {
        GameMode.OFFENSIVE: [
            map_ for map_ in maps if map_.game_mode == GameMode.OFFENSIVE
        ],
        GameMode.WARFARE: [map_ for map_ in maps if map_.game_mode == GameMode.WARFARE],
        GameMode.CONTROL: [map_ for map_ in maps if map_.game_mode == GameMode.CONTROL],
    }

    return categories


def safe_get_map_name(map_name: str, pretty: bool = True) -> str:
    """Return the RCON map name if not found"""
    map_ = parse_layer(map_name)

    if map_ is None:
        return map_name

    if pretty:
        return map_.pretty_name
    else:
        return map_.map.name


def is_server_loading_map(map_name: str) -> bool:
    return "untitled" in map_name.lower()

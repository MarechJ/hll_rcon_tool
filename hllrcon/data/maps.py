# ruff: noqa: N802

from collections.abc import Generator
from enum import StrEnum
from typing import overload

from pydantic import BaseModel, RootModel

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    class_cached_property,
)
from .factions import Faction


class Orientation(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Strongpoint(BaseModel, frozen=True):
    name: str

    # TODO: Add center and radius


class Sector(RootModel[tuple[Strongpoint, Strongpoint, Strongpoint]], frozen=True):
    """A sector is a group of three objectives on the map."""

    def __init__(
        self,
        strongpoint1: Strongpoint,
        strongpoint2: Strongpoint,
        strongpoint3: Strongpoint,
    ) -> None:
        super().__init__((strongpoint1, strongpoint2, strongpoint3))

    def __iter__(self) -> Generator[Strongpoint]:  # type: ignore[override]
        yield from self.root

    def __getitem__(self, index: int) -> Strongpoint:
        return self.root[index]


class Sectors(RootModel[tuple[Sector, Sector, Sector, Sector, Sector]], frozen=True):
    """A collection of five sectors on the map."""

    def __init__(
        self,
        sector1: Sector,
        sector2: Sector,
        sector3: Sector,
        sector4: Sector,
        sector5: Sector,
    ) -> None:
        super().__init__((sector1, sector2, sector3, sector4, sector5))

    def __iter__(self) -> Generator[Sector]:  # type: ignore[override]
        yield from self.root

    @overload
    def __getitem__(self, index: int) -> Sector: ...

    @overload
    def __getitem__(self, index: tuple[int, int]) -> Strongpoint: ...

    def __getitem__(self, index: int | tuple[int, int]) -> Sector | Strongpoint:
        if isinstance(index, tuple) and len(index) == 2:  # noqa: PLR2004
            return self.root[index[0]][index[1]]
        return self.root[index]


class Map(CaseInsensitiveIndexedBaseModel):
    name: str
    tag: str
    pretty_name: str
    short_name: str
    allies: Faction
    axis: Faction
    orientation: Orientation
    """Whether the sectors on this map are stacked horizontally (left-to-right) or
    vertically (top-to-bottom)."""
    sectors: Sectors
    """The five sectors available on the map for Warfare and Offensive game modes.
    Sectors run from left to right or top to bottom, depending on the orientation of
    the map."""
    mirror_factions: bool
    """If the side each faction starts at is mirrored or not. By default, Allies spawn
    left/top, Axis spawn right/bottom."""

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r}, "
            f"tag={self.tag!r}, pretty_name={self.pretty_name!r}, "
            f"short_name={self.short_name!r}, allies={self.allies!r}, "
            f"axis={self.axis!r}, orientation={self.orientation!r}, "
            f"mirror_factions={self.mirror_factions!r})"
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Map, str)):
            return str(self).lower() == str(other).lower()
        return NotImplemented

    @class_cached_property
    @classmethod
    def CARENTAN(cls) -> "Map":
        return cls(
            id="carentan",
            name="CARENTAN",
            tag="CAR",
            pretty_name="Carentan",
            short_name="Carentan",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Blactot"),
                    Strongpoint(name="502nd Start"),
                    Strongpoint(name="Farm Ruins"),
                ),
                Sector(
                    Strongpoint(name="Pumping Station"),
                    Strongpoint(name="Ruins"),
                    Strongpoint(name="Derailed Train"),
                ),
                Sector(
                    Strongpoint(name="Canal Crossing"),
                    Strongpoint(name="Town Center"),
                    Strongpoint(name="Train Station"),
                ),
                Sector(
                    Strongpoint(name="Customs"),
                    Strongpoint(name="Rail Crossing"),
                    Strongpoint(name="Mount Halais"),
                ),
                Sector(
                    Strongpoint(name="Canal Locks"),
                    Strongpoint(name="Rail Causeway"),
                    Strongpoint(name="La Maison Des Ormes"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def DRIEL(cls) -> "Map":
        return cls(
            id="driel",
            name="DRIEL",
            tag="DRL",
            pretty_name="Driel",
            short_name="Driel",
            allies=Faction.CW,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Oosterbeek Approach"),
                    Strongpoint(name="Roseander Polder"),
                    Strongpoint(name="Kasteel Rosande"),
                ),
                Sector(
                    Strongpoint(name="Boatyard"),
                    Strongpoint(name="Bridgeway"),
                    Strongpoint(name="Rijn Banks"),
                ),
                Sector(
                    Strongpoint(name="Brick Factory"),
                    Strongpoint(name="Railway Bridge"),
                    Strongpoint(name="Gun Emplacements"),
                ),
                Sector(
                    Strongpoint(name="Rietveld"),
                    Strongpoint(name="South Railway"),
                    Strongpoint(name="Middel Road"),
                ),
                Sector(
                    Strongpoint(name="Orchards"),
                    Strongpoint(name="Schaduwwolken Farm"),
                    Strongpoint(name="Fields"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def EL_ALAMEIN(cls) -> "Map":
        return cls(
            id="elalamein",
            name="EL ALAMEIN",
            tag="ELA",
            pretty_name="El Alamein",
            short_name="Alamein",
            allies=Faction.B8A,
            axis=Faction.DAK,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Vehicle Depot"),
                    Strongpoint(name="Artillery Guns"),
                    Strongpoint(name="Miteiriya Ridge"),
                ),
                Sector(
                    Strongpoint(name="Hamlet Ruins"),
                    Strongpoint(name="El Mreir"),
                    Strongpoint(name="Watchtower"),
                ),
                Sector(
                    Strongpoint(name="Desert Rat Trenches"),
                    Strongpoint(name="Oasis"),
                    Strongpoint(name="Valley"),
                ),
                Sector(
                    Strongpoint(name="Fuel Depot"),
                    Strongpoint(name="Airfield Command"),
                    Strongpoint(name="Airfield Hangars"),
                ),
                Sector(
                    Strongpoint(name="Cliffside Village"),
                    Strongpoint(name="Ambushed Convoy"),
                    Strongpoint(name="Quarry"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_RIDGE(cls) -> "Map":
        return cls(
            id="elsenbornridge",
            name="ELSENBORN RIDGE",
            tag="EBR",
            pretty_name="Elsenborn Ridge",
            short_name="Elsenborn",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="99th Command Centre"),
                    Strongpoint(name="Gun Battery"),
                    Strongpoint(name="U.S. Camp"),
                ),
                Sector(
                    Strongpoint(name="Elsenborn Ridge"),
                    Strongpoint(name="Farahilde Farm"),
                    Strongpoint(name="Jensit Pillboxes"),
                ),
                Sector(
                    Strongpoint(name="Road To Elsenborn Ridge"),
                    Strongpoint(name="Dug Out Tank"),
                    Strongpoint(name="Checkpoint"),
                ),
                Sector(
                    Strongpoint(name="Erelsdell Farmhouse"),
                    Strongpoint(name="AA Battery"),
                    Strongpoint(name="Hinterburg"),
                ),
                Sector(
                    Strongpoint(name="Supply Cache"),
                    Strongpoint(name="Foxholes"),
                    Strongpoint(name="Fuel Depot"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def FOY(cls) -> "Map":
        return cls(
            id="foy",
            name="FOY",
            tag="FOY",
            pretty_name="Foy",
            short_name="Foy",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Road To Recogne"),
                    Strongpoint(name="Cobru Approach"),
                    Strongpoint(name="Road To Noville"),
                ),
                Sector(
                    Strongpoint(name="Cobru Factory"),
                    Strongpoint(name="Foy"),
                    Strongpoint(name="Flak Battery"),
                ),
                Sector(
                    Strongpoint(name="West Bend"),
                    Strongpoint(name="Southern Edge"),
                    Strongpoint(name="Dugout Barn"),
                ),
                Sector(
                    Strongpoint(name="N30 Highway"),
                    Strongpoint(name="Bizory Foy Road"),
                    Strongpoint(name="Eastern Ourthe"),
                ),
                Sector(
                    Strongpoint(name="Road To Bastogne"),
                    Strongpoint(name="Bois Jacques"),
                    Strongpoint(name="Forest Outskirts"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def HILL_400(cls) -> "Map":
        return cls(
            id="hill400",
            name="HILL 400",
            tag="HIL",
            pretty_name="Hill 400",
            short_name="Hill 400",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Convoy Ambush"),
                    Strongpoint(name="Federchecke Junction"),
                    Strongpoint(name="Stuckchen Farm"),
                ),
                Sector(
                    Strongpoint(name="Roer River House"),
                    Strongpoint(name="Bergstein Church"),
                    Strongpoint(name="Kirchweg"),
                ),
                Sector(
                    Strongpoint(name="Flak Pits"),
                    Strongpoint(name="Hill 400"),
                    Strongpoint(name="Southern Approach"),
                ),
                Sector(
                    Strongpoint(name="Eselsweg Junction"),
                    Strongpoint(name="Eastern Slope"),
                    Strongpoint(name="Trainwreck"),
                ),
                Sector(
                    Strongpoint(name="Roer River Crossing"),
                    Strongpoint(name="Zerkall"),
                    Strongpoint(name="PaperMill"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_FOREST(cls) -> "Map":
        return cls(
            id="hurtgenforest",
            name="HÜRTGEN FOREST",
            tag="HUR",
            pretty_name="Hurtgen Forest",
            short_name="Hurtgen",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="The Masbauch Approach"),
                    Strongpoint(name="Reserve Station"),
                    Strongpoint(name="Lumber Yard"),
                ),
                Sector(
                    Strongpoint(name="Wehebach Overlook"),
                    Strongpoint(name="Kall Trail"),
                    Strongpoint(name="The Ruin"),
                ),
                Sector(
                    Strongpoint(name="North Pass"),
                    Strongpoint(name="The Scar"),
                    Strongpoint(name="The Siegfried Line"),
                ),
                Sector(
                    Strongpoint(name="Hill 15"),
                    Strongpoint(name="Jacob's Barn"),
                    Strongpoint(name="Salient 42"),
                ),
                Sector(
                    Strongpoint(name="Grosshau Approach"),
                    Strongpoint(name="Hürtgen Approach"),
                    Strongpoint(name="Logging Camp"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def KHARKOV(cls) -> "Map":
        return cls(
            id="kharkov",
            name="Kharkov",
            tag="KHA",
            pretty_name="Kharkov",
            short_name="Kharkov",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Marsh Town"),
                    Strongpoint(name="Soviet Vantage Point"),
                    Strongpoint(name="German Fuel Dump"),
                ),
                Sector(
                    Strongpoint(name="Bitter Spring"),
                    Strongpoint(name="Lumber Works"),
                    Strongpoint(name="Windmill Hillside"),
                ),
                Sector(
                    Strongpoint(name="Water Mill"),
                    Strongpoint(name="St Mary"),
                    Strongpoint(name="Distillery"),
                ),
                Sector(
                    Strongpoint(name="River Crossing"),
                    Strongpoint(name="Belgorod Outskirts"),
                    Strongpoint(name="Lumberyard"),
                ),
                Sector(
                    Strongpoint(name="Wehrmacht Overlook"),
                    Strongpoint(name="Hay Storage"),
                    Strongpoint(name="Overpass"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def KURSK(cls) -> "Map":
        return cls(
            id="kursk",
            name="KURSK",
            tag="KUR",
            pretty_name="Kursk",
            short_name="Kursk",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Artillery Position"),
                    Strongpoint(name="Grushki"),
                    Strongpoint(name="Grushki Flank"),
                ),
                Sector(
                    Strongpoint(name="Panzer's End"),
                    Strongpoint(name="Defence In Depth"),
                    Strongpoint(name="Listening Post"),
                ),
                Sector(
                    Strongpoint(name="The Windmills"),
                    Strongpoint(name="Yamki"),
                    Strongpoint(name="Oleg's House"),
                ),
                Sector(
                    Strongpoint(name="Rudno"),
                    Strongpoint(name="Destroyed Battery"),
                    Strongpoint(name="The Muddy Churn"),
                ),
                Sector(
                    Strongpoint(name="Road To Kursk"),
                    Strongpoint(name="Ammo Dump"),
                    Strongpoint(name="Eastern Position"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def MORTAIN(cls) -> "Map":
        return cls(
            id="mortain",
            name="MORTAIN",
            tag="MOR",
            pretty_name="Mortain",
            short_name="Mortain",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Hotel De La Poste"),
                    Strongpoint(name="Forward Battery"),
                    Strongpoint(name="Southern Approach"),
                ),
                Sector(
                    Strongpoint(name="Mortain Outskirts"),
                    Strongpoint(name="Forward Medical Aid Station"),
                    Strongpoint(name="Mortain Approach"),
                ),
                Sector(
                    Strongpoint(name="Hill 314"),
                    Strongpoint(name="Petit Chappelle Saint Michel"),
                    Strongpoint(name="U.S. Southern Roadblock"),
                ),
                Sector(
                    Strongpoint(name="Destroyed German Convoy"),
                    Strongpoint(name="German Recon Camp"),
                    Strongpoint(name="Le Hermitage Farm"),
                ),
                Sector(
                    Strongpoint(name="Abandoned German Checkpoint"),
                    Strongpoint(name="German Defensive Camp"),
                    Strongpoint(name="Farm Of Bonovisin"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def OMAHA_BEACH(cls) -> "Map":
        return cls(
            id="omahabeach",
            name="OMAHA BEACH",
            tag="OMA",
            pretty_name="Omaha Beach",
            short_name="Omaha",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Beaumont Road"),
                    Strongpoint(name="Crossroads"),
                    Strongpoint(name="Les Isles"),
                ),
                Sector(
                    Strongpoint(name="Rear Battery"),
                    Strongpoint(name="Church Road"),
                    Strongpoint(name="The Orchards"),
                ),
                Sector(
                    Strongpoint(name="West Vierville"),
                    Strongpoint(name="Vierville Sur Mer"),
                    Strongpoint(name="Artillery Battery"),
                ),
                Sector(
                    Strongpoint(name="WN73"),
                    Strongpoint(name="WN71"),
                    Strongpoint(name="WN70"),
                ),
                Sector(
                    Strongpoint(name="Dog Green"),
                    Strongpoint(name="The Draw"),
                    Strongpoint(name="Dog White"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def PURPLE_HEART_LANE(cls) -> "Map":
        return cls(
            id="purpleheartlane",
            name="PURPLE HEART LANE",
            tag="PHL",
            pretty_name="Purple Heart Lane",
            short_name="PHL",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Bloody Bend"),
                    Strongpoint(name="Dead Man's Corner"),
                    Strongpoint(name="Forward Battery"),
                ),
                Sector(
                    Strongpoint(name="Jourdan Canal"),
                    Strongpoint(name="Douve Bridge"),
                    Strongpoint(name="Douve River Battery"),
                ),
                Sector(
                    Strongpoint(name="Groult Pillbox"),
                    Strongpoint(name="Carentan Causeway"),
                    Strongpoint(name="Flak Position"),
                ),
                Sector(
                    Strongpoint(name="Madeleine Farm"),
                    Strongpoint(name="Madeleine Bridge"),
                    Strongpoint(name="Aid Station"),
                ),
                Sector(
                    Strongpoint(name="Ingouf Crossroads"),
                    Strongpoint(name="Road To Carentan"),
                    Strongpoint(name="Cabbage Patch"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def REMAGEN(cls) -> "Map":
        return cls(
            id="remagen",
            name="REMAGEN",
            tag="REM",
            pretty_name="Remagen",
            short_name="Remagen",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Alte Liebe Barsch"),
                    Strongpoint(name="Bewaldet Kreuzung"),
                    Strongpoint(name="Dan Radart 512"),
                ),
                Sector(
                    Strongpoint(name="Erpel"),
                    Strongpoint(name="Erpeler Ley"),
                    Strongpoint(name="Kasbach Outlook"),
                ),
                Sector(
                    Strongpoint(name="St Severin Chapel"),
                    Strongpoint(name="Ludendorff Bridge"),
                    Strongpoint(name="Bauernhof Am Rhein"),
                ),
                Sector(
                    Strongpoint(name="Remagen"),
                    Strongpoint(name="Mobelfabrik"),
                    Strongpoint(name="SchlieffenAusweg"),
                ),
                Sector(
                    Strongpoint(name="Waldburg"),
                    Strongpoint(name="Muhlenweg"),
                    Strongpoint(name="Hagelkreuz"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def ST_MARIE_DU_MONT(cls) -> "Map":
        return cls(
            id="stmariedumont",
            name="ST MARIE DU MONT",
            tag="SMDM",
            pretty_name="St. Marie Du Mont",
            short_name="SMDM",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Winters Landing"),
                    Strongpoint(name="Le Grand Chemin"),
                    Strongpoint(name="The Barn"),
                ),
                Sector(
                    Strongpoint(name="Brecourt Battery"),
                    Strongpoint(name="Cattlesheds"),
                    Strongpoint(name="Rue De La Gare"),
                ),
                Sector(
                    Strongpoint(name="The Dugout"),
                    Strongpoint(name="AA Network"),
                    Strongpoint(name="Pierre's Farm"),
                ),
                Sector(
                    Strongpoint(name="Hugo's Farm"),
                    Strongpoint(name="The Hamlet"),
                    Strongpoint(name="Ste Marie Du Mont"),
                ),
                Sector(
                    Strongpoint(name="The Corner"),
                    Strongpoint(name="Hill 6"),
                    Strongpoint(name="The Fields"),
                ),
            ),
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def ST_MERE_EGLISE(cls) -> "Map":
        return cls(
            id="stmereeglise",
            name="SAINTE-MÈRE-ÉGLISE",
            tag="SME",
            pretty_name="St. Mere Eglise",
            short_name="SME",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Flak Position"),
                    Strongpoint(name="Vaulaville"),
                    Strongpoint(name="La Prairie"),
                ),
                Sector(
                    Strongpoint(name="Route Du Haras"),
                    Strongpoint(name="Western Approach"),
                    Strongpoint(name="Rue De Gambosville"),
                ),
                Sector(
                    Strongpoint(name="Hospice"),
                    Strongpoint(name="Ste Mere Eglise"),
                    Strongpoint(name="Checkpoint"),
                ),
                Sector(
                    Strongpoint(name="Artillery Battery"),
                    Strongpoint(name="The Cemetery"),
                    Strongpoint(name="Maison Du Crique"),
                ),
                Sector(
                    Strongpoint(name="Les Vieux Vergers"),
                    Strongpoint(name="Cross Roads"),
                    Strongpoint(name="Russeau De Ferme"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD(cls) -> "Map":
        return cls(
            id="stalingrad",
            name="STALINGRAD",
            tag="STA",
            pretty_name="Stalingrad",
            short_name="Stalingrad",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Mamayev Approach"),
                    Strongpoint(name="Nail Factory"),
                    Strongpoint(name="City Overlook"),
                ),
                Sector(
                    Strongpoint(name="Dolgiy Ravine"),
                    Strongpoint(name="Yellow House"),
                    Strongpoint(name="Komsomol HQ"),
                ),
                Sector(
                    Strongpoint(name="Railway Crossing"),
                    Strongpoint(name="Carriage Depot"),
                    Strongpoint(name="Train Station"),
                ),
                Sector(
                    Strongpoint(name="House Of The Workers"),
                    Strongpoint(name="Pavlov's House"),
                    Strongpoint(name="The Brewery"),
                ),
                Sector(
                    Strongpoint(name="L Shaped House"),
                    Strongpoint(name="Grudinin's Mill"),
                    Strongpoint(name="Volga Banks"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def TOBRUK(cls) -> "Map":
        return cls(
            id="tobruk",
            name="TOBRUK",
            tag="TBK",
            pretty_name="Tobruk",
            short_name="Tobruk",
            allies=Faction.B8A,
            axis=Faction.DAK,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Guard Room"),
                    Strongpoint(name="Tank Graveyard"),
                    Strongpoint(name="Division Headquarters"),
                ),
                Sector(
                    Strongpoint(name="West Creek"),
                    Strongpoint(name="Albergo Ristorante Moderno"),
                    Strongpoint(name="King Square"),
                ),
                Sector(
                    Strongpoint(name="Desert Rat Caves"),
                    Strongpoint(name="Church Grounds"),
                    Strongpoint(name="Admiralty House"),
                ),
                Sector(
                    Strongpoint(name="Abandoned Ammo Cache"),
                    Strongpoint(name="8th Army Medical Hospital"),
                    Strongpoint(name="Supply Drop"),
                ),
                Sector(
                    Strongpoint(name="Road To Senussi Mine"),
                    Strongpoint(name="Makeshift Aid Station"),
                    Strongpoint(name="Cargo Warehouses"),
                ),
            ),
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def UTAH_BEACH(cls) -> "Map":
        return cls(
            id="utahbeach",
            name="UTAH BEACH",
            tag="UTA",
            pretty_name="Utah Beach",
            short_name="Utah",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            sectors=Sectors(
                Sector(
                    Strongpoint(name="Mammut Radar"),
                    Strongpoint(name="Flooded House"),
                    Strongpoint(name="Sainte Marie Approach"),
                ),
                Sector(
                    Strongpoint(name="Sunken Bridge"),
                    Strongpoint(name="La Grande Crique"),
                    Strongpoint(name="Drowned Fields"),
                ),
                Sector(
                    Strongpoint(name="WN4"),
                    Strongpoint(name="The Chapel"),
                    Strongpoint(name="WN7"),
                ),
                Sector(
                    Strongpoint(name="AABattery"),
                    Strongpoint(name="Hill 5"),
                    Strongpoint(name="WN5"),
                ),
                Sector(
                    Strongpoint(name="Tare Green"),
                    Strongpoint(name="Red Roof House"),
                    Strongpoint(name="Uncle Red"),
                ),
            ),
            mirror_factions=True,
        )

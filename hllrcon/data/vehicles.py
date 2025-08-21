# ruff: noqa: N802, D400, D415

from enum import StrEnum

from pydantic import BaseModel, Field

from hllrcon.data._utils import IndexedBaseModel, class_cached_property
from hllrcon.data.factions import Faction
from hllrcon.data.roles import Role, RoleType
from hllrcon.data.weapons import Weapon

_TANK_CREW_ROLES = {role for role in Role.all() if role.type == RoleType.ARMOR}


class VehicleType(StrEnum):
    HEAVY_TANK = "Heavy Tank"
    MEDIUM_TANK = "Medium Tank"
    LIGHT_TANK = "Light Tank"
    RECON_VEHICLE = "Recon Vehicle"
    HALF_TRACK = "Half-Track"
    TRANSPORT_TRUCK = "Transport Truck"
    SUPPLY_TRUCK = "Supply Truck"
    JEEP = "Jeep"
    ARTILLERY = "Artillery"
    ANTI_TANK_GUN = "Anti-Tank Gun"


class VehicleSeatType(StrEnum):
    DRIVER = "Driver"
    GUNNER = "Gunner"
    SPOTTER = "Spotter"
    LOADER = "Loader"
    PASSENGER = "Passenger"


class VehicleSeat(BaseModel, frozen=True):
    index: int
    type: VehicleSeatType
    weapons: list[Weapon] = Field(default_factory=list)
    requires_roles: set[Role] | None = None
    exposed: bool


class Vehicle(IndexedBaseModel[str]):
    id: str
    name: str
    factions: set[Faction] = Field(min_length=1)
    type: VehicleType
    seats: list[VehicleSeat]

    @class_cached_property
    @classmethod
    def M1_57MM(cls) -> "Vehicle":
        """*M1 57mm*"""
        return cls(
            id="M1 57mm",
            name="M1 57mm",
            type=VehicleType.ANTI_TANK_GUN,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_57MM_CANNON__M1_57],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M114(cls) -> "Vehicle":
        """*M114*"""
        return cls(
            id="M114",
            name="M114 Howitzer",
            type=VehicleType.ARTILLERY,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_57MM_CANNON__M1_57],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M8_GREYHOUND(cls) -> "Vehicle":
        """*M8 Greyhound*"""
        return cls(
            id="M8 Greyhound",
            name="M8 Greyhound",
            type=VehicleType.RECON_VEHICLE,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_M6_37MM__M8_GREYHOUND,
                        Weapon.V_COAXIAL_M1919__M8_GREYHOUND,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def STUART_M5A1(cls) -> "Vehicle":
        """*Stuart M5A1*"""
        return cls(
            id="Stuart M5A1",
            name="M5A1 Stuart",
            type=VehicleType.LIGHT_TANK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_M1919__STUART_M5A1,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_37MM_CANNON__STUART_M5A1,
                        Weapon.V_COAXIAL_M1919__STUART_M5A1,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3_75W(cls) -> "Vehicle":
        """*Sherman M4A3(75)W*"""
        return cls(
            id="Sherman M4A3(75)W",
            name="M4A3(75)W Sherman",
            type=VehicleType.MEDIUM_TANK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_M1919__SHERMAN_M4A3_75W,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_HULL_M1919__SHERMAN_M4A3_75W,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3E2(cls) -> "Vehicle":
        """*Sherman M4A3E2*"""
        return cls(
            id="Sherman M4A3E2",
            name="M4A3E2 Sherman",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_M1919__SHERMAN_M4A3E2,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_75MM_M3_GUN__SHERMAN_M4A3E2,
                        Weapon.V_COAXIAL_M1919__SHERMAN_M4A3E2,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3E2_76(cls) -> "Vehicle":
        """*Sherman M4A3E2(76)*"""
        return cls(
            id="Sherman M4A3E2(76)",
            name="M4A3E2(76) Sherman",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_M1919__SHERMAN_M4A3E2_76,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_76MM_M1_GUN__SHERMAN_M4A3E2_76,
                        Weapon.V_COAXIAL_M1919__SHERMAN_M4A3E2_76,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GMC_CCKW_353_SUPPLY(cls) -> "Vehicle":
        """*GMC CCKW 353 (Supply)*"""
        return cls(
            id="GMC CCKW 353 (Supply)",
            name="GMC CCKW 353",
            type=VehicleType.SUPPLY_TRUCK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GMC_CCKW_353_TRANSPORT(cls) -> "Vehicle":
        """*GMC CCKW 353 (Transport)*"""
        return cls(
            id="GMC CCKW 353 (Transport)",
            name="GMC CCKW 353",
            type=VehicleType.TRANSPORT_TRUCK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=5,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=6,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=7,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=8,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=9,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=10,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=11,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M3_HALF_TRACK(cls) -> "Vehicle":
        """*M3 Half-track*"""
        return cls(
            id="M3 Half-track",
            name="M3 Half-track",
            type=VehicleType.HALF_TRACK,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_M2_BROWNING__M3_HALF_TRACK,
                    ],
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=5,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=6,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=7,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def JEEP_WILLYS(cls) -> "Vehicle":
        """*Jeep Willys*"""
        return cls(
            id="Jeep Willys",
            name="Willy's Jeep",
            type=VehicleType.JEEP,
            factions={Faction.US},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def PAK_40(cls) -> "Vehicle":
        """*PAK 40*"""
        return cls(
            id="PAK 40",
            name="Pak 40",
            type=VehicleType.ANTI_TANK_GUN,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_75MM_CANNON__PAK_40],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SFH_18(cls) -> "Vehicle":
        """*sFH 18*"""
        return cls(
            id="sFH 18",
            name="sFH 18",
            type=VehicleType.ARTILLERY,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_150MM_HOWITZER__SFH_18],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_234_PUMA(cls) -> "Vehicle":
        """*Sd.Kfz.234 Puma*"""
        return cls(
            id="Sd.Kfz.234 Puma",
            name="Sd.Kfz.234 Puma",
            type=VehicleType.RECON_VEHICLE,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_50MM_KWK_91_1__SD_KFZ_234_PUMA,
                        Weapon.V_COAXIAL_MG34__SD_KFZ_234_PUMA,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_121_LUCHS(cls) -> "Vehicle":
        """*Sd.Kfz.121 Luchs*"""
        return cls(
            id="Sd.Kfz.121 Luchs",
            name="Sd.Kfz.121 Luchs",
            type=VehicleType.LIGHT_TANK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_20MM_KWK_30__SD_KFZ_121_LUCHS,
                        Weapon.V_COAXIAL_MG34__SD_KFZ_121_LUCHS,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_161_PANZER_IV(cls) -> "Vehicle":
        """*Sd.Kfz.161 Panzer IV*"""
        return cls(
            id="Sd.Kfz.161 Panzer IV",
            name="Sd.Kfz.161 Panzer IV",
            type=VehicleType.MEDIUM_TANK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_MG34__SD_KFZ_161_PANZER_IV,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_75MM_CANNON__SD_KFZ_161_PANZER_IV,
                        Weapon.V_COAXIAL_MG34__SD_KFZ_161_PANZER_IV,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_171_PANTHER(cls) -> "Vehicle":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Sd.Kfz.171 Panther",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_MG34__SD_KFZ_171_PANTHER,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_75MM_CANNON__SD_KFZ_171_PANTHER,
                        Weapon.V_COAXIAL_MG34__SD_KFZ_171_PANTHER,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_181_TIGER_1(cls) -> "Vehicle":
        """*Sd.Kfz.181 Tiger 1*"""
        return cls(
            id="Sd.Kfz.181 Tiger 1",
            name="Sd.Kfz.181 Tiger 1",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_MG34__SD_KFZ_181_TIGER_1,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_88MM_KWK_36_L_56__SD_KFZ_181_TIGER_1,
                        Weapon.V_COAXIAL_MG34__SD_KFZ_181_TIGER_1,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def OPEL_BLITZ_SUPPLY(cls) -> "Vehicle":
        """*Opel Blitz (Supply)*"""
        return cls(
            id="Opel Blitz (Supply)",
            name="Opel Blitz",
            type=VehicleType.SUPPLY_TRUCK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def OPEL_BLITZ_TRANSPORT(cls) -> "Vehicle":
        """*Opel Blitz (Transport)*"""
        return cls(
            id="Opel Blitz (Transport)",
            name="Opel Blitz",
            type=VehicleType.TRANSPORT_TRUCK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=5,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=6,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=7,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=8,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=9,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=10,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=11,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_251_HALF_TRACK(cls) -> "Vehicle":
        """*Sd.Kfz 251 Half-track*"""
        return cls(
            id="Sd.Kfz 251 Half-track",
            name="Sd.Kfz 251 Half-track",
            type=VehicleType.HALF_TRACK,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_M2_BROWNING__M3_HALF_TRACK,
                    ],
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=5,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=6,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=7,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def KUBELWAGEN(cls) -> "Vehicle":
        """*Kubelwagen*"""
        return cls(
            id="Kubelwagen",
            name="Kubelwagen",
            type=VehicleType.JEEP,
            factions={Faction.GER, Faction.DAK},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_2(cls) -> "Vehicle":
        """*ZiS-2*"""
        return cls(
            id="ZiS-2",
            name="ZiS-2",
            type=VehicleType.ANTI_TANK_GUN,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_57MM_CANNON__ZIS_2],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M1938_M_30(cls) -> "Vehicle":
        """*M1938 (M-30)*"""
        return cls(
            id="M1938 (M-30)",
            name="M-30",
            type=VehicleType.ARTILLERY,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_122MM_HOWITZER__M1938_M_30],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BA_10(cls) -> "Vehicle":
        """*BA-10*"""
        return cls(
            id="BA-10",
            name="BA-10",
            type=VehicleType.RECON_VEHICLE,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_19_K_45MM__BA_10,
                        Weapon.V_COAXIAL_DT__BA_10,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def T70(cls) -> "Vehicle":
        """*T70*"""
        return cls(
            id="T70",
            name="T70",
            type=VehicleType.LIGHT_TANK,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_45MM_M1937__T70,
                        Weapon.V_COAXIAL_DT__T70,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def T34_76(cls) -> "Vehicle":
        """*T34/76*"""
        return cls(
            id="T34/76",
            name="T34/76",
            type=VehicleType.MEDIUM_TANK,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_DT__T34_76,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_76MM_ZIS_5__T34_76,
                        Weapon.V_COAXIAL_DT__T34_76,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def IS_1(cls) -> "Vehicle":
        """*IS-1*"""
        return cls(
            id="IS-1",
            name="IS-1",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_DT__IS_1,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_D_5T_85MM__IS_1,
                        Weapon.V_COAXIAL_DT__IS_1,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_5_SUPPLY(cls) -> "Vehicle":
        """*ZIS-5 (Supply)*"""
        return cls(
            id="ZIS-5 (Supply)",
            name="ZIS-5",
            type=VehicleType.SUPPLY_TRUCK,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_5_TRANSPORT(cls) -> "Vehicle":
        """*ZIS-5 (Transport)*"""
        return cls(
            id="ZIS-5 (Transport)",
            name="ZIS-5",
            type=VehicleType.TRANSPORT_TRUCK,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=5,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=6,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=7,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=8,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=9,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=10,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=11,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GAZ_67(cls) -> "Vehicle":
        """*GAZ-67*"""
        return cls(
            id="GAZ-67",
            name="GAZ-67",
            type=VehicleType.JEEP,
            factions={Faction.SOV},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def QF_6_POUNDER(cls) -> "Vehicle":
        """*QF 6-Pounder*"""
        return cls(
            id="QF 6-Pounder",
            name="QF 6-Pounder",
            type=VehicleType.ANTI_TANK_GUN,
            factions={Faction.CW, Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_QF_6_POUNDER__QF_6_POUNDER],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def QF_25_POUNDER(cls) -> "Vehicle":
        """*QF 25-Pounder*"""
        return cls(
            id="QF 25-Pounder",
            name="QF 25-Pounder",
            type=VehicleType.ARTILLERY,
            factions={Faction.CW, Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.GUNNER,
                    weapons=[Weapon.V_QF_25_POUNDER__QF_25_POUNDER],
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.LOADER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def DAIMLER(cls) -> "Vehicle":
        """*Daimler*"""
        return cls(
            id="Daimler",
            name="Daimler",
            type=VehicleType.RECON_VEHICLE,
            factions={Faction.CW, Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_QF_2_POUNDER__DAIMLER,
                        Weapon.V_COAXIAL_BESA__DAIMLER,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def TETRARCH(cls) -> "Vehicle":
        """*Tetrarch*"""
        return cls(
            id="Tetrarch",
            name="Tetrarch",
            type=VehicleType.LIGHT_TANK,
            factions={Faction.CW},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_QF_2_POUNDER__TETRARCH,
                        Weapon.V_COAXIAL_BESA__TETRARCH,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M3_STUART_HONEY(cls) -> "Vehicle":
        """*M3 Stuart Honey*"""
        return cls(
            id="M3 Stuart Honey",
            name="M3 Stuart Honey",
            type=VehicleType.LIGHT_TANK,
            factions={Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_M1919__M3_STUART_HONEY,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_37MM_CANNON__M3_STUART_HONEY,
                        Weapon.V_COAXIAL_M1919__M3_STUART_HONEY,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CROMWELL(cls) -> "Vehicle":
        """*Cromwell*"""
        return cls(
            id="Cromwell",
            name="Cromwell",
            type=VehicleType.MEDIUM_TANK,
            factions={Faction.CW},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_BESA__CROMWELL,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_OQF_75MM__CROMWELL,
                        Weapon.V_COAXIAL_BESA__CROMWELL,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CRUSADER_MK_III(cls) -> "Vehicle":
        """*Crusader Mk.III*"""
        return cls(
            id="Crusader Mk.III",
            name="Crusader Mk III",
            type=VehicleType.MEDIUM_TANK,
            factions={Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_OQF_57MM__CRUSADER_MK_III,
                        Weapon.V_COAXIAL_BESA__CRUSADER_MK_III,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def FIREFLY(cls) -> "Vehicle":
        """*Firefly*"""
        return cls(
            id="Firefly",
            name="Sherman Firefly",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.CW},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_QF_17_POUNDER__FIREFLY,
                        Weapon.V_COAXIAL_M1919__FIREFLY,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MK_III(cls) -> "Vehicle":
        """*Churchill Mk.III*"""
        return cls(
            id="Churchill Mk.III",
            name="Churchill Mk III",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_BESA_7_92MM__CHURCHILL_MK_III,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_OQF_57MM__CHURCHILL_MK_III,
                        Weapon.V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_III,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MK_VII(cls) -> "Vehicle":
        """*Churchill Mk.VII*"""
        return cls(
            id="Churchill Mk.VII",
            name="Churchill Mk VII",
            type=VehicleType.HEAVY_TANK,
            factions={Faction.CW},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    weapons=[
                        Weapon.V_HULL_BESA_7_92MM__CHURCHILL_MK_VII,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.GUNNER,
                    weapons=[
                        Weapon.V_OQF_75MM__CHURCHILL_MK_VII,
                        Weapon.V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_VII,
                    ],
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.SPOTTER,
                    requires_roles=_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BEDFORD_OYD_SUPPLY(cls) -> "Vehicle":
        """*Bedford OYD (Supply)*"""
        return cls(
            id="Bedford OYD (Supply)",
            name="Bedford OYD",
            type=VehicleType.SUPPLY_TRUCK,
            factions={Faction.CW, Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BEDFORD_OYD_TRANSPORT(cls) -> "Vehicle":
        """*Bedford OYD (Transport)*"""
        return cls(
            id="Bedford OYD (Transport)",
            name="Bedford OYD",
            type=VehicleType.TRANSPORT_TRUCK,
            factions={Faction.CW, Faction.B8A},
            seats=[
                VehicleSeat(
                    index=0,
                    type=VehicleSeatType.DRIVER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=1,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=2,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=3,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=4,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=5,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=6,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=7,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=8,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=9,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=10,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
                VehicleSeat(
                    index=11,
                    type=VehicleSeatType.PASSENGER,
                    exposed=True,
                ),
            ],
        )

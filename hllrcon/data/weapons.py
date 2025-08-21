# ruff: noqa: N802, D400, D415

from enum import StrEnum
from functools import cached_property
from typing import TYPE_CHECKING

from pydantic import Field

from hllrcon.data._utils import IndexedBaseModel, class_cached_property
from hllrcon.data.factions import Faction

if TYPE_CHECKING:
    from hllrcon.data.vehicles import Vehicle


class WeaponType(StrEnum):
    BOLT_ACTION_RIFLE = "Bolt Action Rifle"
    SEMI_AUTO_RIFLE = "Semi-Auto Rifle"
    ASSAULT_RIFLE = "Assault Rifle"
    SUBMACHINE_GUN = "Submachine Gun"
    MACHINE_GUN = "Machine Gun"
    SHOTGUN = "Shotgun"
    PISTOL = "Pistol"
    REVOLVER = "Revolver"
    GRENADE = "Grenade"
    AP_MINE = "Anti-Personnel Mine"
    AT_MINE = "Anti-Tank Mine"
    FLAMETHROWER = "Flamethrower"
    MELEE = "Melee"
    FLARE_GUN = "Flare Gun"
    ROCKET_LAUNCHER = "Rocket Launcher"
    ANTI_MATERIEL_RIFLE = "Anti-Materiel Rifle"
    AT_GUN = "Anti-Tank Gun"
    TANK_CANNON = "Tank Cannon"
    TANK_COAXIAL_MG = "Tank Coaxial MG"
    TANK_HULL_MG = "Tank Hull MG"
    MOUNTED_MG = "Mounted MG"
    ROADKILL = "Roadkill"
    ARTILLERY = "Artillery"
    COMMANDER_ABILITY = "Commander Ability"
    SATCHEL = "Satchel"
    UNKNOWN = "Unknown"


class Weapon(IndexedBaseModel[str]):
    id: str
    name: str
    type: WeaponType
    vehicle_id: str | None = None
    factions: set[Faction] = Field(min_length=1)
    magnification: int | None = None

    # @computed_field(repr=False)  # type: ignore[prop-decorator]
    @cached_property
    def vehicle(self) -> "Vehicle | None":
        from hllrcon.data.vehicles import Vehicle  # noqa: PLC0415

        if self.vehicle_id:
            return Vehicle.by_id(self.vehicle_id)
        return None

    # --- American weapons ---

    @class_cached_property
    @classmethod
    def M1_GARAND(cls) -> "Weapon":
        """*M1 GARAND*"""
        return cls(
            id="M1 GARAND",
            name="M1 Garand",
            factions={Faction.US},
            type=WeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def M1_CARBINE(cls) -> "Weapon":
        """*M1 CARBINE*"""
        return cls(
            id="M1 CARBINE",
            name="M1 Carbine",
            factions={Faction.US},
            type=WeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def M1A1_THOMPSON(cls) -> "Weapon":
        """*M1A1 THOMPSON*"""
        return cls(
            id="M1A1 THOMPSON",
            name="M1A1 Thompson",
            factions={Faction.US},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M3_GREASE_GUN(cls) -> "Weapon":
        """*M3 GREASE GUN*"""
        return cls(
            id="M3 GREASE GUN",
            name="M3 Grease Gun",
            factions={Faction.US},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M1918A2_BAR(cls) -> "Weapon":
        """*M1918A2 BAR*"""
        return cls(
            id="M1918A2 BAR",
            name="M1918A2 BAR",
            factions={Faction.US},
            type=WeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def BROWNING_M1919(cls) -> "Weapon":
        """*BROWNING M1919*"""
        return cls(
            id="BROWNING M1919",
            name="M1919 Browning",
            factions={Faction.US},
            type=WeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M1903_SPRINGFIELD_SCOPED_4X(cls) -> "Weapon":
        """*M1903 SPRINGFIELD*"""
        return cls(
            id="M1903 SPRINGFIELD",
            name="M1903 Springfield",
            factions={Faction.US},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def M97_TRENCH_GUN(cls) -> "Weapon":
        """*M97 TRENCH GUN*"""
        return cls(
            id="M97 TRENCH GUN",
            name="M97 Trench Gun",
            factions={Faction.US},
            type=WeaponType.SHOTGUN,
        )

    @class_cached_property
    @classmethod
    def COLT_M1911(cls) -> "Weapon":
        """*COLT M1911*"""
        return cls(
            id="COLT M1911",
            name="Colt M1911",
            factions={Faction.US},
            type=WeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def M3_KNIFE(cls) -> "Weapon":
        """*M3 KNIFE*"""
        return cls(
            id="M3 KNIFE",
            name="M3 Knife",
            factions={Faction.US},
            type=WeaponType.MELEE,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE(cls) -> "Weapon":
        """*SATCHEL*"""
        return cls(
            id="SATCHEL",
            name="Satchel Charge",
            factions={Faction.US, Faction.GER, Faction.DAK},
            type=WeaponType.SATCHEL,
        )

    @class_cached_property
    @classmethod
    def MK2_GRENADE(cls) -> "Weapon":
        """*MK2 GRENADE*"""
        return cls(
            id="MK2 GRENADE",
            name="Mk 2 Grenade",
            factions={Faction.US},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def M2_FLAMETHROWER(cls) -> "Weapon":
        """*M2 FLAMETHROWER*"""
        return cls(
            id="M2 FLAMETHROWER",
            name="M2 Flamethrower",
            factions={Faction.US},
            type=WeaponType.FLAMETHROWER,
        )

    @class_cached_property
    @classmethod
    def BAZOOKA(cls) -> "Weapon":
        """*BAZOOKA*"""
        return cls(
            id="BAZOOKA",
            name="Bazooka",
            factions={Faction.US},
            type=WeaponType.ROCKET_LAUNCHER,
        )

    @class_cached_property
    @classmethod
    def M2_AP_MINE(cls) -> "Weapon":
        """*M2 AP MINE*"""
        return cls(
            id="M2 AP MINE",
            name="M2 AP Mine",
            factions={Faction.US},
            type=WeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def M1A1_AT_MINE(cls) -> "Weapon":
        """*M1A1 AT MINE*"""
        return cls(
            id="M1A1 AT MINE",
            name="M1A1 AT Mine",
            factions={Faction.US},
            type=WeaponType.AT_MINE,
        )

    @class_cached_property
    @classmethod
    def FLARE_GUN(cls) -> "Weapon":
        """*FLARE GUN*"""
        return cls(
            id="FLARE GUN",
            name="Flare Gun",
            factions={Faction.US, Faction.GER, Faction.DAK, Faction.SOV},
            type=WeaponType.FLARE_GUN,
        )

    @class_cached_property
    @classmethod
    def V_57MM_CANNON__M1_57(cls) -> "Weapon":
        """*57MM CANNON [M1 57mm]*"""
        return cls(
            id="57MM CANNON [M1 57mm]",
            name="57mm Cannon",
            vehicle_id="M1 57mm",
            factions={Faction.US},
            type=WeaponType.AT_GUN,
        )

    @class_cached_property
    @classmethod
    def V_155MM_HOWITZER__M114(cls) -> "Weapon":
        """*155MM HOWITZER [M114]*"""
        return cls(
            id="155MM HOWITZER [M114]",
            name="155mm Howitzer",
            vehicle_id="M114",
            factions={Faction.US},
            type=WeaponType.ARTILLERY,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M8_GREYHOUND(cls) -> "Weapon":
        """*M8 Greyhound*"""
        return cls(
            id="M8 Greyhound",
            name="Roadkill",
            vehicle_id="M8 Greyhound",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__STUART_M5A1(cls) -> "Weapon":
        """*Stuart M5A1*"""
        return cls(
            id="Stuart M5A1",
            name="Roadkill",
            vehicle_id="Stuart M5A1",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SHERMAN_M4A3_75W(cls) -> "Weapon":
        """*Sherman M4A3(75)W*"""
        return cls(
            id="Sherman M4A3(75)W",
            name="Roadkill",
            vehicle_id="Sherman M4A3(75)W",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SHERMAN_M4A3E2(cls) -> "Weapon":
        """*Sherman M4A3E2*"""
        return cls(
            id="Sherman M4A3E2",
            name="Roadkill",
            vehicle_id="Sherman M4A3E2",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SHERMAN_M4A3E2_76(cls) -> "Weapon":
        """*Sherman M4A3E2(76)*"""
        return cls(
            id="Sherman M4A3E2(76)",
            name="Roadkill",
            vehicle_id="Sherman M4A3E2(76)",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GMC_CCKW_353_SUPPLY(cls) -> "Weapon":
        """*GMC CCKW 353 (Supply)*"""
        return cls(
            id="GMC CCKW 353 (Supply)",
            name="Roadkill",
            vehicle_id="GMC CCKW 353 (Supply)",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GMC_CCKW_353_TRANSPORT(cls) -> "Weapon":
        """*GMC CCKW 353 (Transport)*"""
        return cls(
            id="GMC CCKW 353 (Transport)",
            name="Roadkill",
            vehicle_id="GMC CCKW 353 (Transport)",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M3_HALF_TRACK(cls) -> "Weapon":
        """*M3 Half-track*"""
        return cls(
            id="M3 Half-track",
            name="Roadkill",
            vehicle_id="M3 Half-track",
            factions={Faction.US, Faction.SOV, Faction.CW, Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__JEEP_WILLYS(cls) -> "Weapon":
        """*Jeep Willys*"""
        return cls(
            id="Jeep Willys",
            name="Roadkill",
            vehicle_id="Jeep Willys",
            factions={Faction.US},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_M6_37MM__M8_GREYHOUND(cls) -> "Weapon":
        """*M6 37mm [M8 Greyhound]*"""
        return cls(
            id="M6 37mm [M8 Greyhound]",
            name="37mm Cannon",
            vehicle_id="M8 Greyhound",
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M8_GREYHOUND(cls) -> "Weapon":
        """*COAXIAL M1919 [M8 Greyhound]*"""
        return cls(
            id="COAXIAL M1919 [M8 Greyhound]",
            name="M1919 Browning",
            vehicle_id="M8 Greyhound",
            factions={Faction.US},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__STUART_M5A1(cls) -> "Weapon":
        """*37MM CANNON [Stuart M5A1]*"""
        return cls(
            id="37MM CANNON [Stuart M5A1]",
            name="37mm Cannon",
            vehicle_id="Stuart M5A1",
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__STUART_M5A1(cls) -> "Weapon":
        """*COAXIAL M1919 [Stuart M5A1]*"""
        return cls(
            id="COAXIAL M1919 [Stuart M5A1]",
            name="M1919 Browning",
            vehicle_id="Stuart M5A1",
            factions={Faction.US},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__STUART_M5A1(cls) -> "Weapon":
        """*HULL M1919 [Stuart M5A1]*"""
        return cls(
            id="HULL M1919 [Stuart M5A1]",
            name="M1919 Browning",
            vehicle_id="Stuart M5A1",
            factions={Faction.US},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SHERMAN_M4A3_75W(cls) -> "Weapon":
        """*75MM CANNON [Sherman M4A3(75)W]*"""
        return cls(
            id="75MM CANNON [Sherman M4A3(75)W]",
            name="75mm Cannon",
            vehicle_id="Sherman M4A3(75)W",
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3_75W(cls) -> "Weapon":
        """*COAXIAL M1919 [Sherman M4A3(75)W]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3(75)W]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3(75)W",
            factions={Faction.US},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3_75W(cls) -> "Weapon":
        """`HULL M1919 [Sherman M4A3(75)W]`"""
        return cls(
            id="HULL M1919 [Sherman M4A3(75)W]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3(75)W",
            factions={Faction.US},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_75MM_M3_GUN__SHERMAN_M4A3E2(cls) -> "Weapon":
        """*75MM M3 GUN [Sherman M4A3E2]*"""
        return cls(
            id="75MM M3 GUN [Sherman M4A3E2]",
            name="75mm Cannon",
            vehicle_id="Sherman M4A3E2",
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3E2(cls) -> "Weapon":
        """*COAXIAL M1919 [Sherman M4A3E2]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3E2]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2",
            factions={Faction.US},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3E2(cls) -> "Weapon":
        """*HULL M1919 [Sherman M4A3E2]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3E2]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2",
            factions={Faction.US},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_76MM_M1_GUN__SHERMAN_M4A3E2_76(cls) -> "Weapon":
        """*76MM M1 GUN [Sherman M4A3E2(76)]*"""
        return cls(
            id="76MM M1 GUN [Sherman M4A3E2(76)]",
            name="76mm Cannon",
            vehicle_id="Sherman M4A3E2(76)",
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3E2_76(cls) -> "Weapon":
        """*COAXIAL M1919 [Sherman M4A3E2(76)]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3E2(76)]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2(76)",
            factions={Faction.US},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3E2_76(cls) -> "Weapon":
        """*HULL M1919 [Sherman M4A3E2(76)]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3E2(76)]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2(76)",
            factions={Faction.US},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_M2_BROWNING__M3_HALF_TRACK(cls) -> "Weapon":
        """*M2 Browning [M3 Half-track]*"""
        return cls(
            id="M2 Browning [M3 Half-track]",
            name="M2 Browning",
            vehicle_id="M3 Half-track",
            factions={Faction.US, Faction.SOV, Faction.CW, Faction.B8A},
            type=WeaponType.MOUNTED_MG,
        )

    @class_cached_property
    @classmethod
    def V_57MM_CANNON__UNKNOWN(cls) -> "Weapon":
        """*57MM CANNON*"""
        return cls(
            id="57MM CANNON",
            name="57mm Cannon",
            vehicle_id=None,
            factions={Faction.US, Faction.SOV},
            type=WeaponType.AT_GUN,
        )

    @class_cached_property
    @classmethod
    def V_76MM_M1_GUN__UNKNOWN(cls) -> "Weapon":
        """*76MM M1 GUN*"""
        return cls(
            id="76MM M1 GUN",
            name="76mm Cannon",
            vehicle_id=None,
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_M3_GUN__UNKNOWN(cls) -> "Weapon":
        """*75MM M3 GUN*"""
        return cls(
            id="75MM M3 GUN",
            name="75mm Cannon",
            vehicle_id=None,
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__UNKNOWN(cls) -> "Weapon":
        """*75MM CANNON*"""
        return cls(
            id="75MM CANNON",
            name="75mm Cannon",
            vehicle_id=None,
            factions={Faction.US, Faction.GER, Faction.DAK},
            type=WeaponType.UNKNOWN,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__UNKNOWN(cls) -> "Weapon":
        """*37MM CANNON*"""
        return cls(
            id="37MM CANNON",
            name="37mm Cannon",
            vehicle_id=None,
            factions={Faction.US, Faction.GB, Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_M6_37MM__UNKNOWN(cls) -> "Weapon":
        """*M6 37MM*"""
        return cls(
            id="M6 37MM",
            name="M6 37mm",
            vehicle_id=None,
            factions={Faction.US},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__UNKNOWN(cls) -> "Weapon":
        """*COAXIAL M1919*"""
        return cls(
            id="COAXIAL M1919",
            name="M1919 Browning",
            vehicle_id=None,
            factions={Faction.US, Faction.GB, Faction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__UNKNOWN(cls) -> "Weapon":
        """*HULL M1919*"""
        return cls(
            id="HULL M1919",
            name="M1919 Browning",
            vehicle_id=None,
            factions={Faction.US, Faction.GB, Faction.CW},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_M2_BROWNING__UNKNOWN(cls) -> "Weapon":
        """*M2 Browning*"""
        return cls(
            id="M2 Browning",
            name="M2 Browning",
            vehicle_id=None,
            factions={Faction.US, Faction.SOV, Faction.CW, Faction.B8A},
            type=WeaponType.MOUNTED_MG,
        )

    # --- German weapons ---

    @class_cached_property
    @classmethod
    def KARABINER_98K(cls) -> "Weapon":
        """*KARABINER 98K*"""
        return cls(
            id="KARABINER 98K",
            name="Karabiner 98k",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def GEWEHR_43(cls) -> "Weapon":
        """*GEWEHR 43*"""
        return cls(
            id="GEWEHR 43",
            name="G43",
            factions={Faction.GER},
            type=WeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def STG44(cls) -> "Weapon":
        """*STG44*"""
        return cls(
            id="STG44",
            name="STG44",
            factions={Faction.GER},
            type=WeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def FG42(cls) -> "Weapon":
        """*FG42*"""
        return cls(
            id="FG42",
            name="FG42",
            factions={Faction.GER},
            type=WeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def MP40(cls) -> "Weapon":
        """*MP40*"""
        return cls(
            id="MP40",
            name="MP40",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def MG34(cls) -> "Weapon":
        """*MG34*"""
        return cls(
            id="MG34",
            name="MG34",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def MG42(cls) -> "Weapon":
        """*MG42*"""
        return cls(
            id="MG42",
            name="MG42",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def FLAMMENWERFER_41(cls) -> "Weapon":
        """*FLAMMENWERFER 41*"""
        return cls(
            id="FLAMMENWERFER 41",
            name="Flammenwerfer 41",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.FLAMETHROWER,
        )

    @class_cached_property
    @classmethod
    def KARABINER_98K_SCOPED_8X(cls) -> "Weapon":
        """*KARABINER 98K x8*"""
        return cls(
            id="KARABINER 98K x8",
            name="Karabiner 98k",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=8,
        )

    @class_cached_property
    @classmethod
    def FG42_SCOPED_4X(cls) -> "Weapon":
        """*FG42 x4*"""
        return cls(
            id="FG42 x4",
            name="FG42",
            factions={Faction.GER},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def LUGER_P08(cls) -> "Weapon":
        """*LUGER P08*"""
        return cls(
            id="LUGER P08",
            name="Luger P08",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def WALTHER_P38(cls) -> "Weapon":
        """*WALTHER P38*"""
        return cls(
            id="WALTHER P38",
            name="Walther P38",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def FELDSPATEN(cls) -> "Weapon":
        """*FELDSPATEN*"""
        return cls(
            id="FELDSPATEN",
            name="Feldspaten",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.MELEE,
        )

    # SATCHEL

    @class_cached_property
    @classmethod
    def M24_STIELHANDGRANATE(cls) -> "Weapon":
        """*M24 STIELHANDGRANATE*"""
        return cls(
            id="M24 STIELHANDGRANATE",
            name="M24 Stielhandgranate",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def M43_STIELHANDGRANATE(cls) -> "Weapon":
        """*M43 STIELHANDGRANATE*"""
        return cls(
            id="M43 STIELHANDGRANATE",
            name="M43 Stielhandgranate",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def PANZERSCHRECK(cls) -> "Weapon":
        """*PANZERSCHRECK*"""
        return cls(
            id="PANZERSCHRECK",
            name="Panzerschreck",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROCKET_LAUNCHER,
        )

    @class_cached_property
    @classmethod
    def S_MINE(cls) -> "Weapon":
        """*S-MINE*"""
        return cls(
            id="S-MINE",
            name="S-Mine",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def TELLERMINE_43(cls) -> "Weapon":
        """*TELLERMINE 43*"""
        return cls(
            id="TELLERMINE 43",
            name="Tellermine 43",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.AT_MINE,
        )

    # FLARE GUN

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__PAK_40(cls) -> "Weapon":
        """*75MM CANNON [PAK 40]*"""
        return cls(
            id="75MM CANNON [PAK 40]",
            name="75mm Cannon",
            vehicle_id="PAK 40",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.AT_GUN,
        )

    @class_cached_property
    @classmethod
    def V_150MM_HOWITZER__SFH_18(cls) -> "Weapon":
        """*150MM HOWITZER [sFH 18]*"""
        return cls(
            id="150MM HOWITZER [sFH 18]",
            name="150mm Howitzer",
            vehicle_id="sFH 18",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ARTILLERY,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_234_PUMA(cls) -> "Weapon":
        """*Sd.Kfz.234 Puma*"""
        return cls(
            id="Sd.Kfz.234 Puma",
            name="Roadkill",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_121_LUCHS(cls) -> "Weapon":
        """*Sd.Kfz.121 Luchs*"""
        return cls(
            id="Sd.Kfz.121 Luchs",
            name="Roadkill",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_161_PANZER_IV(cls) -> "Weapon":
        """*Sd.Kfz.161 Panzer IV*"""
        return cls(
            id="Sd.Kfz.161 Panzer IV",
            name="Roadkill",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_171_PANTHER(cls) -> "Weapon":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Roadkill",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_181_TIGER_1(cls) -> "Weapon":
        """*Sd.Kfz.181 Tiger 1*"""
        return cls(
            id="Sd.Kfz.181 Tiger 1",
            name="Roadkill",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__OPEL_BLITZ_SUPPLY(cls) -> "Weapon":
        """*Opel Blitz (Supply)*"""
        return cls(
            id="Opel Blitz (Supply)",
            name="Roadkill",
            vehicle_id="Opel Blitz (Supply)",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__OPEL_BLITZ_TRANSPORT(cls) -> "Weapon":
        """*Opel Blitz (Transport)*"""
        return cls(
            id="Opel Blitz (Transport)",
            name="Roadkill",
            vehicle_id="Opel Blitz (Transport)",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_251_HALF_TRACK(cls) -> "Weapon":
        """*Sd.Kfz 251 Half-track*"""
        return cls(
            id="Sd.Kfz 251 Half-track",
            name="Roadkill",
            vehicle_id="Sd.Kfz 251 Half-track",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__KUBELWAGEN(cls) -> "Weapon":
        """*Kubelwagen*"""
        return cls(
            id="Kubelwagen",
            name="Roadkill",
            vehicle_id="Kubelwagen",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_50MM_KWK_91_1__SD_KFZ_234_PUMA(cls) -> "Weapon":
        """*50mm KwK 39/1 [Sd.Kfz.234 Puma]*"""
        return cls(
            id="50mm KwK 39/1 [Sd.Kfz.234 Puma]",
            name="50mm KwK 39/1",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_234_PUMA(cls) -> "Weapon":
        """*COAXIAL MG34 [Sd.Kfz.234 Puma]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.234 Puma]",
            name="MG34",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_20MM_KWK_30__SD_KFZ_121_LUCHS(cls) -> "Weapon":
        """*20MM KWK 30 [Sd.Kfz.121 Luchs]*"""
        return cls(
            id="20MM KWK 30 [Sd.Kfz.121 Luchs]",
            name="20mm KwK 30",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_121_LUCHS(cls) -> "Weapon":
        """*COAXIAL MG34 [Sd.Kfz.121 Luchs]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.121 Luchs]",
            name="MG34",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SD_KFZ_161_PANZER_IV(cls) -> "Weapon":
        """*75MM CANNON [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="75MM CANNON [Sd.Kfz.161 Panzer IV]",
            name="75mm Cannon",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_161_PANZER_IV(cls) -> "Weapon":
        """*COAXIAL MG34 [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.161 Panzer IV]",
            name="MG34",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SD_KFZ_161_PANZER_IV(cls) -> "Weapon":
        """*HULL MG34 [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.161 Panzer IV]",
            name="MG34",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SD_KFZ_171_PANTHER(cls) -> "Weapon":
        """*75MM CANNON [Sd.Kfz.171 Panther]*"""
        return cls(
            id="75MM CANNON [Sd.Kfz.171 Panther]",
            name="75mm Cannon",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_171_PANTHER(cls) -> "Weapon":
        """*COAXIAL MG34 [Sd.Kfz.171 Panther]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.171 Panther]",
            name="MG34",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SD_KFZ_171_PANTHER(cls) -> "Weapon":
        """*HULL MG34 [Sd.Kfz.171 Panther]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.171 Panther]",
            name="MG34",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_88MM_KWK_36_L_56__SD_KFZ_181_TIGER_1(cls) -> "Weapon":
        """*88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]",
            name="88mm KwK 36 L/56",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_181_TIGER_1(cls) -> "Weapon":
        """*COAXIAL MG34 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.181 Tiger 1]",
            name="MG34",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SD_KFZ_181_TIGER_1(cls) -> "Weapon":
        """*HULL MG34 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.181 Tiger 1]",
            name="MG34",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_MG_42__SD_KFZ_251_HALF_TRACK(cls) -> "Weapon":
        """*MG 42 [Sd.Kfz 251 Half-track]*"""
        return cls(
            id="MG 42 [Sd.Kfz 251 Half-track]",
            name="MG42",
            vehicle_id="Sd.Kfz 251 Half-track",
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.MOUNTED_MG,
        )

    @class_cached_property
    @classmethod
    def V_50MM_KWK_39_1__UNKNOWN(cls) -> "Weapon":
        """*50MM KWK 39/1*"""
        return cls(
            id="50MM KWK 39/1",
            name="50mm KwK 39/1",
            vehicle_id=None,
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_20MM_KWK_30__UNKNOWN(cls) -> "Weapon":
        """*20MM KWK 30*"""
        return cls(
            id="20MM KWK 30",
            name="20mm KwK 30",
            vehicle_id=None,
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_88MM_KWK_36_L_56__UNKNOWN(cls) -> "Weapon":
        """*88 KWK 36 L/56*"""
        return cls(
            id="88 KWK 36 L/56",
            name="88mm KwK 36 L/56",
            vehicle_id=None,
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__UNKNOWN(cls) -> "Weapon":
        """*COAXIAL MG34*"""
        return cls(
            id="COAXIAL MG34",
            name="MG34",
            vehicle_id=None,
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__UNKNOWN(cls) -> "Weapon":
        """*HULL MG34*"""
        return cls(
            id="HULL MG34",
            name="MG34",
            vehicle_id=None,
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_MG_42__UNKNOWN(cls) -> "Weapon":
        """*MG 42*"""
        return cls(
            id="MG 42",
            name="MG42",
            vehicle_id=None,
            factions={Faction.GER, Faction.DAK},
            type=WeaponType.MOUNTED_MG,
        )

    # --- Soviet weapons ---

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_1891(cls) -> "Weapon":
        """*MOSIN NAGANT 1891*"""
        return cls(
            id="MOSIN NAGANT 1891",
            name="Mosin-Nagant 1891",
            factions={Faction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_91_30(cls) -> "Weapon":
        """*MOSIN NAGANT 91/30*"""
        return cls(
            id="MOSIN NAGANT 91/30",
            name="Mosin-Nagant 91/30",
            factions={Faction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_M38(cls) -> "Weapon":
        """*MOSIN NAGANT M38*"""
        return cls(
            id="MOSIN NAGANT M38",
            name="Mosin-Nagant M38",
            factions={Faction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def SVT_40(cls) -> "Weapon":
        """*SVT40*"""
        return cls(
            id="SVT40",
            name="SVT-40",
            factions={Faction.SOV},
            type=WeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def PPSH_41(cls) -> "Weapon":
        """*PPSH 41*"""
        return cls(
            id="PPSH 41",
            name="PPSh-41",
            factions={Faction.SOV},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def PPSH_41_WITH_DRUM(cls) -> "Weapon":
        """*PPSH 41 W/DRUM*"""
        return cls(
            id="PPSH 41 W/DRUM",
            name="PPSh-41 with Drum",
            factions={Faction.SOV},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def DP_27(cls) -> "Weapon":
        """*DP-27*"""
        return cls(
            id="DP-27",
            name="DP-27",
            factions={Faction.SOV},
            type=WeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_91_30_SCOPED_4X(cls) -> "Weapon":
        """*SCOPED MOSIN NAGANT 91/30*"""
        return cls(
            id="SCOPED MOSIN NAGANT 91/30",
            name="Mosin-Nagant 91/30",
            factions={Faction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def SVT_40_SCOPED_4X(cls) -> "Weapon":
        """*SCOPED SVT40*"""
        return cls(
            id="SCOPED SVT40",
            name="SVT-40",
            factions={Faction.SOV},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def NAGANT_M1895(cls) -> "Weapon":
        """*NAGANT M1895*"""
        return cls(
            id="NAGANT M1895",
            name="Nagant M1895",
            factions={Faction.SOV},
            type=WeaponType.REVOLVER,
        )

    @class_cached_property
    @classmethod
    def TOKAREV_TT33(cls) -> "Weapon":
        """*TOKAREV TT33*"""
        return cls(
            id="TOKAREV TT33",
            name="Tokarev TT-33",
            factions={Faction.SOV},
            type=WeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def MPL_50_SPADE(cls) -> "Weapon":
        """*MPL-50 SPADE*"""
        return cls(
            id="MPL-50 SPADE",
            name="MPL-50 Spade",
            factions={Faction.SOV},
            type=WeaponType.MELEE,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE_SOVIET(cls) -> "Weapon":
        """*SATCHEL CHARGE*"""
        return cls(
            id="SATCHEL CHARGE",
            name="Satchel Charge",
            factions={Faction.SOV},
            type=WeaponType.SATCHEL,
        )

    @class_cached_property
    @classmethod
    def RG_42_GRENADE(cls) -> "Weapon":
        """*RG-42 GRENADE*"""
        return cls(
            id="RG-42 GRENADE",
            name="RG-42 Grenade",
            factions={Faction.SOV},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def MOLOTOV(cls) -> "Weapon":
        """*MOLOTOV*"""
        return cls(
            id="MOLOTOV",
            name="Molotov",
            factions={Faction.SOV},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def PTRS_41(cls) -> "Weapon":
        """*PTRS-41*"""
        return cls(
            id="PTRS-41",
            name="PTRS-41",
            factions={Faction.SOV},
            type=WeaponType.ANTI_MATERIEL_RIFLE,
        )

    @class_cached_property
    @classmethod
    def POMZ_AP_MINE(cls) -> "Weapon":
        """*POMZ AP MINE*"""
        return cls(
            id="POMZ AP MINE",
            name="POMZ AP Mine",
            factions={Faction.SOV},
            type=WeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def TM_35_AT_MINE(cls) -> "Weapon":
        """*TM-35 AT MINE*"""
        return cls(
            id="TM-35 AT MINE",
            name="TM-35 AT Mine",
            factions={Faction.SOV},
            type=WeaponType.AT_MINE,
        )

    # FLARE GUN

    @class_cached_property
    @classmethod
    def V_57MM_CANNON__ZIS_2(cls) -> "Weapon":
        """*57MM CANNON [ZiS-2]*"""
        return cls(
            id="57MM CANNON [ZiS-2]",
            name="57mm Cannon",
            vehicle_id="ZiS-2",
            factions={Faction.SOV},
            type=WeaponType.AT_GUN,
        )

    @class_cached_property
    @classmethod
    def V_122MM_HOWITZER__M1938_M_30(cls) -> "Weapon":
        """*122MM HOWITZER [M1938 (M-30)]*"""
        return cls(
            id="122MM HOWITZER [M1938 (M-30)]",
            name="122mm Howitzer",
            vehicle_id="M1938 (M-30)",
            factions={Faction.SOV},
            type=WeaponType.ARTILLERY,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BA_10(cls) -> "Weapon":
        """*BA-10*"""
        return cls(
            id="BA-10",
            name="Roadkill",
            vehicle_id="BA-10",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__T70(cls) -> "Weapon":
        """*T70*"""
        return cls(
            id="T70",
            name="Roadkill",
            vehicle_id="T70",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__T34_76(cls) -> "Weapon":
        """*T34/76*"""
        return cls(
            id="T34/76",
            name="Roadkill",
            vehicle_id="T34/76",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__IS_1(cls) -> "Weapon":
        """*IS-1*"""
        return cls(
            id="IS-1",
            name="Roadkill",
            vehicle_id="IS-1",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__ZIS_5_SUPPLY(cls) -> "Weapon":
        """*ZIS-5 (Supply)*"""
        return cls(
            id="ZIS-5 (Supply)",
            name="Roadkill",
            vehicle_id="ZIS-5 (Supply)",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__ZIS_5_TRANSPORT(cls) -> "Weapon":
        """*ZIS-5 (Transport)*"""
        return cls(
            id="ZIS-5 (Transport)",
            name="Roadkill",
            vehicle_id="ZIS-5 (Transport)",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    # M3 Half-track,

    @class_cached_property
    @classmethod
    def V_ROADKILL__GAZ_67(cls) -> "Weapon":
        """*GAZ-67*"""
        return cls(
            id="GAZ-67",
            name="Roadkill",
            vehicle_id="GAZ-67",
            factions={Faction.SOV},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_19_K_45MM__BA_10(cls) -> "Weapon":
        """*19-K 45MM [BA-10]*"""
        return cls(
            id="19-K 45MM [BA-10]",
            name="45mm M1932",
            vehicle_id="BA-10",
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__BA_10(cls) -> "Weapon":
        """*COAXIAL DT [BA-10]*"""
        return cls(
            id="COAXIAL DT [BA-10]",
            name="DT",
            vehicle_id="BA-10",
            factions={Faction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_45MM_M1937__T70(cls) -> "Weapon":
        """*45MM M1937 [T70]*"""
        return cls(
            id="45MM M1937 [T70]",
            name="45mm M1937",
            vehicle_id="T70",
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__T70(cls) -> "Weapon":
        """*COAXIAL DT [T70]*"""
        return cls(
            id="COAXIAL DT [T70]",
            name="DT",
            vehicle_id="T70",
            factions={Faction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_76MM_ZIS_5__T34_76(cls) -> "Weapon":
        """*76MM ZiS-5 [T34/76]*"""
        return cls(
            id="76MM ZiS-5 [T34/76]",
            name="76mm M1940",
            vehicle_id="T34/76",
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__T34_76(cls) -> "Weapon":
        """*COAXIAL DT [T34/76]*"""
        return cls(
            id="COAXIAL DT [T34/76]",
            name="DT",
            vehicle_id="T34/76",
            factions={Faction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__T34_76(cls) -> "Weapon":
        """*HULL DT [T34/76]*"""
        return cls(
            id="HULL DT [T34/76]",
            name="DT",
            vehicle_id="T34/76",
            factions={Faction.SOV},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_D_5T_85MM__IS_1(cls) -> "Weapon":
        """*D-5T 85MM [IS-1]*"""
        return cls(
            id="D-5T 85MM [IS-1]",
            name="D-5T 85mm",
            vehicle_id="IS-1",
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__IS_1(cls) -> "Weapon":
        """*COAXIAL DT [IS-1]*"""
        return cls(
            id="COAXIAL DT [IS-1]",
            name="DT",
            vehicle_id="IS-1",
            factions={Faction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__IS_1(cls) -> "Weapon":
        """*HULL DT [IS-1]*"""
        return cls(
            id="HULL DT [IS-1]",
            name="DT",
            vehicle_id="IS-1",
            factions={Faction.SOV},
            type=WeaponType.TANK_HULL_MG,
        )

    # M2 Browning [M3 Half-track]

    @class_cached_property
    @classmethod
    def V_19_K_45MM__UNKNOWN(cls) -> "Weapon":
        """*19-K 45MM*"""
        return cls(
            id="19-K 45MM",
            name="45mm M1932",
            vehicle_id=None,
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_45MM_M1937__UNKNOWN(cls) -> "Weapon":
        """*45MM M1937*"""
        return cls(
            id="45MM M1937",
            name="45mm M1937",
            vehicle_id=None,
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_76MM_ZIS_5__UNKNOWN(cls) -> "Weapon":
        """*76MM ZiS-5*"""
        return cls(
            id="76MM ZiS-5",
            name="76mm M1940",
            vehicle_id=None,
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_D_5T_85MM__UNKNOWN(cls) -> "Weapon":
        """*D-5T 85MM*"""
        return cls(
            id="D-5T 85MM",
            name="D-5T 85mm",
            vehicle_id=None,
            factions={Faction.SOV},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__UNKNOWN(cls) -> "Weapon":
        """*COAXIAL DT*"""
        return cls(
            id="COAXIAL DT",
            name="COAXIAL DT",
            vehicle_id=None,
            factions={Faction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__UNKNOWN(cls) -> "Weapon":
        """*HULL DT*"""
        return cls(
            id="HULL DT",
            name="HULL DT",
            vehicle_id=None,
            factions={Faction.SOV},
            type=WeaponType.TANK_HULL_MG,
        )

    # --- British weapons ---

    @class_cached_property
    @classmethod
    def SMLE_NO_1_MK_III(cls) -> "Weapon":
        """*SMLE No.1 Mk III*"""
        return cls(
            id="SMLE No.1 Mk III",
            name="SMLE Mk III",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def RIFLE_NO_4_MK_I(cls) -> "Weapon":
        """*Rifle No.4 Mk I*"""
        return cls(
            id="Rifle No.4 Mk I",
            name="No.4 Rifle Mk I",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN(cls) -> "Weapon":
        """*Sten Gun*"""
        return cls(
            id="Sten Gun",
            name="Sten Mk II",
            factions={Faction.B8A},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN_MK_II(cls) -> "Weapon":
        """*Sten Gun Mk.II*"""
        return cls(
            id="Sten Gun Mk.II",
            name="Sten Mk II",
            factions={Faction.CW},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN_MK_V(cls) -> "Weapon":
        """*Sten Gun Mk.V*"""
        return cls(
            id="Sten Gun Mk.V",
            name="Sten Mk V",
            factions={Faction.CW},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M1928A1_THOMPSON(cls) -> "Weapon":
        """*M1928A1 THOMPSON*"""
        return cls(
            id="M1928A1 THOMPSON",
            name="M1928A1 Thompson",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def BREN_GUN(cls) -> "Weapon":
        """*Bren Gun*"""
        return cls(
            id="Bren Gun",
            name="Bren Gun",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def LEWIS_GUN(cls) -> "Weapon":
        """*Lewis Gun*"""
        return cls(
            id="Lewis Gun",
            name="Lewis Gun",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def LIFEBUOY_FLAMETHROWER(cls) -> "Weapon":
        """*FLAMETHROWER*"""
        return cls(
            id="FLAMETHROWER",
            name="Lifebuoy Flamethrower",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.FLAMETHROWER,
        )

    @class_cached_property
    @classmethod
    def RIFLE_NO_4_MK_I_SCOPED_8X(cls) -> "Weapon":
        """*Rifle No.4 Mk I Sniper*"""
        return cls(
            id="Rifle No.4 Mk I Sniper",
            name="No.4 Rifle Mk I",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=8,
        )

    @class_cached_property
    @classmethod
    def WEBLEY_MK_VI(cls) -> "Weapon":
        """*Webley MK VI*"""
        return cls(
            id="Webley MK VI",
            name="Webley Mk IV",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.REVOLVER,
        )

    @class_cached_property
    @classmethod
    def FAIRBAIRN_SYKES(cls) -> "Weapon":
        """*Fairbairn–Sykes*"""  # noqa: RUF002
        return cls(
            id="Fairbairn–Sykes",  # noqa: RUF001
            name="Fairbairn-Sykes",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.MELEE,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE_COMMONWEALTH(cls) -> "Weapon":
        """*Satchel*"""
        return cls(
            id="Satchel",
            name="Satchel Charge",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.SATCHEL,
        )

    @class_cached_property
    @classmethod
    def MILLS_BOMB(cls) -> "Weapon":
        """*Mills Bomb*"""
        return cls(
            id="Mills Bomb",
            name="Mills Bomb",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def GAMMON_BOMB(cls) -> "Weapon":
        """*No.82 Grenade*"""
        return cls(
            id="No.82 Grenade",
            name="Gammon Bomb",
            factions={Faction.CW},
            type=WeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def PIAT(cls) -> "Weapon":
        """*PIAT*"""
        return cls(
            id="PIAT",
            name="PIAT",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ROCKET_LAUNCHER,
        )

    @class_cached_property
    @classmethod
    def BOYS_ANTI_TANK_RIFLE(cls) -> "Weapon":
        """*Boys Anti-tank Rifle*"""
        return cls(
            id="Boys Anti-tank Rifle",
            name="Boys AT Rifle",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ANTI_MATERIEL_RIFLE,
        )

    @class_cached_property
    @classmethod
    def AP_SHRAPNEL_MINE_MK_II(cls) -> "Weapon":
        """*A.P. Shrapnel Mine Mk II*"""
        return cls(
            id="A.P. Shrapnel Mine Mk II",
            name="AP Shrapnel Mine Mk II",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def AT_MINE_GS_MK_V(cls) -> "Weapon":
        """*A.T. Mine G.S. Mk V*"""
        return cls(
            id="A.T. Mine G.S. Mk V",
            name="AT Mine G.S. Mk V",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.AT_MINE,
        )

    @class_cached_property
    @classmethod
    def NO_2_MK_V_FLARE_GUN(cls) -> "Weapon":
        """*No.2 Mk 5 Flare Pistol*"""
        return cls(
            id="No.2 Mk 5 Flare Pistol",
            name="No.2 Mk V Flare Gun",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.FLARE_GUN,
        )

    @class_cached_property
    @classmethod
    def V_QF_6_POUNDER__QF_6_POUNDER(cls) -> "Weapon":
        """*QF 6-POUNDER [QF 6-Pounder]*"""
        return cls(
            id="QF 6-POUNDER [QF 6-Pounder]",
            name="57mm Cannon",
            vehicle_id="QF 6-Pounder",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.AT_GUN,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__QF_25_POUNDER(cls) -> "Weapon":
        """*QF 25-POUNDER [QF 25-Pounder]*"""
        return cls(
            id="QF 25-POUNDER [QF 25-Pounder]",
            name="88mm Howitzer",
            vehicle_id="QF 25-Pounder",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ARTILLERY,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__DAIMLER(cls) -> "Weapon":
        """*Daimler*"""
        return cls(
            id="Daimler",
            name="Roadkill",
            vehicle_id="Daimler",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__TETRARCH(cls) -> "Weapon":
        """*Tetrarch*"""
        return cls(
            id="Tetrarch",
            name="Roadkill",
            vehicle_id="Tetrarch",
            factions={Faction.CW},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M3_STUART_HONEY(cls) -> "Weapon":
        """*M3 Stuart Honey*"""
        return cls(
            id="M3 Stuart Honey",
            name="Roadkill",
            vehicle_id="M3 Stuart Honey",
            factions={Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CROMWELL(cls) -> "Weapon":
        """*Cromwell*"""
        return cls(
            id="Cromwell",
            name="Roadkill",
            vehicle_id="Cromwell",
            factions={Faction.CW},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CRUSADER_MK_III(cls) -> "Weapon":
        """*Crusader Mk.III*"""
        return cls(
            id="Crusader Mk.III",
            name="Roadkill",
            vehicle_id="Crusader Mk.III",
            factions={Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__FIREFLY(cls) -> "Weapon":
        """*Firefly*"""
        return cls(
            id="Firefly",
            name="Roadkill",
            vehicle_id="Firefly",
            factions={Faction.CW},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MK_III(cls) -> "Weapon":
        """*Churchill Mk.III*"""
        return cls(
            id="Churchill Mk.III",
            name="Roadkill",
            vehicle_id="Churchill Mk.III",
            factions={Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MK_VII(cls) -> "Weapon":
        """*Churchill Mk.VII*"""
        return cls(
            id="Churchill Mk.VII",
            name="Roadkill",
            vehicle_id="Churchill Mk.VII",
            factions={Faction.CW},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BEDFORD_OYD_SUPPLY(cls) -> "Weapon":
        """*Bedford OYD (Supply)*"""
        return cls(
            id="Bedford OYD (Supply)",
            name="Roadkill",
            vehicle_id="Bedford OYD (Supply)",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BEDFORD_OYD_TRANSPORT(cls) -> "Weapon":
        """*Bedford OYD (Transport)*"""
        return cls(
            id="Bedford OYD (Transport)",
            name="Roadkill",
            vehicle_id="Bedford OYD (Transport)",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.ROADKILL,
        )

    # M3 Half-track,

    # Jeep Willys

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__DAIMLER(cls) -> "Weapon":
        """*QF 2-POUNDER [Daimler]*"""
        return cls(
            id="QF 2-POUNDER [Daimler]",
            name="QF 2-Pounder",
            vehicle_id="Daimler",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__DAIMLER(cls) -> "Weapon":
        """*COAXIAL BESA [Daimler]*"""
        return cls(
            id="COAXIAL BESA [Daimler]",
            name="BESA",
            vehicle_id="Daimler",
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__TETRARCH(cls) -> "Weapon":
        """*QF 2-POUNDER [Tetrarch]*"""
        return cls(
            id="QF 2-POUNDER [Tetrarch]",
            name="QF 2-Pounder",
            vehicle_id="Tetrarch",
            factions={Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__TETRARCH(cls) -> "Weapon":
        """*COAXIAL BESA [Tetrarch]*"""
        return cls(
            id="COAXIAL BESA [Tetrarch]",
            name="BESA",
            vehicle_id="Tetrarch",
            factions={Faction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__M3_STUART_HONEY(cls) -> "Weapon":
        """*37MM CANNON [M3 Stuart Honey]*"""
        return cls(
            id="37MM CANNON [M3 Stuart Honey]",
            name="37mm Cannon",
            vehicle_id="M3 Stuart Honey",
            factions={Faction.B8A},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M3_STUART_HONEY(cls) -> "Weapon":
        """*COAXIAL M1919 [M3 Stuart Honey]*"""
        return cls(
            id="COAXIAL M1919 [M3 Stuart Honey]",
            name="M1919 Browning",
            vehicle_id="M3 Stuart Honey",
            factions={Faction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__M3_STUART_HONEY(cls) -> "Weapon":
        """*HULL M1919 [M3 Stuart Honey]*"""
        return cls(
            id="HULL M1919 [M3 Stuart Honey]",
            name="M1919 Browning",
            vehicle_id="M3 Stuart Honey",
            factions={Faction.B8A},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__CROMWELL(cls) -> "Weapon":
        """*OQF 75MM [Cromwell]*"""
        return cls(
            id="OQF 75MM [Cromwell]",
            name="QF 75mm",
            vehicle_id="Cromwell",
            factions={Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__CROMWELL(cls) -> "Weapon":
        """*COAXIAL BESA [Cromwell]*"""
        return cls(
            id="COAXIAL BESA [Cromwell]",
            name="BESA",
            vehicle_id="Cromwell",
            factions={Faction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA__CROMWELL(cls) -> "Weapon":
        """*HULL BESA [Cromwell]*"""
        return cls(
            id="HULL BESA [Cromwell]",
            name="BESA",
            vehicle_id="Cromwell",
            factions={Faction.CW},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__CRUSADER_MK_III(cls) -> "Weapon":
        """*OQF 57MM [Crusader Mk.III]*"""
        return cls(
            id="OQF 57MM [Crusader Mk.III]",
            name="QF 57mm",
            vehicle_id="Crusader Mk.III",
            factions={Faction.B8A},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__CRUSADER_MK_III(cls) -> "Weapon":
        """*COAXIAL BESA [Crusader Mk.III]*"""
        return cls(
            id="COAXIAL BESA [Crusader Mk.III]",
            name="BESA",
            vehicle_id="Crusader Mk.III",
            factions={Faction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_QF_17_POUNDER__FIREFLY(cls) -> "Weapon":
        """*QF 17-POUNDER [Firefly]*"""
        return cls(
            id="QF 17-POUNDER [Firefly]",
            name="QF 17-Pounder",
            vehicle_id="Firefly",
            factions={Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__FIREFLY(cls) -> "Weapon":
        """*COAXIAL M1919 [Firefly]*"""
        return cls(
            id="COAXIAL M1919 [Firefly]",
            name="M1919 Browning",
            vehicle_id="Firefly",
            factions={Faction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__CHURCHILL_MK_III(cls) -> "Weapon":
        """*OQF 57MM [Churchill Mk.III]*"""
        return cls(
            id="OQF 57MM [Churchill Mk.III]",
            name="QF 57mm",
            vehicle_id="Churchill Mk.III",
            factions={Faction.B8A},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_III(cls) -> "Weapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk.III]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk.III]",
            name="BESA",
            vehicle_id="Churchill Mk.III",
            factions={Faction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__CHURCHILL_MK_III(cls) -> "Weapon":
        """*HULL BESA 7.92mm [Churchill Mk.III]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk.III]",
            name="BESA",
            vehicle_id="Churchill Mk.III",
            factions={Faction.B8A},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__CHURCHILL_MK_VII(cls) -> "Weapon":
        """*OQF 75MM [Churchill Mk.VII]*"""
        return cls(
            id="OQF 75MM [Churchill Mk.VII]",
            name="QF 75mm",
            vehicle_id="Churchill Mk.VII",
            factions={Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_VII(cls) -> "Weapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk.VII]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk.VII]",
            name="BESA",
            vehicle_id="Churchill Mk.VII",
            factions={Faction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__CHURCHILL_MK_VII(cls) -> "Weapon":
        """*HULL BESA 7.92mm [Churchill Mk.VII]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk.VII]",
            name="BESA",
            vehicle_id="Churchill Mk.VII",
            factions={Faction.CW},
            type=WeaponType.TANK_HULL_MG,
        )

    # M2 Browning [M3 Half-track]

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__UNKNOWN(cls) -> "Weapon":
        """*QF 2-POUNDER*"""
        return cls(
            id="QF 2-POUNDER",
            name="QF 2-Pounder",
            vehicle_id=None,
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__UNKNOWN(cls) -> "Weapon":
        """*OQF 75MM*"""
        return cls(
            id="OQF 75MM",
            name="QF 75mm",
            vehicle_id=None,
            factions={Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__UNKNOWN(cls) -> "Weapon":
        """*OQF 57MM*"""
        return cls(
            id="OQF 57MM",
            name="QF 57mm",
            vehicle_id=None,
            factions={Faction.B8A},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_17_POUNDER__UNKNOWN(cls) -> "Weapon":
        """*QF 17-POUNDER*"""
        return cls(
            id="QF 17-POUNDER",
            name="QF 17-Pounder",
            vehicle_id=None,
            factions={Faction.CW},
            type=WeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__UNKNOWN(cls) -> "Weapon":
        """*COAXIAL BESA*"""
        return cls(
            id="COAXIAL BESA",
            name="BESA",
            vehicle_id=None,
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__UNKNOWN(cls) -> "Weapon":
        """*COAXIAL BESA 7.92mm*"""
        return cls(
            id="COAXIAL BESA 7.92mm",
            name="BESA",
            vehicle_id=None,
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA__UNKNOWN(cls) -> "Weapon":
        """*HULL BESA*"""
        return cls(
            id="HULL BESA",
            name="BESA",
            vehicle_id=None,
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__UNKNOWN(cls) -> "Weapon":
        """*HULL BESA 7.92mm*"""
        return cls(
            id="HULL BESA 7.92mm",
            name="7.92mm",
            vehicle_id=None,
            factions={Faction.CW, Faction.B8A},
            type=WeaponType.TANK_HULL_MG,
        )

    # --- Miscellaneous weapons ---

    @class_cached_property
    @classmethod
    def UNKNOWN(cls) -> "Weapon":
        """*UNKNOWN*"""
        return cls(
            id="UNKNOWN",
            name="Unknown",
            factions=set(Faction.all()),
            type=WeaponType.UNKNOWN,
        )

    @class_cached_property
    @classmethod
    def BOMBING_RUN(cls) -> "Weapon":
        """*BOMBING RUN*"""
        return cls(
            id="BOMBING RUN",
            name="Bombing Run",
            factions=set(Faction.all()) - {Faction.SOV},
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def STRAFING_RUN(cls) -> "Weapon":
        """*STRAFING RUN*"""
        return cls(
            id="STRAFING RUN",
            name="Strafing Run",
            factions=set(Faction.all()),
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def PRECISION_STRIKE(cls) -> "Weapon":
        """*PRECISION STRIKE*"""
        return cls(
            id="PRECISION STRIKE",
            name="Precision Strike",
            factions=set(Faction.all()),
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def KATYUSHA_BARRAGE(cls) -> "Weapon":
        """*Unknown*"""
        return cls(
            id="Unknown",
            name="Katyusha Barrage",
            factions={Faction.SOV},
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def FIRE_SPOT(cls) -> "Weapon":
        """*FireSpot*"""
        return cls(
            id="FireSpot",
            name="Fire",
            factions=set(Faction.all()),
            type=WeaponType.UNKNOWN,
        )

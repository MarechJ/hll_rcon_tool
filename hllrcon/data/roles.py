# ruff: noqa: N802

from enum import StrEnum

from hllrcon.data._utils import IndexedBaseModel, class_cached_property


class RoleType(StrEnum):
    INFANTRY = "Infantry"
    ARMOR = "Armor"
    RECON = "Recon"
    COMMANDER = "Commander"


class Role(IndexedBaseModel[int]):
    id: int
    name: str
    pretty_name: str
    type: RoleType
    is_squad_leader: bool
    """Whether this role is exclusive to the squad leader.

    Roles included are:
    - Commander
    - Officer
    - Tank Commander
    - Spotter
    """
    kill_combat_score: int
    """The Combat Effectiveness score gained when killing a player with this role."""
    assist_combat_score: int
    """The Combat Effectiveness score gained when assisting in the kill of a player with
    this role. Assists are gained when a player you downed gets killed by another."""

    @property
    def is_infantry(self) -> bool:
        """Whether the role is associated with infantry units.

        Roles included are:
        - Officer
        - Rifleman
        - Assault
        - Automatic Rifleman
        - Medic
        - Support
        - Machine Gunner
        - Anti-Tank
        - Engineer
        """
        return self.type == RoleType.INFANTRY

    @property
    def is_tanker(self) -> bool:
        """Whether the role is associated with armor units.

        Roles included are:
        - Tank Commander
        - Crewman
        """
        return self.type == RoleType.ARMOR

    @property
    def is_recon(self) -> bool:
        """Whether the role is associated with recon units.

        Roles included are:
        - Spotter
        - Sniper
        """
        return self.type == RoleType.RECON

    @class_cached_property
    @classmethod
    def RIFLEMAN(cls) -> "Role":
        return cls(
            id=0,
            name="Rifleman",
            pretty_name="Rifleman",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=3,
            assist_combat_score=2,
        )

    @class_cached_property
    @classmethod
    def ASSAULT(cls) -> "Role":
        return cls(
            id=1,
            name="Assault",
            pretty_name="Assault",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def AUTOMATIC_RIFLEMAN(cls) -> "Role":
        return cls(
            id=2,
            name="AutomaticRifleman",
            pretty_name="Automatic Rifleman",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def MEDIC(cls) -> "Role":
        return cls(
            id=3,
            name="Medic",
            pretty_name="Medic",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def SPOTTER(cls) -> "Role":
        return cls(
            id=4,
            name="Spotter",
            pretty_name="Spotter",
            type=RoleType.RECON,
            is_squad_leader=True,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def SUPPORT(cls) -> "Role":
        return cls(
            id=5,
            name="Support",
            pretty_name="Support",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def MACHINE_GUNNER(cls) -> "Role":
        return cls(
            id=6,
            name="HeavyMachineGunner",
            pretty_name="Machine Gunner",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def ANTI_TANK(cls) -> "Role":
        return cls(
            id=7,
            name="AntiTank",
            pretty_name="Anti-Tank",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def ENGINEER(cls) -> "Role":
        return cls(
            id=8,
            name="Engineer",
            pretty_name="Engineer",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def OFFICER(cls) -> "Role":
        return cls(
            id=9,
            name="Officer",
            pretty_name="Officer",
            type=RoleType.INFANTRY,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def SNIPER(cls) -> "Role":
        return cls(
            id=10,
            name="Sniper",
            pretty_name="Sniper",
            type=RoleType.RECON,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def CREWMAN(cls) -> "Role":
        return cls(
            id=11,
            name="Crewman",
            pretty_name="Crewman",
            type=RoleType.ARMOR,
            is_squad_leader=False,
            kill_combat_score=3,
            assist_combat_score=2,
        )

    @class_cached_property
    @classmethod
    def TANK_COMMANDER(cls) -> "Role":
        return cls(
            id=12,
            name="TankCommander",
            pretty_name="Tank Commander",
            type=RoleType.ARMOR,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def COMMANDER(cls) -> "Role":
        return cls(
            id=13,
            name="ArmyCommander",
            pretty_name="Army Commander",
            type=RoleType.COMMANDER,
            is_squad_leader=True,
            kill_combat_score=12,
            assist_combat_score=8,
        )

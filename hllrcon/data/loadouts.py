# mypy: disable-error-code="prop-decorator"
# ruff: noqa: N802, RUF001

from functools import cached_property
from typing import NamedTuple, Self

from pydantic import BaseModel, Field

from hllrcon.data._utils import IndexedBaseModel, class_cached_property
from hllrcon.data.factions import Faction
from hllrcon.data.roles import Role
from hllrcon.data.weapons import Weapon


class LoadoutId(NamedTuple):
    faction_id: int
    role_id: int
    name: str


class LoadoutItem(BaseModel, frozen=True):
    name: str
    """The name of this item."""
    amount: int = 1
    """The amount of this item. For small arms, refers to the number of magazines."""

    @cached_property
    def weapon(self) -> Weapon | None:
        """The weapon corresponding to this item, if any."""
        try:
            return Weapon.by_id(self.name)
        except ValueError:
            return None


class Loadout(IndexedBaseModel[LoadoutId]):
    name: str
    faction: Faction
    role: Role
    requires_level: int = Field(ge=1, le=10)
    items: list[LoadoutItem]

    # @computed_field
    @cached_property  # type: ignore[misc]
    def id(self) -> LoadoutId:  # type: ignore[override]
        return LoadoutId(
            faction_id=self.faction.id,
            role_id=self.role.id,
            name=self.name,
        )

    @classmethod
    def _lookup_register(cls, id_: LoadoutId, instance: Self) -> None:
        new_id = LoadoutId(*id_[:2], name=id_[2].lower())
        return super()._lookup_register(new_id, instance)

    @classmethod
    def by_id(cls, id_: LoadoutId | tuple[int, int, str]) -> "Loadout":
        """Look up a loadout by its identifier.

        An identifier consists of a faction ID, role ID, and name.

        For convenience, it is suggested that you use `Loadout.by_name()` instead.

        Parameters
        ----------
        id_ : LoadoutId
            The identifier of the loadout to look up.

        Returns
        -------
        Loadout
            The loadout with the given identifier.

        Raises
        ------
        KeyError
            If no loadout with the given identifier exists.

        """
        new_id = LoadoutId(*id_[:2], name=id_[2].lower())
        return super().by_id(new_id)

    @classmethod
    def by_name(cls, faction: Faction, role: Role, name: str) -> "Loadout":
        """Look up a loadout by its faction, role, and name.

        Parameters
        ----------
        faction : Faction
            The faction of the loadout.
        role : Role
            The role of the loadout.
        name : str
            The name of the loadout.

        Returns
        -------
        Loadout
            The loadout with the given faction, role, and name.

        Raises
        ------
        ValueError
            If no loadout with the given faction, role, and name exists.

        """
        return cls.by_id(
            LoadoutId(
                faction_id=faction.id,
                role_id=role.id,
                name=name,
            ),
        )

    @class_cached_property
    @classmethod
    def US_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="COLT M1911", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_COMMANDER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.US,
            role=Role.COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="M1 GARAND", amount=12),
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OFFICER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.OFFICER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OFFICER_POINT_MAN(cls) -> "Loadout":
        return cls(
            name="Point Man",
            faction=Faction.US,
            role=Role.OFFICER,
            requires_level=3,
            items=[
                LoadoutItem(name="M1 CARBINE", amount=12),
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OFFICER_NCO(cls) -> "Loadout":
        return cls(
            name="NCO",
            faction=Faction.US,
            role=Role.OFFICER,
            requires_level=6,
            items=[
                LoadoutItem(name="M1 GARAND", amount=19),
                LoadoutItem(name="MK2 GRENADE", amount=3),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=3),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="M1 GARAND", amount=19),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_RIFLEMAN_POINT_MAN(cls) -> "Loadout":
        return cls(
            name="Point Man",
            faction=Faction.US,
            role=Role.RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="M1 CARBINE", amount=12),
                LoadoutItem(name="MK2 GRENADE", amount=3),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.ASSAULT,
            requires_level=1,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.US,
            role=Role.ASSAULT,
            requires_level=3,
            items=[
                LoadoutItem(name="M97 TRENCH GUN", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.US,
            role=Role.ASSAULT,
            requires_level=6,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=6),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=4),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_RAIDER(cls) -> "Loadout":
        return cls(
            name="Raider",
            faction=Faction.US,
            role=Role.ASSAULT,
            requires_level=9,
            items=[
                LoadoutItem(name="M3 GREASE GUN", amount=6),
                LoadoutItem(name="MK2 GRENADE"),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="M1918A2 BAR", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.US,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MEDIC_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.MEDIC,
            requires_level=1,
            items=[
                LoadoutItem(name="M1 CARBINE", amount=3),
                LoadoutItem(name="COLT M1911", amount=6),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=4),
                LoadoutItem(name="MORPHINE SYRETTE", amount=20),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MEDIC_CORPSMAN(cls) -> "Loadout":
        return cls(
            name="Corpsman",
            faction=Faction.US,
            role=Role.MEDIC,
            requires_level=3,
            items=[
                LoadoutItem(name="COLT M1911", amount=16),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=6),
                LoadoutItem(name="MORPHINE SYRETTE", amount=20),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="MEDICAL SUPPLIES"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SUPPORT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.SUPPORT,
            requires_level=1,
            items=[
                LoadoutItem(name="M1 GARAND", amount=12),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SUPPORT_AMMO_CARRIER(cls) -> "Loadout":
        return cls(
            name="Ammo Carrier",
            faction=Faction.US,
            role=Role.SUPPORT,
            requires_level=3,
            items=[
                LoadoutItem(name="M3 GREASE GUN", amount=12),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SUPPORT_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.US,
            role=Role.SUPPORT,
            requires_level=8,
            items=[
                LoadoutItem(name="M2 FLAMETHROWER"),
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.MACHINE_GUNNER,
            requires_level=1,
            items=[
                LoadoutItem(name="BROWNING M1919", amount=6),
                LoadoutItem(name="COLT M1911", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MACHINE_GUNNER_FIRE_SUPPORT(cls) -> "Loadout":
        return cls(
            name="Fire Support",
            faction=Faction.US,
            role=Role.MACHINE_GUNNER,
            requires_level=3,
            items=[
                LoadoutItem(name="M1918A2 BAR Bipod", amount=14),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ANTI_TANK_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.ANTI_TANK,
            requires_level=1,
            items=[
                LoadoutItem(name="M1 GARAND", amount=12),
                LoadoutItem(name="BAZOOKA", amount=2),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ANTI_TANK_GUN_CREW(cls) -> "Loadout":
        return cls(
            name="Gun Crew",
            faction=Faction.US,
            role=Role.ANTI_TANK,
            requires_level=3,
            items=[
                LoadoutItem(name="M1 GARAND", amount=12),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="57MM M1"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ANTI_TANK_AMBUSHER(cls) -> "Loadout":
        return cls(
            name="Ambusher",
            faction=Faction.US,
            role=Role.ANTI_TANK,
            requires_level=6,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="M1A1 AT MINE", amount=4),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ENGINEER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.ENGINEER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1 CARBINE", amount=12),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WRENCH"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="M2 AP MINE", amount=2),
                LoadoutItem(name="M1A1 AT MINE"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ENGINEER_SAPPER(cls) -> "Loadout":
        return cls(
            name="Sapper",
            faction=Faction.US,
            role=Role.ENGINEER,
            requires_level=3,
            items=[
                LoadoutItem(name="M97 TRENCH GUN", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M2 AP MINE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ENGINEER_FIELD_ENGINEER(cls) -> "Loadout":
        return cls(
            name="Field Engineer",
            faction=Faction.US,
            role=Role.ENGINEER,
            requires_level=6,
            items=[
                LoadoutItem(name="M3 GREASE GUN", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WRENCH"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.TANK_COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=4),
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_TANK_COMMANDER_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.US,
            role=Role.TANK_COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="COLT M1911", amount=6),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_CREWMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.CREWMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_CREWMAN_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.US,
            role=Role.CREWMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="COLT M1911", amount=4),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SPOTTER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.SPOTTER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1A1 THOMPSON", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M2 AP MINE"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SPOTTER_SCOUT(cls) -> "Loadout":
        return cls(
            name="Scout",
            faction=Faction.US,
            role=Role.SPOTTER,
            requires_level=3,
            items=[
                LoadoutItem(name="M1 CARBINE", amount=12),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="WESTINGHOUSE M3 6×30"),
                LoadoutItem(name="FLARE GUN"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SNIPER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.US,
            role=Role.SNIPER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1903 SPRINGFIELD", amount=17),
                LoadoutItem(name="COLT M1911", amount=6),
                LoadoutItem(name="MK2 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SNIPER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.US,
            role=Role.SNIPER,
            requires_level=3,
            items=[
                LoadoutItem(name="M1903 SPRINGFIELD", amount=17),
                LoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                LoadoutItem(name="M2 AP MINE"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="M3 KNIFE"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="LUGER P08", amount=4),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_COMMANDER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.GER,
            role=Role.COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="GEWEHR 43", amount=12),
                LoadoutItem(name="WALTHER P38", amount=4),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OFFICER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.OFFICER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="LUGER P08", amount=4),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OFFICER_POINT_MAN(cls) -> "Loadout":
        return cls(
            name="Point Man",
            faction=Faction.GER,
            role=Role.OFFICER,
            requires_level=3,
            items=[
                LoadoutItem(name="GEWEHR 43", amount=10),
                LoadoutItem(name="WALTHER P38", amount=4),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OFFICER_NCO(cls) -> "Loadout":
        return cls(
            name="NCO",
            faction=Faction.GER,
            role=Role.OFFICER,
            requires_level=6,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=13),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=3),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=13),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=3),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_RIFLEMAN_STURMTRUPPEN(cls) -> "Loadout":
        return cls(
            name="Sturmtruppen",
            faction=Faction.GER,
            role=Role.RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="WALTHER P38", amount=12),
                LoadoutItem(name="M24 STIELHANDGRANATE", amount=4),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_RIFLEMAN_PANZERGRENADIER(cls) -> "Loadout":
        return cls(
            name="Panzergrenadier",
            faction=Faction.GER,
            role=Role.RIFLEMAN,
            requires_level=6,
            items=[
                LoadoutItem(name="GEWEHR 43", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.ASSAULT,
            requires_level=1,
            items=[
                LoadoutItem(name="GEWEHR 43", amount=10),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.GER,
            role=Role.ASSAULT,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.GER,
            role=Role.ASSAULT,
            requires_level=6,
            items=[
                LoadoutItem(name="GEWEHR 43", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=6),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_RAIDER(cls) -> "Loadout":
        return cls(
            name="Raider",
            faction=Faction.GER,
            role=Role.ASSAULT,
            requires_level=9,
            items=[
                LoadoutItem(name="STG44", amount=6),
                LoadoutItem(name="M43 STIELHANDGRANATE"),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="STG44", amount=6),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.GER,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=10),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_AUTOMATIC_RIFLEMAN_PARATROOPER(cls) -> "Loadout":
        return cls(
            name="Paratrooper",
            faction=Faction.GER,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=6,
            items=[
                LoadoutItem(name="FG42", amount=5),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MEDIC_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.MEDIC,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=8),
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=4),
                LoadoutItem(name="MORPHINE AMPOULE", amount=20),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MEDIC_SANITATER(cls) -> "Loadout":
        return cls(
            name="Sanitater",
            faction=Faction.GER,
            role=Role.MEDIC,
            requires_level=3,
            items=[
                LoadoutItem(name="LUGER P08", amount=16),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=6),
                LoadoutItem(name="MORPHINE AMPOULE", amount=20),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="MEDICAL SUPPLIES"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SUPPORT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.SUPPORT,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SUPPORT_AMMO_CARRIER(cls) -> "Loadout":
        return cls(
            name="Ammo Carrier",
            faction=Faction.GER,
            role=Role.SUPPORT,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SUPPORT_FLAMMENWERFER(cls) -> "Loadout":
        return cls(
            name="Flammenwerfer",
            faction=Faction.GER,
            role=Role.SUPPORT,
            requires_level=8,
            items=[
                LoadoutItem(name="FLAMMENWERFER 41"),
                LoadoutItem(name="WALTHER P38", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.MACHINE_GUNNER,
            requires_level=1,
            items=[
                LoadoutItem(name="MG34", amount=10),
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MACHINE_GUNNER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.GER,
            role=Role.MACHINE_GUNNER,
            requires_level=3,
            items=[
                LoadoutItem(name="MG42", amount=6),
                LoadoutItem(name="LUGER P08", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ANTI_TANK_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.ANTI_TANK,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="PANZERSCHRECK", amount=2),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ANTI_TANK_GUN_CREW(cls) -> "Loadout":
        return cls(
            name="Gun Crew",
            faction=Faction.GER,
            role=Role.ANTI_TANK,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="PAK 40"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ANTI_TANK_AMBUSHER(cls) -> "Loadout":
        return cls(
            name="Ambusher",
            faction=Faction.GER,
            role=Role.ANTI_TANK,
            requires_level=6,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="TELLERMINE 43", amount=4),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ENGINEER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.ENGINEER,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WRENCH"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="S-MINE", amount=2),
                LoadoutItem(name="TELLERMINE 43"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ENGINEER_PIONIER(cls) -> "Loadout":
        return cls(
            name="Pionier",
            faction=Faction.GER,
            role=Role.ENGINEER,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="S-MINE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.TANK_COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=4),
                LoadoutItem(name="LUGER P08", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_TANK_COMMANDER_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.GER,
            role=Role.TANK_COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="LUGER P08", amount=6),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_CREWMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.CREWMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_CREWMAN_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.GER,
            role=Role.CREWMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SPOTTER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.SPOTTER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="S-MINE"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SPOTTER_SCOUT(cls) -> "Loadout":
        return cls(
            name="Scout",
            faction=Faction.GER,
            role=Role.SPOTTER,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=10),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FLARE GUN"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SNIPER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.GER,
            role=Role.SNIPER,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K x8", amount=19),
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SNIPER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.GER,
            role=Role.SNIPER,
            requires_level=3,
            items=[
                LoadoutItem(name="FG42 x4", amount=12),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="S-MINE"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="PPSH 41", amount=10),
                LoadoutItem(name="NAGANT M1895", amount=4),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OFFICER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.OFFICER,
            requires_level=1,
            items=[
                LoadoutItem(name="PPSH 41", amount=8),
                LoadoutItem(name="TOKAREV TT33", amount=4),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OFFICER_JUNIOR_SERGEANT(cls) -> "Loadout":
        return cls(
            name="Junior Sergeant",
            faction=Faction.SOV,
            role=Role.OFFICER,
            requires_level=3,
            items=[
                LoadoutItem(name="SVT40", amount=12),
                LoadoutItem(name="TOKAREV TT33", amount=4),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OFFICER_STARSHINA(cls) -> "Loadout":
        return cls(
            name="Starshina",
            faction=Faction.SOV,
            role=Role.OFFICER,
            requires_level=6,
            items=[
                LoadoutItem(name="PPSH 41 W/DRUM", amount=19),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="MOSIN NAGANT 1891", amount=12),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_RIFLEMAN_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.SOV,
            role=Role.RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="MOSIN NAGANT M38", amount=12),
                LoadoutItem(name="RG-42 GRENADE", amount=4),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_RIFLEMAN_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.SOV,
            role=Role.RIFLEMAN,
            requires_level=6,
            items=[
                LoadoutItem(name="MOSIN NAGANT M38", amount=12),
                LoadoutItem(name="MOLOTOV", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.ASSAULT,
            requires_level=1,
            items=[
                LoadoutItem(name="PPSH 41", amount=14),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.SOV,
            role=Role.ASSAULT,
            requires_level=3,
            items=[
                LoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                LoadoutItem(name="RG-42 GRENADE", amount=1),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.SOV,
            role=Role.ASSAULT,
            requires_level=6,
            items=[
                LoadoutItem(name="SVT40", amount=6),
                LoadoutItem(name="RG-42 GRENADE", amount=6),
                LoadoutItem(name="RDG-2 SMOKE", amount=3),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.SOV,
            role=Role.ASSAULT,
            requires_level=9,
            items=[
                LoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                LoadoutItem(name="MOLOTOV", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_AUTOMATIC_RIFLEMAN_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.SOV,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                LoadoutItem(name="MOLOTOV", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_MEDIC_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.MEDIC,
            requires_level=1,
            items=[
                LoadoutItem(name="MOSIN NAGANT 91/30", amount=8),
                LoadoutItem(name="NAGANT M1895", amount=7),
                LoadoutItem(name="RDG-2 SMOKE", amount=4),
                LoadoutItem(name="REVIVE", amount=999),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_MEDIC_SANITATI(cls) -> "Loadout":
        return cls(
            name="Sanitati",
            faction=Faction.SOV,
            role=Role.MEDIC,
            requires_level=3,
            items=[
                LoadoutItem(name="NAGANT M1895", amount=18),
                LoadoutItem(name="RDG-2 SMOKE", amount=6),
                LoadoutItem(name="REVIVE"),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="MEDICAL SUPPLIES"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SUPPORT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.SUPPORT,
            requires_level=1,
            items=[
                LoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SUPPORT_AMMO_CARRIER(cls) -> "Loadout":
        return cls(
            name="Ammo Carrier",
            faction=Faction.SOV,
            role=Role.SUPPORT,
            requires_level=3,
            items=[
                LoadoutItem(name="SVT40", amount=12),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SUPPORT_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.SOV,
            role=Role.SUPPORT,
            requires_level=8,
            items=[
                LoadoutItem(name="MOSIN NAGANT M38", amount=12),
                LoadoutItem(name="NAGANT M1895", amount=4),
                LoadoutItem(name="MOLOTOV", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.MACHINE_GUNNER,
            requires_level=1,
            items=[
                LoadoutItem(name="DP-27", amount=12),
                LoadoutItem(name="NAGANT M1895", amount=6),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.ANTI_TANK,
            requires_level=1,
            items=[
                LoadoutItem(name="MOSIN NAGANT 91/30", amount=16),
                LoadoutItem(name="PTRS-41", amount=8),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_GUN_CREW(cls) -> "Loadout":
        return cls(
            name="Gun Crew",
            faction=Faction.SOV,
            role=Role.ANTI_TANK,
            requires_level=3,
            items=[
                LoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="ZiS 3"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_AMBUSHER(cls) -> "Loadout":
        return cls(
            name="Ambusher",
            faction=Faction.SOV,
            role=Role.ANTI_TANK,
            requires_level=6,
            items=[
                LoadoutItem(name="PPSH 41", amount=8),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="TM-35 AT MINE", amount=4),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_LEND_LEASE(cls) -> "Loadout":
        return cls(
            name="Lend Lease",
            faction=Faction.SOV,
            role=Role.ANTI_TANK,
            requires_level=8,
            items=[
                LoadoutItem(name="PPSH 41", amount=8),
                LoadoutItem(name="BAZOOKA", amount=2),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ENGINEER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.ENGINEER,
            requires_level=1,
            items=[
                LoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WRENCH"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="POMZ AP MINE", amount=2),
                LoadoutItem(name="TM-35 AT MINE"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ENGINEER_SAPPER(cls) -> "Loadout":
        return cls(
            name="Sapper",
            faction=Faction.SOV,
            role=Role.ENGINEER,
            requires_level=3,
            items=[
                LoadoutItem(name="MOSIN NAGANT 91/30", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="POMZ AP MINE", amount=2),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.TANK_COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="PPSH 41", amount=4),
                LoadoutItem(name="NAGANT M1895", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_TANK_COMMANDER_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.SOV,
            role=Role.TANK_COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="TOKAREV TT33", amount=6),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_CREWMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.CREWMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="NAGANT M1895", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_CREWMAN_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.SOV,
            role=Role.CREWMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="NAGANT M1895", amount=6),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SPOTTER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.SPOTTER,
            requires_level=1,
            items=[
                LoadoutItem(name="PPSH 41", amount=8),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="POMZ AP MINE"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SPOTTER_SCOUT(cls) -> "Loadout":
        return cls(
            name="Scout",
            faction=Faction.SOV,
            role=Role.SPOTTER,
            requires_level=3,
            items=[
                LoadoutItem(name="SVT40", amount=12),
                LoadoutItem(name="RDG-2 SMOKE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="RKKA 8×40"),
                LoadoutItem(name="FLARE GUN"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SNIPER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.SOV,
            role=Role.SNIPER,
            requires_level=1,
            items=[
                LoadoutItem(name="SCOPED MOSIN NAGANT 91/30", amount=17),
                LoadoutItem(name="NAGANT M1895", amount=6),
                LoadoutItem(name="RG-42 GRENADE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SNIPER_AUTOMATIC_MARKSMAN(cls) -> "Loadout":
        return cls(
            name="Automatic Marksman",
            faction=Faction.SOV,
            role=Role.SNIPER,
            requires_level=6,
            items=[
                LoadoutItem(name="SCOPED SVT40", amount=12),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="MPL-50 SPADE"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=8),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_COMMANDER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.CW,
            role=Role.COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OFFICER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.OFFICER,
            requires_level=1,
            items=[
                LoadoutItem(name="Sten Gun Mk.V", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OFFICER_POINT_MAN(cls) -> "Loadout":
        return cls(
            name="Point Man",
            faction=Faction.CW,
            role=Role.OFFICER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OFFICER_NCO(cls) -> "Loadout":
        return cls(
            name="NCO",
            faction=Faction.CW,
            role=Role.OFFICER,
            requires_level=6,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=3),
                LoadoutItem(name="No.77", amount=3),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Small Ammunition Box"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_RIFLEMAN_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.CW,
            role=Role.RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_RIFLEMAN_TROOPER(cls) -> "Loadout":
        return cls(
            name="Trooper",
            faction=Faction.CW,
            role=Role.RIFLEMAN,
            requires_level=6,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Explosive Ammo Box"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.ASSAULT,
            requires_level=1,
            items=[
                LoadoutItem(name="Sten Gun Mk.V", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.CW,
            role=Role.ASSAULT,
            requires_level=3,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.CW,
            role=Role.ASSAULT,
            requires_level=6,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=6),
                LoadoutItem(name="No.77", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_RAIDER(cls) -> "Loadout":
        return cls(
            name="Raider",
            faction=Faction.CW,
            role=Role.ASSAULT,
            requires_level=9,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=6),
                LoadoutItem(name="Mills Bomb", amount=1),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Satchel"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="Bren Gun", amount=10),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_AUTOMATIC_RIFLEMAN_DRUM_GUNNER(cls) -> "Loadout":
        return cls(
            name="Drum Gunner",
            faction=Faction.CW,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=5),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MEDIC_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.MEDIC,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=4),
                LoadoutItem(name="Webley MK VI", amount=8),
                LoadoutItem(name="No.77", amount=4),
                LoadoutItem(name="Morphine", amount=20),
                LoadoutItem(name="Bandage", amount=20),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MEDIC_CORPSMAN(cls) -> "Loadout":
        return cls(
            name="Corpsman",
            faction=Faction.CW,
            role=Role.MEDIC,
            requires_level=3,
            items=[
                LoadoutItem(name="Webley MK VI", amount=21),
                LoadoutItem(name="No.77", amount=6),
                LoadoutItem(name="Morphine", amount=20),
                LoadoutItem(name="Bandage", amount=20),
                LoadoutItem(name="Medical Supplies"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SUPPORT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.SUPPORT,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Supplies"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SUPPORT_AMMO_CARRIER(cls) -> "Loadout":
        return cls(
            name="Ammo Carrier",
            faction=Faction.CW,
            role=Role.SUPPORT,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Supplies"),
                LoadoutItem(name="Small Ammunition Box"),
                LoadoutItem(name="Explosive Ammo Box"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SUPPORT_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.CW,
            role=Role.SUPPORT,
            requires_level=8,
            items=[
                LoadoutItem(name="FLAMETHROWER"),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Supplies"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.MACHINE_GUNNER,
            requires_level=1,
            items=[
                LoadoutItem(name="Lewis Gun", amount=10),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MACHINE_GUNNER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.CW,
            role=Role.MACHINE_GUNNER,
            requires_level=3,
            items=[
                LoadoutItem(name="Bren Gun", amount=14),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.ANTI_TANK,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="PIAT", amount=2),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_GUN_CREW(cls) -> "Loadout":
        return cls(
            name="Gun Crew",
            faction=Faction.CW,
            role=Role.ANTI_TANK,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Ordnance QF 6-pounder"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_AMBUSHER(cls) -> "Loadout":
        return cls(
            name="Ambusher",
            faction=Faction.CW,
            role=Role.ANTI_TANK,
            requires_level=6,
            items=[
                LoadoutItem(name="Sten Gun Mk.V", amount=8),
                LoadoutItem(name="No.82 Grenade", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Satchel"),
                LoadoutItem(name="A.T. Mine G.S. Mk V", amount=4),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_ELEPHANT_GUNNER(cls) -> "Loadout":
        return cls(
            name="Elephant Gunner",
            faction=Faction.CW,
            role=Role.ANTI_TANK,
            requires_level=8,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Boys Anti-tank Rifle", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ENGINEER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.ENGINEER,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Wrench"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                LoadoutItem(name="A.T. Mine G.S. Mk V", amount=1),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ENGINEER_SAPPER(cls) -> "Loadout":
        return cls(
            name="Sapper",
            faction=Faction.CW,
            role=Role.ENGINEER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Satchel"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ENGINEER_FIELD_ENGINEER(cls) -> "Loadout":
        return cls(
            name="Field Engineer",
            faction=Faction.CW,
            role=Role.ENGINEER,
            requires_level=6,
            items=[
                LoadoutItem(name="Sten Gun Mk.V", amount=5),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Wrench"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="No.82 Grenade", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.TANK_COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="Sten Gun Mk.II", amount=4),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_TANK_COMMANDER_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.CW,
            role=Role.TANK_COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_CREWMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.CREWMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_CREWMAN_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.CW,
            role=Role.CREWMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SPOTTER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.SPOTTER,
            requires_level=1,
            items=[
                LoadoutItem(name="Sten Gun Mk.V", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                LoadoutItem(name="Small Ammunition Box"),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SPOTTER_SCOUT(cls) -> "Loadout":
        return cls(
            name="Scout",
            faction=Faction.CW,
            role=Role.SPOTTER,
            requires_level=3,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="No.2 Mk 5 Flare Pistol"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SNIPER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.CW,
            role=Role.SNIPER,
            requires_level=1,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SNIPER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.CW,
            role=Role.SNIPER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="LUGER P08", amount=4),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_COMMANDER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.DAK,
            role=Role.COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="WALTHER P38", amount=4),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OFFICER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.OFFICER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="LUGER P08", amount=4),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OFFICER_POINT_MAN(cls) -> "Loadout":
        return cls(
            name="Point Man",
            faction=Faction.DAK,
            role=Role.OFFICER,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=10),
                LoadoutItem(name="WALTHER P38", amount=4),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OFFICER_NCO(cls) -> "Loadout":
        return cls(
            name="NCO",
            faction=Faction.DAK,
            role=Role.OFFICER,
            requires_level=6,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=13),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=3),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=13),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=3),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_RIFLEMAN_STURMTRUPPEN(cls) -> "Loadout":
        return cls(
            name="Sturmtruppen",
            faction=Faction.DAK,
            role=Role.RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="WALTHER P38", amount=12),
                LoadoutItem(name="M24 STIELHANDGRANATE", amount=4),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_RIFLEMAN_PANZERGRENADIER(cls) -> "Loadout":
        return cls(
            name="Panzergrenadier",
            faction=Faction.DAK,
            role=Role.RIFLEMAN,
            requires_level=6,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.ASSAULT,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.DAK,
            role=Role.ASSAULT,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.DAK,
            role=Role.ASSAULT,
            requires_level=6,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=6),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_RAIDER(cls) -> "Loadout":
        return cls(
            name="Raider",
            faction=Faction.DAK,
            role=Role.ASSAULT,
            requires_level=9,
            items=[
                LoadoutItem(name="MP40", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE"),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=10),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.DAK,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=10),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MEDIC_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.MEDIC,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=8),
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=4),
                LoadoutItem(name="MORPHINE AMPOULE", amount=20),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MEDIC_SANITATER(cls) -> "Loadout":
        return cls(
            name="Sanitater",
            faction=Faction.DAK,
            role=Role.MEDIC,
            requires_level=3,
            items=[
                LoadoutItem(name="LUGER P08", amount=16),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=6),
                LoadoutItem(name="MORPHINE AMPOULE", amount=20),
                LoadoutItem(name="BANDAGE", amount=20),
                LoadoutItem(name="MEDICAL SUPPLIES"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SUPPORT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.SUPPORT,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SUPPORT_AMMO_CARRIER(cls) -> "Loadout":
        return cls(
            name="Ammo Carrier",
            faction=Faction.DAK,
            role=Role.SUPPORT,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="EXPLOSIVE AMMO BOX"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SUPPORT_FLAMMENWERFER(cls) -> "Loadout":
        return cls(
            name="Flammenwerfer",
            faction=Faction.DAK,
            role=Role.SUPPORT,
            requires_level=8,
            items=[
                LoadoutItem(name="FLAMMENWERFER 41"),
                LoadoutItem(name="WALTHER P38", amount=4),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="SUPPLIES"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.MACHINE_GUNNER,
            requires_level=1,
            items=[
                LoadoutItem(name="MG34", amount=10),
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MACHINE_GUNNER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.DAK,
            role=Role.MACHINE_GUNNER,
            requires_level=3,
            items=[
                LoadoutItem(name="MG42", amount=6),
                LoadoutItem(name="LUGER P08", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ANTI_TANK_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.ANTI_TANK,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="PANZERSCHRECK", amount=2),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ANTI_TANK_GUN_CREW(cls) -> "Loadout":
        return cls(
            name="Gun Crew",
            faction=Faction.DAK,
            role=Role.ANTI_TANK,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="PAK 40"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ANTI_TANK_AMBUSHER(cls) -> "Loadout":
        return cls(
            name="Ambusher",
            faction=Faction.DAK,
            role=Role.ANTI_TANK,
            requires_level=6,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="TELLERMINE 43", amount=4),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ENGINEER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.ENGINEER,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=12),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WRENCH"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="S-MINE", amount=2),
                LoadoutItem(name="TELLERMINE 43"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ENGINEER_PIONIER(cls) -> "Loadout":
        return cls(
            name="Pionier",
            faction=Faction.DAK,
            role=Role.ENGINEER,
            requires_level=3,
            items=[
                LoadoutItem(name="MP40", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="S-MINE", amount=2),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="SATCHEL"),
                LoadoutItem(name="HAMMER"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.TANK_COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=4),
                LoadoutItem(name="LUGER P08", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_TANK_COMMANDER_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.DAK,
            role=Role.TANK_COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="LUGER P08", amount=6),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_CREWMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.CREWMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_CREWMAN_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.DAK,
            role=Role.CREWMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="TORCH"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SPOTTER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.SPOTTER,
            requires_level=1,
            items=[
                LoadoutItem(name="MP40", amount=8),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="S-MINE"),
                LoadoutItem(name="SMALL AMMUNITION BOX"),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SPOTTER_SCOUT(cls) -> "Loadout":
        return cls(
            name="Scout",
            faction=Faction.DAK,
            role=Role.SPOTTER,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K", amount=10),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="WATCH"),
                LoadoutItem(name="DIENSTGLAS 6×30"),
                LoadoutItem(name="FLARE GUN"),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SNIPER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.DAK,
            role=Role.SNIPER,
            requires_level=1,
            items=[
                LoadoutItem(name="KARABINER 98K x8", amount=19),
                LoadoutItem(name="WALTHER P38", amount=6),
                LoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SNIPER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.DAK,
            role=Role.SNIPER,
            requires_level=3,
            items=[
                LoadoutItem(name="KARABINER 98K x*", amount=12),
                LoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                LoadoutItem(name="S-MINE"),
                LoadoutItem(name="BANDAGE", amount=2),
                LoadoutItem(name="FELDSPATEN"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=8),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_COMMANDER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.B8A,
            role=Role.COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OFFICER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.OFFICER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=5),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OFFICER_POINT_MAN(cls) -> "Loadout":
        return cls(
            name="Point Man",
            faction=Faction.B8A,
            role=Role.OFFICER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OFFICER_NCO(cls) -> "Loadout":
        return cls(
            name="NCO",
            faction=Faction.B8A,
            role=Role.OFFICER,
            requires_level=6,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=3),
                LoadoutItem(name="No.77", amount=3),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Small Ammunition Box"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_RIFLEMAN_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.B8A,
            role=Role.RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_RIFLEMAN_TROOPER(cls) -> "Loadout":
        return cls(
            name="Trooper",
            faction=Faction.B8A,
            role=Role.RIFLEMAN,
            requires_level=6,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Explosive Ammo Box"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.ASSAULT,
            requires_level=1,
            items=[
                LoadoutItem(name="Sten Gun", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.B8A,
            role=Role.ASSAULT,
            requires_level=3,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_GRENADIER(cls) -> "Loadout":
        return cls(
            name="Grenadier",
            faction=Faction.B8A,
            role=Role.ASSAULT,
            requires_level=6,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=6),
                LoadoutItem(name="No.77", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_RAIDER(cls) -> "Loadout":
        return cls(
            name="Raider",
            faction=Faction.B8A,
            role=Role.ASSAULT,
            requires_level=9,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=6),
                LoadoutItem(name="Mills Bomb", amount=1),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Satchel"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="Bren Gun", amount=10),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_AUTOMATIC_RIFLEMAN_DRUM_GUNNER(cls) -> "Loadout":
        return cls(
            name="Drum Gunner",
            faction=Faction.B8A,
            role=Role.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=5),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MEDIC_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.MEDIC,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=4),
                LoadoutItem(name="Webley MK VI", amount=8),
                LoadoutItem(name="No.77", amount=4),
                LoadoutItem(name="Morphine", amount=20),
                LoadoutItem(name="Bandage", amount=20),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MEDIC_CORPSMAN(cls) -> "Loadout":
        return cls(
            name="Corpsman",
            faction=Faction.B8A,
            role=Role.MEDIC,
            requires_level=3,
            items=[
                LoadoutItem(name="Webley MK VI", amount=21),
                LoadoutItem(name="No.77", amount=6),
                LoadoutItem(name="Morphine", amount=20),
                LoadoutItem(name="Bandage", amount=20),
                LoadoutItem(name="Medical Supplies"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SUPPORT_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.SUPPORT,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Supplies"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SUPPORT_AMMO_CARRIER(cls) -> "Loadout":
        return cls(
            name="Ammo Carrier",
            faction=Faction.B8A,
            role=Role.SUPPORT,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Supplies"),
                LoadoutItem(name="Small Ammunition Box"),
                LoadoutItem(name="Explosive Ammo Box"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SUPPORT_FLAMER(cls) -> "Loadout":
        return cls(
            name="Flamer",
            faction=Faction.B8A,
            role=Role.SUPPORT,
            requires_level=8,
            items=[
                LoadoutItem(name="FLAMETHROWER"),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Supplies"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.MACHINE_GUNNER,
            requires_level=1,
            items=[
                LoadoutItem(name="Lewis Gun", amount=10),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MACHINE_GUNNER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.B8A,
            role=Role.MACHINE_GUNNER,
            requires_level=3,
            items=[
                LoadoutItem(name="Bren Gun", amount=14),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.ANTI_TANK,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="PIAT", amount=2),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_GUN_CREW(cls) -> "Loadout":
        return cls(
            name="Gun Crew",
            faction=Faction.B8A,
            role=Role.ANTI_TANK,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Ordnance QF 6-pounder"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_AMBUSHER(cls) -> "Loadout":
        return cls(
            name="Ambusher",
            faction=Faction.B8A,
            role=Role.ANTI_TANK,
            requires_level=6,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                LoadoutItem(name="A.T. Mine G.S. Mk V", amount=4),
                LoadoutItem(name="Satchel"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_ELEPHANT_GUNNER(cls) -> "Loadout":
        return cls(
            name="Elephant Gunner",
            faction=Faction.B8A,
            role=Role.ANTI_TANK,
            requires_level=8,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Boys Anti-tank Rifle", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ENGINEER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.ENGINEER,
            requires_level=1,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                LoadoutItem(name="A.T. Mine G.S. Mk V", amount=1),
                LoadoutItem(name="Wrench"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ENGINEER_SAPPER(cls) -> "Loadout":
        return cls(
            name="Sapper",
            faction=Faction.B8A,
            role=Role.ENGINEER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I", amount=6),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                LoadoutItem(name="Satchel"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ENGINEER_FIELD_ENGINEER(cls) -> "Loadout":
        return cls(
            name="Field Engineer",
            faction=Faction.B8A,
            role=Role.ENGINEER,
            requires_level=6,
            items=[
                LoadoutItem(name="Sten Gun", amount=5),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Wrench"),
                LoadoutItem(name="Hammer"),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.TANK_COMMANDER,
            requires_level=1,
            items=[
                LoadoutItem(name="Sten Gun", amount=4),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_TANK_COMMANDER_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.B8A,
            role=Role.TANK_COMMANDER,
            requires_level=3,
            items=[
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_CREWMAN_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.CREWMAN,
            requires_level=1,
            items=[
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_CREWMAN_MECHANIC(cls) -> "Loadout":
        return cls(
            name="Mechanic",
            faction=Faction.B8A,
            role=Role.CREWMAN,
            requires_level=3,
            items=[
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Torch"),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SPOTTER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.SPOTTER,
            requires_level=1,
            items=[
                LoadoutItem(name="M1928A1 THOMPSON", amount=8),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Small Ammunition Box"),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SPOTTER_SCOUT(cls) -> "Loadout":
        return cls(
            name="Scout",
            faction=Faction.B8A,
            role=Role.SPOTTER,
            requires_level=3,
            items=[
                LoadoutItem(name="SMLE No.1 Mk III", amount=6),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Watch"),
                LoadoutItem(name="Prism No.2 Mk II x6"),
                LoadoutItem(name="No.2 Mk 5 Flare Pistol"),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SNIPER_STANDARD_ISSUE(cls) -> "Loadout":
        return cls(
            name="Standard Issue",
            faction=Faction.B8A,
            role=Role.SNIPER,
            requires_level=1,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                LoadoutItem(name="Webley MK VI", amount=4),
                LoadoutItem(name="Mills Bomb", amount=2),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SNIPER_VETERAN(cls) -> "Loadout":
        return cls(
            name="Veteran",
            faction=Faction.B8A,
            role=Role.SNIPER,
            requires_level=3,
            items=[
                LoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                LoadoutItem(name="No.77", amount=2),
                LoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                LoadoutItem(name="Bandage", amount=2),
                LoadoutItem(name="Fairbairn–Sykes"),
            ],
        )

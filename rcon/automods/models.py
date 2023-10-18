import logging
from dataclasses import field
from datetime import datetime
from enum import Enum, auto
from typing import List, Mapping, Optional, TypedDict

from pydantic import HttpUrl
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


class SquadHasLeader(Exception):
    pass


class NoSoloTanker(Exception):
    pass


class SquadCycleOver(Exception):
    pass


class NoSeedingViolation(Exception):
    pass


class NoLevelViolation(Exception):
    pass


class OffensiveDefensiveState(TypedDict):
    offensive_points: int
    defensive_points: int


@dataclass
class WatchStatus:
    offensive_points: Mapping[str, int] = field(default_factory=dict)

    noted: Mapping[str, List[datetime]] = field(default_factory=dict)
    warned: Mapping[str, List[datetime]] = field(default_factory=dict)
    punished: Mapping[str, List[datetime]] = field(default_factory=dict)


class PunishStepState(Enum):
    WAIT = auto()
    IMMUNED = auto()
    DISABLED = auto()
    APPLY = auto()
    GO_TO_NEXT_STEP = auto()


class ActionMethod(Enum):
    MESSAGE = auto()
    PUNISH = auto()
    KICK = auto()
    FORCE_KICK = auto()


@dataclass
class PunishDetails:
    author: str
    message: str = ""
    discord_audit_url: Optional[HttpUrl] = field(repr=False, default=None)
    dry_run: bool = False


@dataclass
class PunishPlayer:
    steam_id_64: str
    name: str
    squad: str
    team: str
    role: str = None
    lvl: int = None
    details: PunishDetails = None

    def short_repr(self):
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name}, lvl={self.lvl}, role={self.role})"
        )


@dataclass
class ASquad:
    team: str
    name: str
    players: List[PunishPlayer] = field(default_factory=list)


@dataclass
class PunitionsToApply:
    warning: List[PunishPlayer] = field(default_factory=list)
    punish: List[PunishPlayer] = field(default_factory=list)
    kick: List[PunishPlayer] = field(default_factory=list)
    squads_state: List[ASquad] = field(default_factory=list)

    def add_squad_state(self, team: str, squad_name: str, squad: dict):
        try:
            if any(s.team == team and s.name == squad_name for s in self.squads_state):
                return
            self.squads_state.append(
                ASquad(
                    team=team,
                    name=squad_name,
                    players=[
                        PunishPlayer(
                            steam_id_64=p.get("steam_id_64"),
                            name=p.get("name"),
                            squad=p.get("unit_name"),
                            team=p.get("team"),
                            role=p.get("role"),
                            lvl=p.get("level"),
                        )
                        for p in squad.get("players", [])
                    ],
                )
            )
        except:
            logger.exception("Unable to add squad info")

    def merge(self, o: "PunitionsToApply"):
        if len(o.warning) != 0:
            self.warning.extend(o.warning)
        for p in o.punish:
            if not any(sp.steam_id_64 == p.steam_id_64 for sp in self.punish):
                self.punish.append(p)
        for k in o.kick:
            if not any(sk.steam_id_64 == k.steam_id_64 for sk in self.kick):
                self.kick.append(k)
        for s in o.squads_state:
            if any(s.team == ss.team and s.name == ss.name for ss in self.squads_state):
                continue
            self.squads_state.append(
                ASquad(
                    team=s.team,
                    name=s.name,
                    players=s.players,
                )
            )

    def __bool__(self):
        return any(
            [
                self.warning,
                self.punish,
                self.kick,
            ]
        )


@dataclass
class NoSoloTankConfig:
    enabled: bool = False
    dry_run: bool = True
    whitelist_flags: List = field(default_factory=list)
    discord_webhook_url: str = ""

    number_of_notes: int = 2  # Let's give the mates some time to arrive
    notes_interval_seconds: int = 60

    number_of_warning: int = 2
    warning_interval_seconds: int = 60
    warning_message: str = (
        "Warning, {player_name} !\n\n"
        "You can't play solo tank on this server !\n\n"
        "You will be punished after {max_warnings} warnings\n"
        "(you already received {received_warnings})\n\n"
        "Next check will happen automatically in {next_check_seconds}s."
    )

    disable_punish_below_server_player_count: int = 40
    number_of_punish: int = 2
    punish_interval_seconds: int = 60
    punish_message: str = (
        "You violated solo tank rule on this server.\n"
        "You're being punished by a bot ({received_punishes}/{max_punishes}).\n"
        "Next check in {next_check_seconds}s."
    )

    disable_kick_below_server_player_count: int = 40
    kick_after_max_punish: bool = False
    kick_grace_period_seconds: int = 60
    kick_message: str = (
        "You violated solo tank rule on this server.\n"
        "Your grace period of {kick_grace_period}s has passed.\n"
        "You failed to comply with the previous warnings."
    )

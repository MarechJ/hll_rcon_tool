import logging
from dataclasses import field
from datetime import datetime
from enum import Enum, auto
from typing import List, Mapping

from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)


class SquadHasLeader(Exception):
    pass


class SquadCycleOver(Exception):
    pass


@dataclass
class WatchStatus:
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


@dataclass
class NoLeaderConfig:
    enabled: bool = False
    dry_run: bool = True
    discord_webhook_url: str = ""

    number_of_notes: int = 1
    notes_interval_seconds: int = 10

    warning_message: str = (
        "Warning, {player_name}! Your squad ({squad_name}) does not have an officer."
        "Players of squads without an officer will be punished after {max_warnings} warnings"
        "(you already received {received_warnings}), then kicked.\n"
        "Next check will happen automatically in {next_check_seconds}s."
    )
    # Set to 0 to disable, -1 for infinite warnings (will never go to punishes)
    number_of_warning: int = 2
    warning_interval_seconds: int = 60

    # Set to 0 to disable, -1 for infinite punish (will never go to kicks)
    number_of_punish: int = 0
    punish_interval_seconds: int = 60
    min_squad_players_for_punish: int = 3
    disable_punish_below_server_player_count: int = 60
    punish_message: str = (
        "Your squad ({squad_name}) must have an officer.\n"
        "You're being punished by a bot ({received_punishes}/{max_punishes}).\n"
        "Next check in {next_check_seconds} seconds"
    )

    kick_after_max_punish: bool = False
    disable_kick_below_server_player_count: int = 60
    min_squad_players_for_kick: int = 3
    kick_grace_period_seconds: int = 120
    kick_message: str = (
        "Your squad ({squad_name}) must have an officer.\n"
        "Your grace period of {kick_grace_period}s has passed.\n"
        "You failed to comply with the previous warnings."
    )
    # roles: 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner', 'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
    immuned_roles: List[str] = field(default_factory=lambda: ["support", "sniper"])
    immuned_level_up_to: int = 15

    # this value is not used in automod
    # but required to succesfully parse the yml data to a pydanctic.dataclass
    whitespace_names_message: str = ""


@dataclass
class APlayer:
    steam_id_64: str
    name: str
    squad: str
    team: str
    role: str = None
    lvl: int = None

    def short_repr(self):
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name}, lvl={self.lvl}, role={self.role})"
        )

@dataclass
class ASquad:
    team: str
    name: str
    players: List[APlayer] = field(default_factory=list)


@dataclass
class PunitionsToApply:
    warning: List[APlayer] = field(default_factory=list)
    punish: List[APlayer] = field(default_factory=list)
    kick: List[APlayer] = field(default_factory=list)
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
                        APlayer(
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

    def __bool__(self):
        return any(
            [
                self.warning,
                self.punish,
                self.kick,
            ]
        )


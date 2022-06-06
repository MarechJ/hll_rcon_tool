import logging
import pickle
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Callable, List, Mapping

import redis
from rcon.audit import ingame_mods, online_mods
from rcon.cache_utils import get_redis_client
from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.extended_commands import CommandFailedError
from rcon.map_recorder import MapsRecorder
from rcon.recorded_commands import RecordedRcon
from rcon.user_config import AutoVoteKickConfig


class SquadHasLeader(Exception):
    pass


class SquadCycleOver(Exception):
    pass


@dataclass
class WatchStatus:
    warned: List[datetime] = field(default_factory=list)
    punished: Mapping[str, List[datetime]] = field(default_factory=dict)


class PunishStepState(Enum):
    wait = auto()
    immuned = auto()
    disabled = auto()
    apply = auto()
    go_to_next_step = auto()


@dataclass
class NoLeaderConfig:
    enabled: bool = False
    dry_run: bool = True
    warn_message_header: str = "Warning squads must have an Officer.\nYou will be punished then kicked"
    warn_message_footer: str = "Next check will happen automatically in 60s"
    # Set to 0 to disable, -1 for infinite warnings (will never go to punishes)
    number_of_warning: int = 2
    warning_interval_seconds: int = 60

    # Set to 0 to disable, -1 for infinite punish (will never go to kicks)
    number_of_punish: int = 0
    punish_interval_seconds: int = 60
    min_squad_players_for_punish: int = 3
    disable_punish_below_server_player_count: int = 60
    punish_message: str = (
        "Squads must have an officer.\nYou're being punished by a bot.\nNext check in 60seconds"
    )

    kick_after_max_punish: bool = False
    disable_kick_below_server_player_count: int = 60
    min_squad_players_for_kick: int = 3
    kick_grace_period_seconds: int = 120
    kick_message: str = (
        "Squads must have an officer.\nYou failed to comply with the previous warnings."
    )
    # roles: 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner', 'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
    immuned_roles: List[str] = field(default_factory=lambda: ["support", "sniper"])
    immuned_level_up_to: int = 15


@dataclass
class APlayer:
    player: str
    squad: str
    team: str


@dataclass
class PunitionsToApply:
    warning: Mapping[str, List[str]] = field(default_factory=lambda: {"allies": [], "axis": []})
    punish: List[APlayer] = field(default_factory=list)
    kick: List[APlayer] = field(default_factory=list)

    def __bool__(self):
        return any([self.warning.get("allies"), self.warning.get("axis"), self.kick, self.punish])

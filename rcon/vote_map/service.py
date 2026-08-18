from dataclasses import dataclass
from enum import Enum, IntFlag
import functools
import logging
import random
import re
from datetime import UTC, datetime, timedelta
from functools import partial
from typing import Dict, List, Optional, Tuple
from collections.abc import Iterable, Callable
from collections import Counter

from sqlalchemy import and_
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from rcon import maps
from rcon.cache_utils import ttl_cache
from rcon.connection import HLLCommandError
from rcon.maps import (
    Environment,
    GameMode,
    Layer,
    categorize_maps,
    sort_maps_by_gamemode,
)
from rcon.models import PlayerID, PlayerOptins, enter_session
from rcon.player_history import get_player
from rcon.rcon import HLLCommandFailedError, Rcon, get_rcon
from rcon.types import (
    MapInfo,
    PlayerProfileType,
    StructuredLogLineWithMetaData,
    VoteMapStatus,
    VoteMapVote,
    VoteMapMapResult,
)
from rcon.user_config.vote_map import (
    HELP_TEXT,
    PLAYER_CHOICE_HELP_TEXT,
    DefaultMethods,
    VoteMapUserConfig,
)
from rcon.utils import MapsHistory

from .exceptions import (
    InvalidMapParam,
    InvalidVoteError,
    PlayerChoiceNotAllowed,
    PlayerNotFound,
    PlayerVoteNotAllowed,
    RestrictiveFilterError,
    SelectionLimitExceeded,
    VoteMapException,
    VoteMapNoInitialised,
)
from .selection import MapSelectionBuilder, MapSelectionCriteria
from .state import VotemapState

logger = logging.getLogger(__name__)


def validate_maps(func):
    @functools.wraps(func)
    def wrapper(self, map_arg, *args, **kwargs):
        all_maps = self._rcon.get_maps()
        # Check for Layer
        if isinstance(map_arg, Layer):
            if map_arg not in all_maps:
                raise Exception(
                    f"Map `{map_arg}` is not a valid map on the game server."
                )
        # Check for iterable of strings (but not a string itself)
        elif isinstance(map_arg, Iterable) and not isinstance(map_arg, Layer):
            invalid = [map for map in map_arg if map not in all_maps]
            if invalid:
                raise Exception(
                    f"Invalid maps: {', '.join(str(map) for map in invalid)}"
                )
        else:
            raise Exception("Invalid argument type for map(s)")
        return func(self, map_arg, *args, **kwargs)

    return wrapper


class ActionOutcome(Enum):
    SUCCESS = "success"
    DISABLED = "disabled"
    ON_COOLDOWN = "on_cooldown"
    PAUSED = "paused"
    INVALID_CONFIG = "invalid_config"


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    outcome: ActionOutcome
    message: Optional[str] = None

    def __bool__(self) -> bool:
        return self.ok


class VotemapPermissions(IntFlag):
    REGISTER_VOTE = 1
    REGISTER_CHOICE = 2


class VoteMap:
    next_map = None

    def __init__(
        self,
        rcon: Rcon | None = None,
        config_loader: Callable | None = None,
        maps_history: MapsHistory | None = None,
    ) -> None:
        self.OPTIN_NAME = "votemap_reminder"
        self.SELECTION_LIMIT = 20
        self._rcon = rcon or get_rcon()
        self.__config_loader = config_loader or VoteMapUserConfig.load_from_db
        self._maps_history = maps_history or MapsHistory()
        self._parse_layer = self._rcon.game_profile.parse_layer
        self._state = VotemapState(layer_parser=self._parse_layer)

        whitelist_not_initialized = len(self._state.get_whitelist()) == 0
        if whitelist_not_initialized:
            self.reset_map_whitelist()

    @staticmethod
    def require_enabled(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.enabled:
                logger.warning("Method %s skipped: Votemap is disabled", func.__name__)
                return ActionResult(
                    ok=False,
                    outcome=ActionOutcome.DISABLED,
                    message="Votemap is disabled.",
                )
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def join_vote_options(
        selection: list[maps.Layer],
        maps_to_numbers: dict[maps.Layer, str],
        ranked_votes: Counter[maps.Layer],
        total_votes: int,
        join_char: str = " ",
    ) -> str:
        return join_char.join(
            f"[{maps_to_numbers[m]}] {m.pretty_name} - {ranked_votes[m]}/{total_votes} votes"
            for m in selection
        )

    @staticmethod
    def format_map_vote(
        selection: list[Layer],
        votes: list[VoteMapVote],
        format_type="vertical",
        player_choice: Dict[str, str] | None = None,
    ) -> str:
        """
        Returns an enumarated list of votemap selection.\n
        The entry id starts from 1. Entry id 0 is reserved for player's chosen map.\n
        format_type=vertical is suitable for broadcast message\n
        format_type=by_mod* is suitable for in game message
        """
        if len(selection) == 0:
            logger.warning("No vote map selection")
            return ""

        text: list[str] = []
        total_vote_counts = 0

        ranked_votes = Counter()
        for vote in votes:
            ranked_votes[vote["map_id"]] += vote["vote_count"]
            total_vote_counts += vote["vote_count"]

        # 0: map 1, 1: map 2, etc.
        vote_dict = {}
        entry_id = 1 if not player_choice else 0
        for map in selection:
            vote_dict[entry_id] = map
            entry_id += 1

        if format_type == "vertical":
            items = [
                f"[{k}] {v} - {ranked_votes[v]}/{total_vote_counts} votes"
                for k, v in vote_dict.items()
            ]
            text.append("\n".join(items))
        elif format_type.startswith("by_mod"):
            # map 1: 0, map 2: 1, etc.
            maps_to_numbers = dict(zip(vote_dict.values(), vote_dict.keys()))

            if player_choice:
                map_choice = selection.pop(0)
                s = f"{player_choice["player_name"]}'s pick:\n"
                s += f"[{maps_to_numbers[map_choice]}] {map_choice.pretty_name} - {ranked_votes[map_choice]}/{total_vote_counts} votes"
                text.append(s)
            categorized = categorize_maps(selection)
            if len(categorized[maps.GameMode.WARFARE]):
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.GameMode.WARFARE],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=total_vote_counts,
                    join_char="\n",
                )
                text.append(f"WARFARES:\n{vote_options}")
            if len(categorized[maps.GameMode.OFFENSIVE]):
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.GameMode.OFFENSIVE],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=total_vote_counts,
                    join_char="\n",
                )
                text.append(f"OFFENSIVES:\n{vote_options}")
            if len(categorized[maps.GameMode.SKIRMISH]):
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.GameMode.SKIRMISH],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=total_vote_counts,
                    join_char="\n",
                )
                text.append(f"SKIRMISHES:\n{vote_options}")

        return "\n\n".join(text)

    #########################
    #                       #
    #  GETTERS AND SETTERS  #
    #                       #
    #########################
    @property
    def config(self):
        return self.__config_loader()

    @property
    def enabled(self):
        return self.config.enabled

    @property
    def paused(self):
        return self.get_admin_next_map() is not None

    @validate_maps
    def set_admin_next_map(self, map: Layer):
        self._state.set_admin_next_map(map)

    def reset_admin_next_map(self):
        self._state.delete_admin_next_map()

    def get_admin_next_map(self) -> Layer | None:
        return self._state.get_admin_next_map()

    def get_next_map(self) -> Layer | None:
        return self._state.get_next_map()

    @validate_maps
    def set_next_map(self, map: Layer):
        self._state.set_next_map(map)

    def reset_next_map(self):
        self._state.delete_next_map()

    def get_last_reminder_time(self) -> datetime | None:
        return self._state.get_last_reminder_time()

    def set_last_reminder_time(self) -> None:
        dt = datetime.now(tz=UTC)
        self._state.set_last_reminder_time(dt)

    def reset_last_reminder_time(self) -> None:
        self._state.delete_last_reminder_time()

    def get_votes(self):
        return self._state.get_votes()

    def parse_layer(self, layer_name: str | Layer) -> Layer:
        """Parse a layer using the game profile associated with this server."""
        return self._parse_layer(layer_name)

    def get_vote(self, player_id: str) -> VoteMapVote | None:
        return self._state.get_vote(player_id)

    def get_map_whitelist(self):
        return self._state.get_whitelist()

    @validate_maps
    def add_map_to_whitelist(self, map: Layer):
        self._state.add_map_to_whitelist(map)

    @validate_maps
    def add_maps_to_whitelist(self, maps: Iterable[Layer]):
        for map in maps:
            self._state.add_map_to_whitelist(map)

    def remove_map_from_whitelist(self, map: Layer):
        self._state.remove_map_from_whitelist(map)

    def remove_maps_from_whitelist(self, maps):
        for map in maps:
            self.remove_map_from_whitelist(map)

    def reset_map_whitelist(self):
        all_maps = self._rcon.get_maps()
        self.set_map_whitelist(all_maps)

    @validate_maps
    def set_map_whitelist(self, maps: Iterable[Layer]):
        if len([*maps]) < 1:
            raise Exception("Votemap whitelist must have at least 1 one map.")
        self._state.set_whitelist(maps)

    def get_selection(self) -> list[Layer]:
        return self._state.get_selection()

    def reset_selection(self):
        self._state.delete_selection()

    def rebuild_selection(self):
        self.set_selection(self.get_new_selection())

    @validate_maps
    def set_selection(self, maps: Iterable[Layer]):
        if len([*maps]) > self.SELECTION_LIMIT:
            raise SelectionLimitExceeded(
                f"Cannot change votemap selection. Max selection limit {self.SELECTION_LIMIT} would be exceeded."
            )
        # if has player choice exclude the first item from being sorted
        maps = list(maps)
        if self.get_player_choice():
            sorted_map_selection = [maps[0]] + sort_maps_by_gamemode(maps[1:])
        else:
            sorted_map_selection = sort_maps_by_gamemode(maps)

        self._state.set_selection(sorted_map_selection)

    @validate_maps
    def add_map_to_selection(self, map: Layer, index: int | None = None):
        selection = self.get_selection()
        if len(selection) >= self.SELECTION_LIMIT:
            raise SelectionLimitExceeded(
                f"Cannot add map {map.pretty_name} to votemap selection. Max selection limit {self.SELECTION_LIMIT} would be exceeded."
            )
        if map in selection:
            raise VoteMapException(
                f"Map {map.pretty_name} is already in the selection."
            )

        if index is not None:
            selection.insert(index, map)
        else:
            selection.append(map)

        self.set_selection(selection)

    @validate_maps
    def remove_map_from_selection(self, map: Layer):
        selection = self.get_selection()
        position = -1
        for idx, m in enumerate(selection):
            if m.id == map.id:
                position = idx
                break
        if position == -1:
            raise Exception(f"Map {map.pretty_name} is not in the selection.")

        if self.get_player_choice() and position == 0:
            self.delete_player_choice()
        else:
            self._state.remove_map_from_selection(map)
        self._delete_votes_by_map(map)
        self.apply_results()

    def _delete_vote(self, player_id: str):
        self._state.delete_vote(player_id)
        try:
            self._rcon.message_player(
                player_id,
                "VOTE MAP\n\nYour vote has been removed.",
            )
        except (HLLCommandFailedError, HLLCommandError):
            logger.info(
                "Unable to message %s. The player may not be on the server.", player_id
            )

    def _delete_votes_by_map(self, map: Layer):
        votes_to_delete = [v for v in self.get_votes() if v["map_id"] == map.id]
        for vote in votes_to_delete:
            self._delete_vote(vote["player_id"])

    @validate_maps
    def guarantee_next_map(self, map: Layer):
        self.set_admin_next_map(map)
        self.apply_results()

    @validate_maps
    def add_vote(
        self,
        map: Layer,
        player_id: str,
        player_name: str,
        vote_count: int | None = None,
    ):

        if map not in self.get_selection():
            raise Exception(
                f"Map {map.pretty_name} is not in the selection. Vote could not be counted."
            )

        if vote_count is None:
            try:
                # get vote count based on vip or flags
                vote_count = self._get_vote_count(self._get_player(player_id))
            except:
                # if player not found or any other issue default to 1
                vote_count = 1
        elif vote_count < 1:
            raise Exception("Number of votes must be 1 or greater.")

        self._state.add_vote(
            player_id=player_id, player_name=player_name, map=map, vote_count=vote_count
        )

    def get_new_selection(self) -> list[Layer]:
        config = self.config
        new_selection = []
        maps_history = [self.parse_layer(m["name"]) for m in self._maps_history]
        current_map = self._maps_history.get_current_map()
        options = {
            "maps_history": maps_history,
            # Map history is updated before votemap is restarted on match start,
            # while Rcon.current_map may still contain the previous cached layer.
            "current_map": (
                self.parse_layer(current_map["name"])
                if current_map
                else self._rcon.current_map
            ),
            "allowed_maps": set(self.get_map_whitelist()),
            **config.model_dump(),
        }

        logger.debug(
            """
            Generating new map selection for vote map with the following criteria:
            %s
            %s
            """,
            self._rcon.get_maps(),
            config,
        )

        try:
            new_selection = self.__suggest_new_selection(**options)
        except RestrictiveFilterError:
            logger.warning(
                "Falling back on all possible maps since the filters are too restrictive"
            )
            options["allowed_maps"] = set(
                self.parse_layer(m) for m in self._rcon.get_maps()
            )
            new_selection = self.__suggest_new_selection(**options)

        return new_selection

    def get_status(self, sort_by_vote: bool = True) -> VoteMapStatus:
        if not self.config.enabled:
            return VoteMapStatus(
                enabled=False,
                paused=False,
                results=[],
                last_reminder=None,
                next_map=None,
                player_choice=None,
            )

        votes = self.get_votes()
        map_states: dict[str, VoteMapMapResult] = {
            map.id: VoteMapMapResult(
                voters=[],
                map=map,
                votes_count=0,
            )
            for map in self.get_selection()
        }
        for vote in votes:
            try:
                state = map_states[vote["map_id"]]
                state["voters"].append(
                    {
                        "player_id": vote["player_id"],
                        "player_name": vote["player_name"],
                        "count": vote["vote_count"],
                    }
                )
                state["votes_count"] += vote["vote_count"]
            except KeyError:
                logger.exception("Invalid vote. Map not in the selection", vote)

        results = list(map_states.values())
        if sort_by_vote:
            results = sorted(results, key=lambda d: d["votes_count"], reverse=True)

        next_map = self.get_next_map()
        if next_map:
            next_map = next_map.pretty_name
        return {
            "enabled": True,
            "paused": self.paused,
            "results": results,
            "last_reminder": self.get_last_reminder_time(),
            "next_map": next_map,
            "player_choice": self.get_player_choice(),
        }

    def get_player_choice(self) -> Dict[str, str] | None:
        return self._state.get_player_choice()

    def delete_player_choice(self):
        """Clears player choice slot and removes the first map from the selection."""
        if not self.get_player_choice():
            return
        self._state.delete_player_choice()
        selection = self.get_selection()
        if len(selection) == 0:
            return
        self.set_selection(selection[1:])

    def get_results(self):
        return self._state.get_results()

    def record_result(self, map_info: MapInfo):
        ts = int(map_info["end"] or datetime.now().timestamp())
        self._state.add_result(self.get_status(), map_info["name"], ts)

    #########################
    #                       #
    #       BEHAVIOUR       #
    #                       #
    #########################

    def reset(self):
        self.reset_votes()
        self.reset_selection()
        self.reset_next_map()
        self.reset_admin_next_map()
        self.delete_player_choice()

    def restart(self):
        self.reset()
        if self.enabled:
            self.rebuild_selection()
            self.apply_results()

    def get_paused_message(self):
        if not (map := self.get_admin_next_map()):
            raise VoteMapException("The admin next map was not set")
        return f"VOTE MAP PAUSED (for this round)\n\nNext map: {map.pretty_name}"

    def is_time_for_reminder(self) -> bool:
        reminder_frequency = self.config.reminder_frequency_minutes * 60
        last_time_reminded = self._state.get_last_reminder_time()

        reminder_disabled = reminder_frequency == 0
        if reminder_disabled:
            return False

        not_reminded_yet = last_time_reminded is None
        if not_reminded_yet:
            return True

        time_since_last_reminder = (
            datetime.now(tz=UTC) - last_time_reminded
        ).total_seconds()
        if time_since_last_reminder > reminder_frequency:
            return True
        return False

    def get_result_message(self, status: VoteMapStatus | None = None) -> str:
        if not status:
            status = self.get_status()
        return f"""
        ### Vote map result
        Winner map: `{status["next_map"]}`
        Total votes: `{sum([d["votes_count"] for d in status["results"]])}`
        {"\n".join([f"1. {d["map"].pretty_name} [{d["votes_count"]} votes]" for d in status['results']])}
        """

    def _get_optin_players(self) -> List[Tuple[str, str]]:
        online_players = self._rcon.get_player_ids()
        online_player_ids = [player_id for _, player_id in online_players]

        # No players online
        if len(online_players) == 0:
            return []

        # Get players who opt-out from reminders
        opted_out = {}
        try:
            with enter_session() as sess:
                res = (
                    sess.query(PlayerOptins)
                    .join(PlayerID)
                    .filter(
                        and_(
                            PlayerID.player_id.in_(online_player_ids),
                            PlayerOptins.optin_name == self.OPTIN_NAME,
                            PlayerOptins.optin_value == "false",
                        )
                    )
                    .all()
                )
                opted_out = {p.player.player_id for p in res}
        except Exception:
            logger.exception("Cannot get votemap reminder optins.")

        optin_players = list(
            filter(
                lambda player: (
                    player[1] not in opted_out if self.config.allow_opt_out else True
                ),
                online_players,
            )
        )
        return optin_players

    @require_enabled
    def send_reminder(self, force: bool = False) -> ActionResult:
        """
        Send vote reminder to all players except the ones
        who opted out of reminders.\n
        Forcing will ignore reminder frequency cooldown
        """
        logger.debug("Attempting to send votemap reminder.")
        config = self.config
        instructions = config.instruction_text

        if not self.is_time_for_reminder() and not force:
            return ActionResult(
                ok=False,
                outcome=ActionOutcome.ON_COOLDOWN,
                message="Cooldown not elapsed and reminder not forced.",
            )

        if self.paused and not force:
            return ActionResult(
                ok=False,
                outcome=ActionOutcome.PAUSED,
                message="Votemap is paused as admin set the next map and reminder not forced.",
            )

        if "{map_selection}" not in instructions:
            logger.error(
                "Votemap is not configured properly, %s is not present in the instruction text.",
                "map_selection",
            )
            return ActionResult(
                ok=False,
                outcome=ActionOutcome.INVALID_CONFIG,
                message="'{map_selection}' missing from instruction text.",
            )

        players_to_remind = list(
            filter(
                lambda player: not self.has_player_voted(player[1]),
                self._get_optin_players(),
            )
        )

        if self.paused:
            reminder_message = self.get_paused_message()
        else:
            map_selection = self.format_map_vote(
                selection=self.get_selection(),
                votes=self.get_votes(),
                format_type="by_mod_vertical_all",
                player_choice=self.get_player_choice(),
            )
            reminder_message = instructions.format(map_selection=map_selection)

        for name, player_id in players_to_remind:
            try:
                self._rcon.message_player(
                    player_id=player_id,
                    message=reminder_message,
                )
            except HLLCommandFailedError:
                logger.warning("Unable to message %s", name)

        self.set_last_reminder_time()
        return ActionResult(
            ok=True,
            outcome=ActionOutcome.SUCCESS,
        )

    def has_player_voted(self, player_id: str) -> bool:
        return True if self._state.get_vote(player_id) else False

    @require_enabled
    def handle_vote_command(self, struct_log: StructuredLogLineWithMetaData) -> bool:
        """Handles (!vm|!votemap) chat command and returns True if handled as expected, False otherwise."""
        sub_content = struct_log.get("sub_content")
        message = sub_content.strip() if sub_content else ""
        config = self.config
        rcon = self._rcon

        if not message.lower().startswith(("!votemap", "!vm")):
            return False

        player_id = struct_log["player_id_1"]
        if not player_id:
            logger.error("Player id could not parsed from log.")
            if player_id is not None:
                rcon.message_player(player_id=player_id, message="Invalid vote.")
            return False

        cmd_handler = VoteMapCommandHandler(self, self._rcon, config)
        return cmd_handler.execute(struct_log, player_id)

    def _get_player_permissions(self, player: PlayerProfileType) -> VotemapPermissions:
        perm = VotemapPermissions(0)
        config = self.config
        player_flags = {flag_record["flag"] for flag_record in player["flags"]}
        is_vip = any(
            vip["player_id"] == player["player_id"] for vip in self._rcon.get_vip_ids()
        )
        not_banned = not set(config.vote_ban_flags) & set(player_flags)

        if (
            not_banned
            and (not config.allow_vip_only or (config.allow_vip_only and is_vip))
            and (
                not config.allow_flag_only
                or (player_flags & set(config.allow_flag_only))
            )
        ):
            perm |= VotemapPermissions.REGISTER_VOTE
        else:
            return perm

        if not config.player_choice_flags or (
            player_flags & set(config.player_choice_flags)
        ):
            perm |= VotemapPermissions.REGISTER_CHOICE

        return perm

    def _get_vote_count(self, player: PlayerProfileType) -> int:
        # Check for player's flags and vip status
        # Pick the one with the highest vote_count
        is_player_vip = any(
            vip["player_id"] == player["player_id"] for vip in self._rcon.get_vip_ids()
        )
        player_flags = list(
            map(lambda flag_record: flag_record["flag"], player["flags"])
        )
        vote_counts = []
        if is_player_vip:
            vote_counts.append(self.config.vip_vote_count)
        for flag in self.config.vote_flags:
            if flag.flag in player_flags:
                vote_counts.append(flag.vote_count)
        vote_count = max(vote_counts, default=1)
        return vote_count

    def register_vote(
        self,
        player: PlayerProfileType,
        timestamp: int,
        entry: int,
    ):
        """
        Checks whether the player exists, the vote is not too old and
        if there is any game going on.\n
        If all checks pass, it saves `entry` as the players selected map
        with the `count` number of votes.\n
        This also allows voting for players outside the server.\n
        """
        if self.paused:
            raise VoteMapException(self.get_paused_message())

        player_name = player["names"][0]["name"]
        player_id = player["player_id"]

        if VotemapPermissions.REGISTER_VOTE not in self._get_player_permissions(player):
            raise PlayerVoteNotAllowed(
                "NOT ALLOWED!\n\nYou are not allowed to use this command on this server."
            )

        vote_count = self._get_vote_count(player)

        selection = self.get_selection()
        # The selection in-game text starts from index 1 as index 0 is reserved for player's choice
        # However the selection is a list indexed from 0 so the index does not reflect
        # the map's position in the list if the choice is not present
        if not self.get_player_choice():
            start = 1
            end = len(selection) + start
            map_index = entry - start
        else:
            start = 0
            end = len(selection)
            map_index = entry

        try:
            if entry not in range(start, end):
                raise ValueError
            selected_map = selection[map_index]
        except (TypeError, ValueError, IndexError):
            raise InvalidVoteError(
                f"Vote must be a number between {start} and {end - 1}"
            )

        try:
            current_map = self._maps_history[0]
            map_start = current_map["start"]
        except IndexError as e:
            raise VoteMapNoInitialised(
                "Map history is empty - Can't register vote"
            ) from e
        except KeyError as e:
            raise VoteMapNoInitialised(
                "Map history is corrupted - Can't register vote"
            ) from e

        if map_start is None or timestamp < map_start:
            logger.warning(
                "Vote is too old %s, %s, %d, %s",
                player_name,
                timestamp,
                entry,
                current_map,
            )

        # Vote registered
        self._state.add_vote(player_id, player_name, selected_map, vote_count)

        logger.info(
            "Registered vote from %s(%s) for {%s} - {%d}",
            player_name,
            player_id,
            selected_map,
            entry,
        )

        # Recalculate results
        self.apply_results()

        return selected_map

    @validate_maps
    def register_player_choice(self, map_choice: Layer, player: PlayerProfileType):

        if self.paused:
            raise VoteMapException(self.get_paused_message())

        if not (
            self._get_player_permissions(player) & VotemapPermissions.REGISTER_CHOICE
        ):
            raise PlayerChoiceNotAllowed(
                "NOT ALLOWED!\n\nYou are not allowed to use this command on this server."
            )

        if self.get_player_choice():
            raise VoteMapException("Players' map choice was already selected.")

        # Player choice is always at index 0
        self.add_map_to_selection(map_choice, 0)

        player_name = player["names"][0]["name"]
        player_id = player["player_id"]

        self._state.set_player_choice(player_id, player_name)

    def get_vote_overview(self) -> list[tuple[Layer, int]]:
        counter = self.get_selection_counter()
        if not counter:
            return []
        ranked_maps = counter.most_common()
        return [
            (self.parse_layer(map_id), vote_count) for map_id, vote_count in ranked_maps
        ]

    def reset_votes(self):
        self._state.delete_votes()

    def get_selection_counter(self) -> Counter[str] | None:
        selection = set(self.get_selection())
        valid_votes = [vote for vote in self.get_votes() if vote["map_id"] in selection]
        if len(valid_votes) == 0:
            return None
        counter = Counter()
        for vote in valid_votes:
            counter[vote["map_id"]] += vote["vote_count"]
        return counter

    def get_most_voted_map(self) -> Layer | None:
        counter = self.get_selection_counter()
        if not counter:
            return None
        most_voted_map, _ = counter.most_common()[0]
        return self.parse_layer(most_voted_map)

    def _get_least_played_map(self, maps_to_pick_from: list[Layer]) -> Layer:

        if not maps_to_pick_from:
            raise ValueError(
                "Cannot get the least played map as a default map. There are no maps to pick from."
            )

        map_id_counts = dict(Counter(map["name"] for map in self._maps_history))
        least_played_map, max_count = maps_to_pick_from[0], float("inf")

        for map in maps_to_pick_from:
            count = map_id_counts.get(map.id, 0)
            if count == 0:
                least_played_map = map
                break
            if count < max_count:
                least_played_map = map
                max_count = count

        return least_played_map

    def _get_default_next_map(self) -> Layer:
        selection = self.get_selection()
        all_maps = self._rcon.get_maps()
        config = self.config

        if not config.allow_default_to_offensive:
            logger.debug(
                "Not allowing default to offensive, removing all offensive maps"
            )
            selection = [m for m in selection if m.game_mode != maps.GameMode.OFFENSIVE]
            all_maps = [m for m in all_maps if m.game_mode != maps.GameMode.OFFENSIVE]

        if not config.allow_default_to_skirmish:
            logger.debug("Not allowing default to skirmish, removing all skirmish maps")
            selection = [m for m in selection if not m.game_mode.is_small()]
            all_maps = [m for m in all_maps if not m.game_mode.is_small()]

        if not self._maps_history:
            choice = random.choice(self.get_map_whitelist())
            return choice

        last_played_map = lambda map: map.id != self._maps_history[0]["name"]

        try:
            next_default_map: Layer = {
                DefaultMethods.least_played_suggestions: partial(
                    self._get_least_played_map,
                    selection,
                ),
                DefaultMethods.least_played_all_maps: partial(
                    self._get_least_played_map,
                    all_maps,
                ),
                DefaultMethods.random_all_maps: lambda: random.choice(
                    list(filter(last_played_map, all_maps))
                ),
                DefaultMethods.random_suggestions: lambda: random.choice(
                    list(filter(last_played_map, selection))
                ),
            }[config.default_method]()
        except Exception as e:
            logger.exception(e)
            next_default_map = random.choice(list(filter(last_played_map, all_maps)))
            logger.info(
                "Next default map was randomly picked from all maps - %s",
                next_default_map,
            )

        return next_default_map

    def __suggest_new_selection(
        self,
        maps_history: list[maps.Layer],
        current_map: maps.Layer,
        allowed_maps: set[maps.Layer],
        number_last_played_to_exclude: int,
        num_warfare_options: int,
        num_offensive_options: int,
        num_skirmish_control_options: int,
        consider_offensive_same_map: bool,
        consider_skirmishes_as_same_map: bool,
        consider_environment_as_same_map: bool,
        allow_multiple_maps_with_same_environment: bool,
        allow_consecutive_offensives: bool,
        allow_consecutive_offensives_opposite_sides: bool,
        allow_consecutive_skirmishes: bool,
        **kwargs,
    ) -> list[maps.Layer]:
        """Delegate map selection generation to MapSelectionBuilder."""
        criteria = MapSelectionCriteria(
            maps_history=maps_history,
            current_map=current_map,
            allowed_maps=allowed_maps,
            number_last_played_to_exclude=number_last_played_to_exclude,
            num_warfare_options=num_warfare_options,
            num_offensive_options=num_offensive_options,
            num_skirmish_control_options=num_skirmish_control_options,
            consider_offensive_same_map=consider_offensive_same_map,
            consider_skirmishes_as_same_map=consider_skirmishes_as_same_map,
            consider_environment_as_same_map=consider_environment_as_same_map,
            allow_multiple_maps_with_same_environment=allow_multiple_maps_with_same_environment,
            allow_consecutive_offensives=allow_consecutive_offensives,
            allow_consecutive_offensives_opposite_sides=allow_consecutive_offensives_opposite_sides,
            allow_consecutive_skirmishes=allow_consecutive_skirmishes,
        )
        return MapSelectionBuilder().build(criteria)

    def generate_next_map(self) -> Layer:
        if admin_next_map := self.get_admin_next_map():
            return admin_next_map
        most_voted_map = self.get_most_voted_map()
        if not most_voted_map:
            next_map = self._get_default_next_map()
            logger.warning(
                "No votes recorded, defaulting with %s using default winning map %s",
                self.config.default_method.value,
                next_map,
            )
        else:
            next_map = most_voted_map

        if next_map not in self._rcon.get_maps():
            logger.error(
                "%s is not part of the all map list maps=%s",
                next_map,
                self._rcon.get_maps(),
            )
        if next_map not in (selection := self.get_selection()):
            logger.info("%s is not part of vote selection %s", next_map, selection)

        logger.info("Next map %s", next_map)
        return next_map

    @require_enabled
    def apply_results(self, retries: int = 2) -> Layer | None:
        """
        Replaces the current map rotation on the server with a single map.\n
        The map with the most votes is selected.\n
        If no votes were registered, user selected default method is applied to find one.\n

        :return The selected map
        """
        next_map = self.generate_next_map()

        # Apply rotation safely

        current_rotation = self._rcon.get_map_rotation()["maps"]

        while len(current_rotation) > 1:
            # Make sure only 1 map is in rotation
            map_ = current_rotation.pop(1)
            self._rcon.remove_map_from_rotation(map_.id)

        current_next_map = current_rotation[0]
        if current_next_map != next_map:
            # Replace the only map left in rotation
            self._rcon.add_map_to_rotation(next_map.id)
            self._rcon.remove_map_from_rotation(current_next_map.id)

        # Check that it worked
        current_rotation = self._rcon.get_map_rotation()["maps"]
        if len(current_rotation) != 1 or current_rotation[0] != next_map:
            if retries > 0:
                return self.apply_results(retries - 1)
            else:
                logger.error(
                    "Applying the votemap results failed. Next map %s. Rotation: %s",
                    next_map,
                    current_rotation,
                )
                return None

        self.set_next_map(next_map)
        logger.info(
            "Successfully applied next map %s, rotation %s",
            next_map,
            current_rotation,
        )
        return next_map

    @ttl_cache(ttl=5)
    def _get_player(self, player_id: str) -> PlayerProfileType:
        with enter_session() as db_session:
            try:
                player = db_session.query(PlayerID).filter_by(player_id=player_id).one()
                player = player.to_dict()
            except NoResultFound as e:
                raise PlayerNotFound(f"Player {player_id=} not found.") from e
            except MultipleResultsFound as e:
                raise Exception(
                    f"Multiple entries found for player {player_id=}."
                ) from e
            except Exception as e:
                raise PlayerNotFound(
                    f"Something went wrong while searching for your {player_id=} profile."
                )
        return player


class VoteMapCommandHandler:
    VOTE_CMD_PATTERN = re.compile(r"(!votemap|!vm)\s*(\d+)", re.IGNORECASE)
    HELP_CMD_PATTERN = re.compile(r"(!votemap|!vm)\s*help", re.IGNORECASE)
    SHOW_CMD_PATTERN = re.compile(r"(!votemap|!vm)$", re.IGNORECASE)
    NEVER_CMD_PATTERN = re.compile(r"(!votemap|!vm)\s*never$", re.IGNORECASE)
    ALLOW_CMD_PATTERN = re.compile(r"(!votemap|!vm)\s*allow$", re.IGNORECASE)
    CHOICE_CMD_PATTERN = re.compile(r"(!votemap|!vm)\s*add(.*)", re.IGNORECASE)

    def __init__(self, votemap: VoteMap, rcon: Rcon, config: VoteMapUserConfig):
        self.votemap = votemap
        self.rcon = rcon
        self.config = config

    def execute(self, log: StructuredLogLineWithMetaData, player_id: str):
        """Returns `True` if handled as expected, `False` otherwise."""

        if (datetime.now() - timedelta(minutes=3)) > log["event_time"]:
            logger.info("Log entry is more than 3 minutes old - no execution")
            return False

        message = (log.get("sub_content") or "").strip()

        try:
            if match := self.VOTE_CMD_PATTERN.match(message):
                entry = int(match.group(2))
                self.handle_vote(player_id, log, entry)
            elif self.HELP_CMD_PATTERN.match(message):
                self.handle_help(player_id, log)
            elif self.SHOW_CMD_PATTERN.match(message):
                self.handle_show_selection(player_id)
            elif self.NEVER_CMD_PATTERN.match(message):
                self.handle_opt_out(player_id)
            elif self.ALLOW_CMD_PATTERN.match(message):
                self.handle_opt_in(player_id)
            elif match := self.CHOICE_CMD_PATTERN.match(message):
                args = match.group(2).strip().lower().split()
                logger.debug(args)
                if len(args) < 1 or args[0] == "help":
                    self.handle_player_choice_help(player_id)
                else:
                    self.handle_player_choice(player_id, *args)
            else:
                # fallback
                message = "INVALID COMMAND!\n" + (
                    self.config.help_text or "Type '!votemap help' in the chat."
                )
                self.rcon.message_player(player_id=player_id, message=message)
        except VoteMapException as e:
            self.rcon.message_player(player_id=player_id, message=str(e))
            return False
        except Exception as e:
            self.rcon.message_player(
                player_id=player_id,
                message="Something went wrong!\n\nSorry about that.",
            )
            logger.exception(str(e))
            return False

        return True

    def handle_player_choice_help(self, player_id: str):
        all_maps = self.rcon.get_maps()
        tag_to_id = {m.map.tag: m.map.shortname for m in all_maps}
        environments = [weather.value for weather in Environment]
        game_modes = [mode.value for mode in GameMode]
        teams = ["axis", "allies"]
        help_text = self.config.player_choice_help_text or PLAYER_CHOICE_HELP_TEXT
        help_text += (
            """

        <map_tag> options:
        """
            + "\n".join(f"{key} -> {value}" for key, value in tag_to_id.items())
            + """

        [game_mode] options:
        """
            + "\n".join(game_modes)
            + """

        [attackers] options:
        """
            + "\n".join(teams)
            + """

        [environment] options:
        """
            + "\n".join(environments)
        )
        self.rcon.message_player(player_id=player_id, message=help_text)

    def handle_player_choice(
        self,
        player_id: str,
        *args,
    ):
        """
        Provide args in the following order:\n
        <map_tag> [game_mode] [attackers | only if game_mode=offensive] [environment]
        """
        all_maps = self.rcon.get_maps()
        tag_to_id = {m.map.tag: m.map.shortname for m in all_maps}
        environments = [weather.value for weather in Environment]
        game_modes = [mode.value for mode in GameMode]
        teams = ["axis", "allies"]
        params = list(args)

        if (
            not (map_tag := self.__get_next_param(params))
            or map_tag.upper() not in tag_to_id
        ):
            raise InvalidMapParam(
                f"""INVALID MAP\n
                OPTIONS:\n\
                {"\n".join(f"{key} -> {value}" for key, value in tag_to_id.items())}"""
            )

        if (game_mode := self.__get_next_param(params, "warfare")) not in game_modes:
            raise InvalidMapParam(
                f"""INVALID GAME MODE\n
                OPTIONS:\n\
                {"\n".join(game_modes)}"""
            )

        attackers = None
        if game_mode == GameMode.OFFENSIVE.value:
            if (attackers := self.__get_next_param(params, "allies")) not in teams:
                raise InvalidMapParam(
                    f"""INVALID ATTACK TEAM\n                    
                    When choosing the Offensive mode, you must specify attacking team to select environment.\n
                    => {map_tag} {game_mode} <{" | ".join(teams)}> [env]\n                    
                    OPTIONS:
                    {"\n".join(teams)}"""
                )

        if (environment := self.__get_next_param(params, "day")) not in environments:
            raise InvalidMapParam(
                f"""INVALID ENVIRONMENT\n
                OPTIONS:\n
                {"\n".join(environments)}"""
            )

        map_found = list(
            filter(
                lambda m: m.map.tag == map_tag.upper()
                and m.game_mode == game_mode
                and m.attackers == attackers
                and m.environment == environment,
                all_maps,
            )
        )

        if len(map_found) == 0:
            raise InvalidMapParam(
                f"""INVALID OPTIONS\n
                The map with the given options does not exist.\n
                OPTIONS:\n
                {"\n".join([f"{map_tag=}", f"{game_mode=}", f"{environment=}"])}"""
            )

        map_choice = map_found[0]

        success_msg = f"""SUCCESS\n
        Map selected:
        {map_choice.pretty_name}\n\n
        Your vote was registered.
        Type !vm too see the new selection"""

        player = self.votemap._get_player(player_id)
        self.votemap.register_player_choice(map_choice, player)
        # Automatically register player's vote for the selected map
        timestamp = int(datetime.now().timestamp())
        self.votemap.register_vote(player, timestamp, entry=0)  # It's always at index 0
        self.rcon.message_player(player_id=player_id, message=success_msg)

    def handle_vote(
        self, player_id: str, log: StructuredLogLineWithMetaData, entry: int
    ):
        logger.info("Registering vote %s", log)
        player = self.votemap._get_player(player_id)
        player_id = player["player_id"]
        try:
            map = self.votemap.register_vote(player, log["timestamp_ms"] // 1000, entry)
        except InvalidVoteError as e:
            exception_message = f"INVALID VOTE!\n{e}\n{self.config.help_text or "Type '!votemap' in the chat."}"
            raise VoteMapException(exception_message) from e
        except VoteMapNoInitialised as e:
            raise VoteMapException(
                "We cannot register your vote at this time.\nVote map is not initialised"
            ) from e
        else:
            if msg := self.config.thank_you_text:
                msg = msg.format(
                    player_name=log["player_name_1"],
                    map_name=map.pretty_name,
                )
                self.rcon.message_player(player_id=player_id, message=msg)

    def handle_help(self, player_id: str, log: StructuredLogLineWithMetaData):
        logger.info("Showing help %s", log)
        self.rcon.message_player(
            player_id=player_id,
            message=self.config.help_text or HELP_TEXT,
        )

    def handle_show_selection(self, player_id: str):
        logger.info("Showing vote selection to %s", player_id)

        if self.votemap.paused:
            self.rcon.message_player(
                player_id=player_id,
                message=self.votemap.get_paused_message(),
            )
            return

        overview = self.votemap.format_map_vote(
            selection=self.votemap.get_selection(),
            votes=self.votemap.get_votes(),
            format_type="by_mod_vertical_all",
            player_choice=self.votemap.get_player_choice(),
        )

        message = "VOTE MAP OVERVIEW"
        message += "\n"
        message += "-------------------"
        message += "\n"
        message += overview
        message += "\n"
        message += "-------------------"
        message += "\n"

        player_vote = self.votemap.get_vote(player_id)
        if player_vote:
            message += f"You've voted for {self.votemap.parse_layer(player_vote["map_id"]).pretty_name}"
        else:
            message += ">>> You have not voted yet! <<<"

        self.rcon.message_player(
            player_id=player_id,
            message=message,
        )

    def handle_opt_out(self, player_id: str):
        if not self.config.allow_opt_out:
            raise VoteMapException(
                "You cannot opt-out of vote map reminders on this server."
            )

        logger.info("Player %s opting out of vote reminders", player_id)

        with enter_session() as sess:
            player = get_player(sess, player_id)
            if player is None:
                logger.exception("Unable to find player record for %s.", player_id)
                raise VoteMapException(
                    "Something went wrong while opting out of vote map reminders.\nPlease try again later."
                )

            reminder_optin = (
                sess.query(PlayerOptins)
                .filter(
                    and_(
                        PlayerOptins.player_id_id == player.id,
                        PlayerOptins.optin_name == self.votemap.OPTIN_NAME,
                    )
                )
                .one_or_none()
            )

            if reminder_optin:
                reminder_optin.optin_value = "false"
            else:
                sess.add(
                    PlayerOptins(
                        player=player,
                        optin_name=self.votemap.OPTIN_NAME,
                        optin_value="false",
                    )
                )

            try:
                sess.commit()
                self.rcon.message_player(
                    player_id=player_id, message="Vote map reminders\nOPTED OUT"
                )
            except Exception as e:
                logger.exception(
                    "Unable to add votemap reminder optin for %s. Exception %s",
                    player_id,
                    str(e),
                )
                raise VoteMapException(
                    "Something went wrong while opting out of vote map reminders.\nPlease try again later."
                )

    def handle_opt_in(self, player_id: str):
        logger.info("Player %s opting in to vote reminders", player_id)

        with enter_session() as sess:
            player = get_player(sess, player_id)
            if player is None:
                logger.exception("Unable to find player record for %s.", player_id)
                raise VoteMapException(
                    "Something went wrong while opting in to vote map reminders.\nPlease try again later."
                )

            reminder_optin = (
                sess.query(PlayerOptins)
                .filter(
                    and_(
                        PlayerOptins.player_id_id == player.id,
                        PlayerOptins.optin_name == self.votemap.OPTIN_NAME,
                    )
                )
                .one_or_none()
            )

            if reminder_optin:
                reminder_optin.optin_value = "true"
            else:
                sess.add(
                    PlayerOptins(
                        player=player,
                        optin_name=self.votemap.OPTIN_NAME,
                        optin_value="true",
                    )
                )

            try:
                sess.commit()
                self.rcon.message_player(
                    player_id=player_id, message="Vote map reminders\nOPTED IN"
                )
            except Exception as e:
                logger.exception(
                    "Unable to add votemap reminder optin for %s. Exception %s",
                    player_id,
                    str(e),
                )
                raise VoteMapException(
                    "Something went wrong while opting in to vote map reminders.\nPlease try again later."
                )

    def __get_next_param(
        self, params: list[str], default: str | None = None
    ) -> str | None:
        """Provide default value for optional params."""
        try:
            return params.pop(0)
        except IndexError:
            return default

from dataclasses import dataclass
from enum import Enum
import functools
import logging
import pickle
import random
import re
from datetime import UTC, datetime
from functools import partial
from typing import Any, Dict, List, Optional, Set, Tuple, cast
from collections.abc import Iterable, Callable
from collections import Counter

from sqlalchemy import and_
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from rcon import maps
from rcon.cache_utils import get_redis_client, ttl_cache
from rcon.maps import (
    Environment,
    GameMode,
    categorize_maps,
    sort_maps_by_gamemode,
)
from rcon.models import PlayerID, PlayerOptins, enter_session
from rcon.player_history import get_player
from rcon.rcon import CommandFailedError, Rcon, get_rcon
from rcon.types import (
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

logger = logging.getLogger(__name__)


def validate_map_ids(func):
    @functools.wraps(func)
    def wrapper(self, map_arg, *args, **kwargs):
        all_map_ids = {m.id for m in self._rcon.get_maps()}
        # Check for string (single map_id)
        if isinstance(map_arg, str):
            if map_arg not in all_map_ids:
                raise Exception(
                    f"Map `{map_arg}` is not a valid map on the game server."
                )
        # Check for iterable of strings (but not a string itself)
        elif isinstance(map_arg, Iterable) and not isinstance(map_arg, str):
            invalid = [mid for mid in map_arg if mid not in all_map_ids]
            if invalid:
                raise Exception(f"Invalid map_ids: {', '.join(invalid)}")
        else:
            raise Exception("Invalid argument type for map_id(s)")
        return func(self, map_arg, *args, **kwargs)

    return wrapper


class ActionOutcome(Enum):
    SUCCESS = "success"
    DISABLED = "disabled"
    ON_COOLDOWN = "on_cooldown"
    INVALID_CONFIG = "invalid_config"


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    outcome: ActionOutcome
    message: Optional[str] = None

    def __bool__(self) -> bool:
        return self.ok


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
        self._state = VotemapState()

        whitelist_not_initialized = len(self._state.get_whitelist()) == 0
        if whitelist_not_initialized:
            self.reset_map_whitelist()

        if self.enabled and not self.get_next_map():
            self.apply_results()
        
        

    @staticmethod
    def require_enabled(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.enabled:
                logger.warning("Method %s skipped: Votemap is disabled", func.__name__)
                return ActionResult(
                    ok=False,
                    outcome=ActionOutcome.DISABLED,
                    message="Votemap is disabled."
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
        selection: list[str],
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
        selection_map_layers = [maps.parse_layer(map_id) for map_id in selection]

        # 0: map 1, 1: map 2, etc.
        vote_dict = {}
        entry_id = 1 if not player_choice else 0
        for map in selection_map_layers:
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
                map_choice = selection_map_layers.pop(0)
                s = f"{player_choice["player_name"]}'s pick:\n"
                s += f"[{maps_to_numbers[map_choice]}] {map_choice.pretty_name} - {ranked_votes[map_choice]}/{total_vote_counts} votes"
                text.append(s)
            categorized = categorize_maps(selection_map_layers)
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
            if len(categorized[maps.GameMode.CONTROL]):
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.GameMode.SKIRMISH],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=total_vote_counts,
                    join_char="\n",
                )
                text.append(f"CONTROL SKIRMISHES:\n{vote_options}")

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

    def get_next_map(self) -> str | None:
        return self._state.get_next_map()

    @validate_map_ids
    def set_next_map(self, map_id: str):
        self._state.set_next_map(map_id)

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

    def get_vote(self, player_id: str) -> VoteMapVote | None:
        return self._state.get_vote(player_id)

    def get_map_whitelist(self):
        return self._state.get_whitelist()

    @validate_map_ids
    def add_map_to_whitelist(self, map_id: str):
        self._state.add_map_to_whitelist(map_id)

    @validate_map_ids
    def add_maps_to_whitelist(self, map_ids: Iterable[str]):
        for map_id in map_ids:
            self._state.add_map_to_whitelist(map_id)

    def remove_map_from_whitelist(self, map_id: str):
        self._state.remove_map_from_whitelist(map_id)

    def remove_maps_from_whitelist(self, map_ids):
        for map_id in map_ids:
            self.remove_map_from_whitelist(map_id)

    def reset_map_whitelist(self):
        all_map_ids = set([map.id for map in self._rcon.get_maps()])
        self.set_map_whitelist(all_map_ids)

    @validate_map_ids
    def set_map_whitelist(self, map_ids: Iterable[str]):
        if len([*map_ids]) < 1:
            raise Exception("Votemap whitelist must have at least 1 one map.")
        self._state.set_whitelist(map_ids)

    def get_selection(self) -> list[str]:
        return self._state.get_selection()

    def reset_selection(self):
        self._state.delete_selection()

    def rebuild_selection(self):
        self.set_selection(self.get_new_selection())

    @validate_map_ids
    def set_selection(self, map_ids: Iterable[str]):
        if len([*map_ids]) > self.SELECTION_LIMIT:
            raise SelectionLimitExceeded(
                f"Cannot change votemap selection. Max selection limit {self.SELECTION_LIMIT} would be exceeded."
            )
        map_ids = set(map_ids)
        sorted_layers = sort_maps_by_gamemode(
            [maps.parse_layer(map_id) for map_id in map_ids]
        )
        map_ids = [map.id for map in sorted_layers]
        self._state.set_selection(map_ids)

    @validate_map_ids
    def add_map_to_selection(self, map_id: str):
        selection = self.get_selection()
        if len(selection) >= self.SELECTION_LIMIT:
            raise SelectionLimitExceeded(
                f"Cannot add {map_id=} to votemap selection. Max selection limit {self.SELECTION_LIMIT} would be exceeded."
            )
        if map_id in selection:
            raise Exception(f"Map {map_id=} is already in the selection.")

        new_selection = selection + [map_id]
        self.set_selection(new_selection)

    def get_new_selection(self) -> list[str]:
        config = self.config
        new_selection = []
        options = {
            "maps_history": [maps.parse_layer(m["name"]) for m in self._maps_history],
            "current_map": self._rcon.current_map,
            "allowed_maps": set(
                [maps.parse_layer(m) for m in self.get_map_whitelist()]
            ),
            **config.model_dump(),
        }

        logger.debug(
            """
            Generating new map selection for vote map with the following criteria:
            %s
            %s
            """,
            self._rcon.get_maps(),
            config
        )

        try:
            new_selection = self.__suggest_new_selection(**options)
        except RestrictiveFilterError:
            logger.warning(
                "Falling back on all possible maps since the filters are too restrictive"
            )
            options["allowed_maps"] = set(
                maps.parse_layer(m) for m in self._rcon.get_maps()
            )
            new_selection = self.__suggest_new_selection(**options)

        return [map.id for map in new_selection]

    def get_status(self, sort_by_vote: bool = True) -> VoteMapStatus:
        if not self.config.enabled:
            return {
            "enabled": False,
            "results": [],
            "last_reminder": None,
            "next_map": None,
        }

        votes = self.get_votes()
        map_states: dict[str, VoteMapMapResult] = {
            map_id: {
                "voters": [],
                "map": maps.parse_layer(map_id),
                "votes_count": 0,
            }
            for map_id in self.get_selection()
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

        if sort_by_vote:
            return sorted(
                map_states.values(), key=lambda d: d["votes_count"], reverse=True
            )
        return {
            "enabled": True,
            "results": list(map_states.values()),
            "last_reminder": self.get_last_reminder_time(),
            "next_map": maps.parse_layer(self.get_next_map()).pretty_name,
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

    #########################
    #                       #
    #       BEHAVIOUR       #
    #                       #
    #########################

    def reset(self):
        self.reset_votes()
        self.reset_selection()
        self.reset_next_map()
        self.delete_player_choice()

    def restart(self):
        self.reset()
        if self.enabled:
            self.rebuild_selection()
            self.apply_results()

    def is_time_for_reminder(self) -> bool:
        reminder_frequency = self.config.reminder_frequency_minutes * 60
        last_time_reminded = self._state.get_last_reminder_time()

        reminder_disabled = reminder_frequency == 0
        if reminder_disabled:
            return False

        not_reminded_yet = last_time_reminded is None
        if not_reminded_yet:
            return True

        time_since_last_reminder = (datetime.now(tz=UTC) - last_time_reminded).total_seconds()
        if time_since_last_reminder > reminder_frequency:
            return True
        return False

    def _get_optin_players(self) -> List[Tuple[str, str]]:
        online_players = self._rcon.get_playerids()
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

        if "{map_selection}" not in instructions:
            logger.error(
                "Votemap is not configured properly, %s is not present in the instruction text.", "map_selection"
            )
            return ActionResult(
                ok=False,
                outcome=ActionOutcome.INVALID_CONFIG,
                message="'{map_selection}' missing from instruction text.",
            )

        players_to_remind = list(
            filter(lambda player: not self.has_player_voted(player[1]), self._get_optin_players())
        )

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
            except CommandFailedError:
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
            rcon.message_player(player_id=player_id, message="Invalid vote.")
            return False

        cmd_handler = VoteMapCommandHandler(self, self._rcon, config)
        return cmd_handler.execute(struct_log, player_id)

    def register_vote(
        self,
        player: PlayerProfileType,
        timestamp: int,
        entry: int,
        count: int | None = None,
    ):
        """
        Checks whether the player exists, the vote is not too old and
        if there is any game going on.\n
        If all checks pass, it saves `entry` as the players selected map
        with the `count` number of votes.\n
        This also allows voting for players outside the server.\n
        """
        player_name = player["names"][0]["name"]
        player_id = player["player_id"]

        player_flags = list(
            map(lambda flag_record: flag_record["flag"], player["flags"])
        )
        if set(self.config.vote_ban_flags).intersection(set(player_flags)):
            raise PlayerVoteMapBan("NOT ALLOWED!\n\nYou are not allowed to use this command on this server.")

        # Vote count is 1 by default
        vote_count = 1
        # If user calls this function directly with count param set use that
        if count is not None:
            vote_count = count
        # Check for player's flags and vip status
        # Pick the one with the highest vote_count
        else:
            vote_counts = []
            is_player_vip = next(
                (
                    vip
                    for vip in self._rcon.get_vip_ids()
                    if vip["player_id"] == player_id
                ),
                False,
            )
            if is_player_vip:
                vote_counts.append(self.config.vip_vote_count)
            for flag in self.config.vote_flags:
                if flag.flag in player_flags:
                    vote_counts.append(flag.vote_count)
            vote_count = max(vote_counts, default=vote_count)

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
            selected_map_id = selection[map_index]
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
                "Vote is too old %s, %s, %d, %s", player_name, timestamp, entry, current_map 
            )

        # Vote registered
        self._state.add_vote(player_id, player_name, selected_map_id, vote_count)

        logger.info(
            "Registered vote from %s(%s) for {%s} - {%d}", player_name, player_id, selected_map_id, entry
        )

        # Recalculate results
        self.apply_results()

        return selected_map_id

    @validate_map_ids
    def register_player_choice(self, map_id: str, player: PlayerProfileType):

        player_flags = list(
            map(lambda flag_record: flag_record["flag"], player["flags"])
        )

        if set(self.config.vote_ban_flags).intersection(set(player_flags)):
            raise PlayerVoteMapBan("NOT ALLOWED!\n\nYou are not allowed to use this command on this server.")

        player_choice_flags = self.config.player_choice_flags
        # If player_choice_flags list is not empty, player needs to have
        # one of the flags set in the config
        if len(player_choice_flags) > 0:
            if not set(player_flags).intersection(set(player_choice_flags)):
                raise PlayerChoiceNotAllowed(
                    "NOT ALLOWED!\n\nYou are not allowed to use this command on this server."
                )

        if self.get_player_choice():
            raise VoteMapException("Players' map choice was already selected.")

        selection = self.get_selection()
        if map_id in selection:
            raise VoteMapException(
                f"{maps.parse_layer(map_id).pretty_name} is already in the selection. Pick another map."
            )

        player_name = player["names"][0]["name"]
        player_id = player["player_id"]

        self._state.set_player_choice(player_id, player_name)
        # Access state's method directly to prevent sorting by game mode
        self._state.set_selection([map_id] + selection)

    def get_vote_overview(self) -> list[tuple[maps.Layer, int]]:
        try:
            counter = self.get_selection_counter()
            if not counter:
                return []
            ranked_maps = counter.most_common()
            return [
                (maps.parse_layer(map_id), vote_count)
                for map_id, vote_count in ranked_maps
            ]
        except Exception:
            logger.exception("Can't produce vote overview")

    def reset_votes(self):
        self._state.delete_votes()

    def get_selection_counter(self) -> Counter | None:
        selection = set(self.get_selection())
        valid_votes = [vote for vote in self.get_votes() if vote["map_id"] in selection]
        if len(valid_votes) == 0:
            return None
        counter = Counter()
        for vote in valid_votes:
            counter[vote["map_id"]] += vote["vote_count"]
        return counter


    def get_most_voted_map(self) -> str | None:
        counter = self.get_selection_counter()
        if not counter:
            return None
        most_voted_map, _ = counter.most_common()[0]
        return most_voted_map

    def _get_least_played_map(self, maps_to_pick_from: list[str]) -> str:

        if not maps_to_pick_from:
            raise ValueError(
                "Cannot get the least played map as a default map. There are no maps to pick from."
            )

        map_id_counts = dict(Counter(map["name"] for map in self._maps_history))
        least_played_map, max_count = maps_to_pick_from[0], float("inf")

        for map_id in maps_to_pick_from:
            count = map_id_counts.get(map_id, 0)
            if count == 0:
                least_played_map = map_id
                break
            if count < max_count:
                least_played_map = map_id
                max_count = count

        return least_played_map

    def _get_default_next_map(self) -> str:
        selection = [maps.parse_layer(m) for m in self.get_selection()]
        all_maps = [maps.parse_layer(m) for m in self._rcon.get_maps()]
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
            choice = random.choice([m for m in self.get_map_whitelist()])
            return choice

        selection = [map.id for map in selection]
        all_maps = [map.id for map in all_maps]
        last_played_map = lambda map: map != self._maps_history[0]["name"]

        try:
            next_default_map: str = {
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
                "Next default map was randomly picked from all maps - %s", next_default_map
            )

        return next_default_map

    def __get_random_map_selection(
        self, maps: list[maps.Layer], nb_to_return: int
    ) -> list[maps.Layer]:
        try:
            if nb_to_return > 0 and len(maps) < nb_to_return:
                nb_to_return = len(maps)
            return random.sample(maps, k=nb_to_return)
        except (IndexError, ValueError):
            return []

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
        allow_consecutive_offensives: bool,
        allow_consecutive_offensives_opposite_sides: bool,
        allow_consecutive_skirmishes: bool,
        **kwargs,
    ) -> list[maps.Layer]:
        if number_last_played_to_exclude > 0:
            last_n_maps = set(m for m in maps_history[:number_last_played_to_exclude])
        else:
            last_n_maps: set[maps.Layer] = set()
        logger.info(
            "Excluding last %s played maps: %s",
            number_last_played_to_exclude,
            [m.pretty_name for m in last_n_maps],
        )
        remaining_maps = [maps.parse_layer(m) for m in (allowed_maps - last_n_maps)]
        logger.info(
            "Remaining maps to suggest from: %s",
            [m.pretty_name for m in remaining_maps],
        )

        current_side = current_map.attackers

        if consider_offensive_same_map or consider_skirmishes_as_same_map:
            # use the id `carentan`, `hill400` etc. to get the base map regardless of game type
            map_ids = set(m.map for m in last_n_maps)
            logger.info(
                "Considering offensive/skirmish mode as same map, excluding %s", map_ids
            )
            remaining_maps = [
                maps.parse_layer(m) for m in remaining_maps if m.map not in map_ids
            ]
            logger.info(
                "Remaining maps to suggest from: %s",
                [m.pretty_name for m in remaining_maps],
            )

        if not allow_consecutive_offensives_opposite_sides and current_side:
            # TODO: make sure this is correct
            remaining_maps = [
                maps.parse_layer(m)
                for m in remaining_maps
                if m.opposite_side != current_side
            ]
            logger.info(
                "Not allowing consecutive offensive with opposite side: %s",
                maps.get_opposite_side(current_side),
            )
            logger.info(
                "Remaining maps to suggest from: %s",
                [m.pretty_name for m in remaining_maps],
            )

        # Handle case if all maps got excluded
        categorized_maps = categorize_maps(remaining_maps)

        warfares: list[maps.Layer] = self.__get_random_map_selection(
            categorized_maps[maps.GameMode.WARFARE], num_warfare_options
        )
        offensives: list[maps.Layer] = self.__get_random_map_selection(
            categorized_maps[maps.GameMode.OFFENSIVE], num_offensive_options
        )
        skirmishes_control: list[maps.Layer] = self.__get_random_map_selection(
            categorized_maps[maps.GameMode.CONTROL], num_skirmish_control_options
        )

        if (
            not allow_consecutive_offensives
            and current_map.game_mode == maps.GameMode.OFFENSIVE
        ):
            logger.info(
                "Current map %s is offensive. Excluding all offensives from suggestions",
                current_map,
            )
            offensives = []

        if not allow_consecutive_skirmishes and current_map.game_mode in (
            maps.GameMode.CONTROL,
            maps.GameMode.PHASED,
            maps.GameMode.MAJORITY,
        ):
            logger.info(
                "Current map %s is skirmish. Excluding all skirmishes from suggestions",
                current_map,
            )
            skirmishes_control = []

        selection = offensives + warfares + skirmishes_control

        if not selection:
            logger.error("No maps can be suggested with the given parameters.")
            raise RestrictiveFilterError("Unable to suggest map")

        logger.info("Suggestion %s", [m.pretty_name for m in selection])
        return selection

    def generate_next_map(self) -> str:
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
            if next_map not in [map.id for map in self._rcon.get_maps()]:
                logger.error(
                    "%s is not part of the all map list maps=%s", next_map, self._rcon.get_maps()
                )
            if next_map not in (selection := self.get_selection()):
                logger.error(
                    "%s is not part of vote selection %s", next_map, selection
                )
            logger.info("Winning map %s", next_map)
        return next_map

    @require_enabled
    def apply_results(self) -> str:
        """
        Replaces the current map rotation on the server with a single map.\n
        The map with the most votes is selected.\n
        If no votes were registered, user selected default method is applied to find one.\n

        :return The selected map_id
        """
        next_map = self.generate_next_map()        

        # Apply rotation safely

        current_rotation = self._rcon.get_map_rotation()["maps"]

        while len(current_rotation) > 1:
            # Make sure only 1 map is in rotation
            map_ = current_rotation.pop(1)
            self._rcon.remove_map_from_rotation(map_.id)

        current_next_map = current_rotation[0].id
        if current_next_map != next_map:
            # Replace the only map left in rotation
            self._rcon.add_map_to_rotation(next_map)
            self._rcon.remove_map_from_rotation(current_next_map)

        # Check that it worked
        current_rotation = self._rcon.get_map_rotation()["maps"]
        if len(current_rotation) != 1 or current_rotation[0].id != next_map:
            raise ValueError(
                f"Applying the winning map {next_map=} failed: {current_rotation=}"
            )

        logger.info(
            "Successfully applied winning map %s, new rotation %s", next_map, current_rotation
        )
        self.set_next_map(next_map)
        return next_map

    def apply_with_retry(self, nb_retry: int = 2):
        success = False

        for i in range(nb_retry):
            try:
                success = self.apply_results()
            except:
                logger.exception("Applying vote map result failed.")
            else:
                break

        if not success:
            logger.warning("Unable to set votemap results")

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
        self.votemap.register_player_choice(map_choice.id, player)
        # Automatically register player's vote for the selected map
        timestamp = int(datetime.now().timestamp())
        self.votemap.register_vote(
            player, timestamp, entry=0
        )  # It's always at index 0
        self.rcon.message_player(player_id=player_id, message=success_msg)

    def handle_vote(
        self, player_id: str, log: StructuredLogLineWithMetaData, entry: int
    ):
        logger.info("Registering vote %s", log)
        player = self.votemap._get_player(player_id)
        player_id = player["player_id"]
        try:
            map_id = self.votemap.register_vote(
                player, log["timestamp_ms"] // 1000, entry
            )
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
                    map_name=maps.parse_layer(map_id).pretty_name,
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
            message += f"You've voted for {maps.parse_layer(player_vote["map_id"]).pretty_name}"
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
                    "Unable to add votemap reminder optin for %s. Exception %s", player_id, str(e)
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
                    "Unable to add votemap reminder optin for %s. Exception %s", player_id, str(e)
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


class VotemapState:
    VERSION = "votemap:version"
    LATEST_REMINDER = "votemap:reminder"
    MAP_WHITELIST = "votemap:whitelist"
    MAP_SELECTION = "votemap:selection"
    VOTES = "votemap:votes"
    PLAYER_CHOICE = "votemap:player-choice"
    NEXT_MAP = "votemap:next-map"

    def __init__(self) -> None:
        self.version = 0.2
        self.client = get_redis_client()
        if self.get_version() != self.version:
            self.delete_last_reminder_time()
            self.delete_next_map()
            self.delete_player_choice()
            self.delete_selection()
            self.delete_votes()
            self.set_version(self.version)

    ###
    # VERSION
    ###
    def get_version(self):
        version = cast(bytes | None, self.client.get(self.VERSION))
        if version is None:
            return None
        return float(version.decode())

    def set_version(self, version: float):
        self.client.set(self.VERSION, version)

    ###
    # PLAYER CHOICE
    ###
    def get_player_choice(self) -> Dict[str, str] | None:
        raw = cast(Dict[bytes, bytes], self.client.hgetall(self.PLAYER_CHOICE))
        if not raw:
            return None
        return {k.decode(): v.decode() for k, v in raw.items()}

    def set_player_choice(self, player_id: str, player_name: str):
        self.client.hset(
            self.PLAYER_CHOICE,
            mapping={"player_name": player_name, "player_id": player_id},
        )

    def delete_player_choice(self):
        self.client.delete(self.PLAYER_CHOICE)

    ###
    # LAST REMINDER TIME
    ###
    def get_last_reminder_time(self) -> datetime | None:
        as_date: datetime | None = None
        res = self.client.get(self.LATEST_REMINDER)
        if res is not None:
            as_date = pickle.loads(res)  # type: ignore
        return as_date

    def set_last_reminder_time(self, the_time: datetime) -> None:
        self.client.set(self.LATEST_REMINDER, pickle.dumps(the_time))

    def delete_last_reminder_time(self) -> None:
        self.client.delete(self.LATEST_REMINDER)

    ###
    # VOTES
    ###
    def get_votes(self) -> list[VoteMapVote]:
        raw_votes = cast(dict[bytes, bytes], self.client.hgetall(self.VOTES))
        return [pickle.loads(vote) for _, vote in raw_votes.items()]

    def delete_votes(self):
        self.client.delete(self.VOTES)

    def get_vote(self, player_id: str) -> VoteMapVote | None:
        vote = cast(bytes | None, self.client.hget(self.VOTES, player_id))
        if not vote:
            return None
        return pickle.loads(vote)

    def add_vote(
        self, player_id: str, player_name: str, map_id: str, vote_count: int = 1
    ):
        vote = pickle.dumps(
            {
                "player_id": player_id,
                "player_name": player_name,
                "map_id": map_id,
                "vote_count": vote_count,
            }
        )
        self.client.hset(self.VOTES, player_id, cast(Any, vote))

    def delete_vote(self, player_id):
        self.client.hdel(self.VOTES, player_id)

    ###
    # MAP WHITELIST
    ###
    def get_whitelist(self) -> set[str]:
        raw = cast(Set[bytes], self.client.smembers(self.MAP_WHITELIST))
        return {item.decode() for item in raw}

    def add_map_to_whitelist(self, map_id: str):
        self.client.sadd(self.MAP_WHITELIST, map_id)

    def remove_map_from_whitelist(self, map_id: str):
        self.client.srem(self.MAP_WHITELIST, map_id)

    def set_whitelist(self, map_ids: Iterable[str]):
        self.client.delete(self.MAP_WHITELIST)
        self.client.sadd(self.MAP_WHITELIST, *map_ids)

    ###
    # MAP SELECTION
    ###
    def get_selection(self) -> list[str]:
        # Get all map ids in order
        raw = cast(Set[bytes], self.client.zrange(self.MAP_SELECTION, 0, -1))
        return [item.decode() for item in raw]

    def set_selection(self, map_ids: Iterable[str]):
        self.delete_selection()
        # Add each map_id with its index as score
        for idx, map_id in enumerate(map_ids):
            self.client.zadd(self.MAP_SELECTION, {map_id: idx})

    def remove_map_from_selection(self, map_id: str):
        self.client.zrem(self.MAP_SELECTION, map_id)

    def delete_selection(self):
        self.client.delete(self.MAP_SELECTION)

    ###
    # NEXT MAP
    ###
    def get_next_map(self):
        next_map = cast(bytes | None, self.client.get(self.NEXT_MAP))
        if next_map is None:
            return None
        return next_map.decode()

    def set_next_map(self, map_id: str):
        self.client.set(self.NEXT_MAP, map_id)

    def delete_next_map(self):
        self.client.delete(self.NEXT_MAP)


class VoteMapException(Exception):
    pass


class SelectionLimitExceeded(Exception):
    pass


class RestrictiveFilterError(Exception):
    pass


class InvalidVoteError(VoteMapException):
    pass


class VoteMapNoInitialised(VoteMapException):
    pass


class PlayerNotFound(Exception):
    pass


class PlayerVoteMapBan(VoteMapException):
    def __init__(self, message="Player is banned from voting"):
        super().__init__(message)


class PlayerChoiceNotAllowed(VoteMapException):
    def __init__(self, message="Player does not have any of required flags."):
        super().__init__(message)


class InvalidMapParam(VoteMapException):
    pass

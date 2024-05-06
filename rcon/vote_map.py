import logging
import pickle
import random
import re
from datetime import datetime
from functools import partial
from typing import Counter, Iterable

import redis
from sqlalchemy import and_

from rcon import maps
from rcon.cache_utils import get_redis_client
from rcon.maps import categorize_maps, numbered_maps, sort_maps_by_gamemode
from rcon.models import PlayerOptins, PlayerSteamID, enter_session
from rcon.player_history import get_player
from rcon.rcon import CommandFailedError, Rcon, get_rcon
from rcon.types import (
    StructuredLogLineWithMetaData,
    VoteMapPlayerVoteType,
    VoteMapResultType,
    VoteOverview,
)
from rcon.user_config.vote_map import DefaultMethods, VoteMapUserConfig
from rcon.utils import MapsHistory

logger = logging.getLogger(__name__)

####################
#
#  See hooks.py for the actual initialization of the vote map
#
#
####################


class RestrictiveFilterError(Exception):
    pass


class InvalidVoteError(Exception):
    pass


class VoteMapNoInitialised(Exception):
    pass


def _get_random_map_selection(
    maps: list[maps.Layer], nb_to_return: int, history=None
) -> list[maps.Layer]:
    # if history:
    # Calculate weights to stir selection towards least played maps
    try:
        if nb_to_return > 0 and len(maps) < nb_to_return:
            nb_to_return = len(maps)
        return random.sample(maps, k=nb_to_return)
    except (IndexError, ValueError):
        return []


def suggest_next_maps(
    maps_history: MapsHistory,
    current_map: maps.Layer,
    whitelist_maps: set[maps.Layer],
    num_warfare: int,
    num_offensive: int,
    num_skirmish_control: int,
    exclude_last_n: int = 4,
    consider_offensive_as_same_map: bool = True,
    allow_consecutive_offensive: bool = True,
    allow_consecutive_offensives_of_opposite_side: bool = False,
    consider_skirmishes_as_same_map: bool = True,
    allow_consecutive_skirmishes: bool = True,
):
    history_as_layers = [maps.parse_layer(m["name"]) for m in maps_history]
    try:
        return _suggest_next_maps(
            maps_history=history_as_layers,
            current_map=current_map,
            allowed_maps=whitelist_maps,
            num_warfare=num_warfare,
            num_offensive=num_offensive,
            num_skirmish_control=num_skirmish_control,
            exclude_last_n=exclude_last_n,
            consider_offensive_as_same_map=consider_offensive_as_same_map,
            allow_consecutive_offensive=allow_consecutive_offensive,
            allow_consecutive_offensives_of_opposite_side=allow_consecutive_offensives_of_opposite_side,
            consider_skirmishes_as_same_map=consider_skirmishes_as_same_map,
            allow_consecutive_skirmishes=allow_consecutive_skirmishes,
        )
    except RestrictiveFilterError:
        logger.warning(
            "Falling back on all possible maps since the filters are too restrictive"
        )
        rcon = get_rcon()
        return _suggest_next_maps(
            maps_history=history_as_layers,
            current_map=current_map,
            allowed_maps=set(maps.parse_layer(m) for m in rcon.get_maps()),
            num_warfare=num_warfare,
            num_offensive=num_offensive,
            num_skirmish_control=num_skirmish_control,
            exclude_last_n=exclude_last_n,
            consider_offensive_as_same_map=consider_offensive_as_same_map,
            allow_consecutive_offensive=allow_consecutive_offensive,
            allow_consecutive_offensives_of_opposite_side=allow_consecutive_offensives_of_opposite_side,
            consider_skirmishes_as_same_map=consider_skirmishes_as_same_map,
            allow_consecutive_skirmishes=allow_consecutive_skirmishes,
        )


def _suggest_next_maps(
    maps_history: list[maps.Layer],
    current_map: maps.Layer,
    allowed_maps: set[maps.Layer],
    exclude_last_n: int,
    num_warfare: int,
    num_offensive: int,
    num_skirmish_control: int,
    consider_offensive_as_same_map: bool,
    allow_consecutive_offensive: bool,
    allow_consecutive_offensives_of_opposite_side: bool,
    consider_skirmishes_as_same_map: bool,
    allow_consecutive_skirmishes: bool,
) -> list[maps.Layer]:
    if exclude_last_n > 0:
        last_n_maps = set(m for m in maps_history[:exclude_last_n])
    else:
        last_n_maps: set[maps.Layer] = set()
    logger.info("Excluding last %s player maps: %s", exclude_last_n, last_n_maps)
    remaining_maps = [maps.parse_layer(m) for m in allowed_maps - last_n_maps]
    logger.info("Remaining maps to suggest from: %s", remaining_maps)

    current_side = current_map.attackers

    if consider_offensive_as_same_map or consider_skirmishes_as_same_map:
        # use the id `carentan`, `hill400` etc. to get the base map regardless of game type
        map_ids = set(m.map for m in last_n_maps)
        logger.info(
            "Considering offensive/skirmish mode as same map, excluding %s", map_ids
        )
        remaining_maps = [
            maps.parse_layer(m) for m in remaining_maps if m.map not in map_ids
        ]
        logger.info("Remaining maps to suggest from: %s", remaining_maps)

    if not allow_consecutive_offensives_of_opposite_side and current_side:
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
        logger.info("Remaining maps to suggest from: %s", remaining_maps)

    # Handle case if all maps got excluded
    categorized_maps = categorize_maps(remaining_maps)

    warfares: list[maps.Layer] = _get_random_map_selection(
        categorized_maps[maps.Gamemode.WARFARE], num_warfare
    )
    offensives: list[maps.Layer] = _get_random_map_selection(
        categorized_maps[maps.Gamemode.OFFENSIVE], num_offensive
    )
    skirmishes_control: list[maps.Layer] = _get_random_map_selection(
        categorized_maps[maps.Gamemode.CONTROL], num_skirmish_control
    )

    if (
        not allow_consecutive_offensive
        and current_map.gamemode == maps.Gamemode.OFFENSIVE
    ):
        logger.info(
            "Current map %s is offensive. Excluding all offensives from suggestions",
            current_map,
        )
        offensives = []

    if not allow_consecutive_skirmishes and current_map.gamemode in (
        maps.Gamemode.CONTROL,
        maps.Gamemode.PHASED,
        maps.Gamemode.MAJORITY,
    ):
        logger.info(
            "Current map %s is skirmish. Excluding all skirmishes from suggestions",
            current_map,
        )
        skirmishes_control = []

    selection = sort_maps_by_gamemode(offensives + warfares + skirmishes_control)

    if not selection:
        logger.error("No maps can be suggested with the given parameters.")
        raise RestrictiveFilterError("Unable to suggest map")

    logger.info("Suggestion %s", selection)
    return selection


# TODO:  Handle empty selection (None)
class VoteMap:
    def __init__(self) -> None:
        self.rcon = get_rcon()
        self.red = get_redis_client()
        self.reminder_time_key = "last_vote_reminder"
        self.optin_name = "votemap_reminder"
        self.whitelist_key = "votemap_whitelist"

    # TODO: fix votes typing
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
        selection: list[maps.Layer],
        votes: dict[str, maps.Layer],
        format_type="vertical",
    ) -> str:
        if len(selection) == 0:
            logger.warning("No vote map selection")
            return ""

        total_votes = len(votes)
        ranked_votes = Counter(votes.values())

        # 0: map 1, 1: map 2, etc.
        vote_dict = numbered_maps(selection)
        # map 1: 0, map 2: 1, etc.
        maps_to_numbers = dict(zip(vote_dict.values(), vote_dict.keys()))

        items = [
            f"[{k}] {v} - {ranked_votes[v]}/{total_votes} votes"
            for k, v in vote_dict.items()
        ]

        if format_type == "vertical":
            return "\n".join(items)
        elif format_type.startswith("by_mod"):
            categorized = categorize_maps(selection)
            # TODO: these aren't actually used anywhere
            off = VoteMap.join_vote_options(
                selection=categorized[maps.Gamemode.OFFENSIVE],
                maps_to_numbers=maps_to_numbers,
                ranked_votes=ranked_votes,
                total_votes=len(votes),
                join_char="  ",
            )
            warfare = VoteMap.join_vote_options(
                selection=categorized[maps.Gamemode.WARFARE],
                maps_to_numbers=maps_to_numbers,
                ranked_votes=ranked_votes,
                total_votes=len(votes),
                join_char="  ",
            )
            # TODO: include skirmish

            vote_string = ""
            if categorized[maps.Gamemode.WARFARE]:
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.Gamemode.WARFARE],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=len(votes),
                    join_char="\n",
                )
                vote_string = f"WARFARES:\n{vote_options}"
            if categorized[maps.Gamemode.OFFENSIVE]:
                if vote_string:
                    vote_string += "\n\n"
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.Gamemode.OFFENSIVE],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=len(votes),
                    join_char="\n",
                )
                vote_string += f"OFFENSIVES:\n{vote_options}"
            if categorized[maps.Gamemode.CONTROL]:
                if vote_string:
                    vote_string += "\n\n"
                vote_options = VoteMap.join_vote_options(
                    selection=categorized[maps.Gamemode.CONTROL],
                    maps_to_numbers=maps_to_numbers,
                    ranked_votes=ranked_votes,
                    total_votes=len(votes),
                    join_char="\n",
                )
                vote_string += f"CONTROL SKIRMISHES:\n{vote_options}"

            return vote_string
        else:
            return ""

    def get_last_reminder_time(self) -> datetime | None:
        as_date: datetime | None = None
        res: bytes = self.red.get(self.reminder_time_key)  # type: ignore
        if res is not None:
            as_date = pickle.loads(res)
        return as_date

    def set_last_reminder_time(self, the_time: datetime | None = None) -> None:
        dt = the_time or datetime.now()
        self.red.set(self.reminder_time_key, pickle.dumps(dt))

    def reset_last_reminder_time(self) -> None:
        self.red.delete(self.reminder_time_key)

    def is_time_for_reminder(self) -> bool:
        config = VoteMapUserConfig.load_from_db()
        reminder_freq_min = config.reminder_frequency_minutes
        if reminder_freq_min == 0:
            return False

        last_time = self.get_last_reminder_time()

        if last_time is None:
            logger.warning("No time for last vote reminder")
            return True

        if (datetime.now() - last_time).total_seconds() > reminder_freq_min * 60:
            return True

        return False

    def vote_map_reminder(self, rcon: Rcon, force=False):
        logger.info("Vote MAP reminder")
        config = VoteMapUserConfig.load_from_db()
        vote_map_message = config.instruction_text

        if not config.enabled:
            return

        if not self.is_time_for_reminder() and not force:
            return

        if "{map_selection}" not in vote_map_message:
            logger.error(
                "Vote map is not configured properly, {map_selection} is not present in the instruction text"
            )
            return

        self.set_last_reminder_time()
        players = rcon.get_playerids()
        # Get optins
        steamd_ids = [steamid for _, steamid in players]
        opted_out = {}

        try:
            with enter_session() as sess:
                res = (
                    sess.query(PlayerOptins)
                    .join(PlayerSteamID)
                    .filter(
                        and_(
                            PlayerSteamID.steam_id_64.in_(steamd_ids),
                            PlayerOptins.optin_name == self.optin_name,
                            PlayerOptins.optin_value == "false",
                        )
                    )
                    .all()
                )
                opted_out = {p.steamid.steam_id_64 for p in res}
        except Exception:
            logger.exception("Can't get optins")

        for name, steamid in players:
            if self.has_voted(name) or (steamid in opted_out and config.allow_opt_out):
                logger.info("Not showing reminder to %s", name)
                continue

            try:
                rcon.message_player(
                    player_id=steamid,
                    message=vote_map_message.format(
                        map_selection=self.format_map_vote(
                            selection=self.get_selection(),
                            votes=self.get_votes(),
                            format_type="by_mod_vertical_all",
                        )
                    ),
                )
            except CommandFailedError:
                logger.warning("Unable to message %s", name)

    def handle_vote_command(
        self, rcon, struct_log: StructuredLogLineWithMetaData
    ) -> bool:
        sub_content = struct_log.get("sub_content")

        message = sub_content.strip() if sub_content else ""
        config = VoteMapUserConfig.load_from_db()
        if not message.lower().startswith(("!votemap", "!vm")):
            return config.enabled

        steam_id_64_1 = struct_log["steam_id_64_1"]
        if not config.enabled:
            return config.enabled

        if match := re.match(r"(!votemap|!vm)\s*(\d+)", message, re.IGNORECASE):
            logger.info("Registering vote %s", struct_log)
            vote = match.group(2)
            try:
                # shouldn't be possible but making the type checker happy
                player = (
                    struct_log["player"]
                    if struct_log["player"]
                    else "PlayerNameNotFound"
                )
                map_name = self.register_vote(
                    player, struct_log["timestamp_ms"] // 1000, vote
                )
            except InvalidVoteError:
                rcon.message_player(player_id=steam_id_64_1, message="Invalid vote.")
                if config.help_text:
                    rcon.message_player(
                        player_id=steam_id_64_1, message=config.help_text
                    )
            except VoteMapNoInitialised:
                rcon.message_player(
                    player_id=steam_id_64_1,
                    message="We can't register you vote at this time.\nVoteMap not initialised",
                )
                raise
            else:
                if msg := config.thank_you_text:
                    msg = msg.format(
                        player_name=struct_log["player"], map_name=map_name
                    )
                    rcon.message_player(player_id=steam_id_64_1, message=msg)
            finally:
                self.apply_results()
                return config.enabled

        if (
            re.match(r"(!votemap|!vm)\s*help", message, re.IGNORECASE)
            and config.help_text
        ):
            logger.info("Showing help %s", struct_log)
            rcon.message_player(player_id=steam_id_64_1, message=config.help_text)
            return config.enabled

        if re.match(r"(!votemap|!vm)$", message, re.IGNORECASE):
            logger.info("Showing selection %s", struct_log)
            vote_map_message = config.instruction_text
            rcon.message_player(
                player_id=steam_id_64_1,
                message=vote_map_message.format(
                    map_selection=self.format_map_vote(
                        selection=self.get_selection(),
                        votes=self.get_votes(),
                        format_type="by_mod_vertical_all",
                    )
                ),
            )
            return config.enabled

        if re.match(r"(!votemap|!vm)\s*never$", message, re.IGNORECASE):
            if not config.allow_opt_out:
                rcon.message_player(
                    player_id=steam_id_64_1,
                    message="You can't opt-out of vote map on this server",
                )
                return config.enabled

            logger.info("Player opting out of vote %s", struct_log)
            with enter_session() as sess:
                player = get_player(sess, steam_id_64_1)
                existing = (
                    sess.query(PlayerOptins)
                    .filter(
                        and_(
                            PlayerOptins.playersteamid_id == player.id,
                            PlayerOptins.optin_name == self.optin_name,
                        )
                    )
                    .one_or_none()
                )
                if existing:
                    existing.optin_value = "false"
                else:
                    sess.add(
                        PlayerOptins(
                            steamid=player,
                            optin_name=self.optin_name,
                            optin_value="false",
                        )
                    )
                try:
                    sess.commit()
                    rcon.message_player(
                        player_id=steam_id_64_1, message="VoteMap Unsubscribed OK"
                    )
                except Exception as e:
                    logger.exception("Unable to add optin. Already exists?")
                self.apply_with_retry()

            return config.enabled

        if re.match(r"(!votemap|!vm)\s*allow$", message, re.IGNORECASE):
            logger.info("Player opting in for vote %s", struct_log)
            with enter_session() as sess:
                player = get_player(sess, steam_id_64_1)
                existing = (
                    sess.query(PlayerOptins)
                    .filter(
                        and_(
                            PlayerOptins.playersteamid_id == player.id,
                            PlayerOptins.optin_name == self.optin_name,
                        )
                    )
                    .one_or_none()
                )
                if existing:
                    existing.optin_value = "true"
                else:
                    sess.add(
                        PlayerOptins(
                            steamid=player,
                            optin_name=self.optin_name,
                            optin_value="true",
                        )
                    )
                try:
                    sess.commit()
                    rcon.message_player(
                        player_id=steam_id_64_1, message="VoteMap Subscribed OK"
                    )
                except Exception as e:
                    logger.exception("Unable to update optin. Already exists?")
            return config.enabled

        rcon.message_player(player_id=steam_id_64_1, message=config.help_text)
        return config.enabled

    def register_vote(self, player_name: str, vote_timestamp: int, vote_content: str):
        try:
            # Map history is used when generating selections
            current_map = MapsHistory()[0]
            min_time = current_map["start"]
        except IndexError as e:
            raise VoteMapNoInitialised(
                "Map history is empty - Can't register vote"
            ) from e
        except KeyError as e:
            raise VoteMapNoInitialised(
                "Map history is corrupted - Can't register vote"
            ) from e

        if min_time is None or vote_timestamp < min_time:
            logger.warning(
                f"Vote is too old {player_name=}, {vote_timestamp=}, {vote_content=}, {current_map=}"
            )

        selection = self.get_selection()

        try:
            vote_idx = int(vote_content)
            selected_map = selection[vote_idx]
            # Winston: utahbeach_warfare
            self.red.hset("VOTES", player_name, str(selected_map))
        except (TypeError, ValueError, IndexError):
            raise InvalidVoteError(
                f"Vote must be a number between 0 and {len(selection) - 1}"
            )

        logger.info(
            f"Registered vote from {player_name=} for {selected_map=} - {vote_content=}"
        )
        return selected_map

    def get_vote_overview(self) -> VoteOverview | None:
        try:
            votes = self.get_votes()
            maps = Counter(votes.values()).most_common()
            return {
                "total_votes": len(votes),
                "winning_maps": [(str(m), v) for m, v in maps],
            }
        except Exception:
            logger.exception("Can't produce vote overview")

    def clear_votes(self) -> None:
        """Clear all votes"""
        self.red.delete("VOTES")

    def has_voted(self, player_name: str) -> bool:
        """Return if the player name has a value set"""
        return self.red.hget("VOTES", player_name) is not None

    def _get_votes(self) -> VoteMapPlayerVoteType:
        """Returns a dict of player names and the map name they voted for"""
        votes: dict[bytes, bytes] = self.red.hgetall("VOTES") or {}  # type: ignore
        # Redis votes are a hash
        # 127.0.0.1:6379[1]> HKEYS VOTES
        # 1) "Winston"
        # 2) "SodiumEnglish"
        # 127.0.0.1:6379[1]> HGET VOTES Winston
        # "hurtgenforest_warfare_v2_night"
        # 127.0.0.1:6379[1]> HGET VOTES SodiumEnglish
        # "kharkov_warfare"
        # 127.0.0.1:6379[1]> HGETALL VOTES
        # 1) "Winston"
        # 2) "utahbeach_warfare"
        # 3) "SodiumEnglish"
        # 4) "foy_offensive_us"
        return {k.decode(): v.decode() for k, v in votes.items()}

    def get_votes(self) -> dict[str, maps.Layer]:
        votes = self._get_votes()
        return {k: maps.parse_layer(v) for k, v in votes.items()}

    def get_current_map(self) -> maps.Layer:
        """Return the current map name with _RESTART stripped if present"""
        map_ = self.rcon.get_map()
        if map_.endswith("_RESTART"):
            map_ = map_.replace("_RESTART", "")

        return maps.parse_layer(map_)

    def get_map_whitelist(self) -> set[maps.Layer]:
        """Return the set of map names on the whitelist or all possible game server maps if not configured"""
        res = self.red.get(self.whitelist_key)
        if res is not None:
            return pickle.loads(res)  # type: ignore

        return set(maps.parse_layer(map_) for map_ in self.rcon.get_maps())

    def add_map_to_whitelist(self, map_name: str):
        if map_name not in self.rcon.get_maps():
            raise ValueError(
                f"`{map_name}` is not a valid map on the game server, you may need to clear your cache"
            )

        whitelist = self.get_map_whitelist()
        whitelist.add(maps.parse_layer(map_name))
        self.set_map_vm_whitelist(whitelist)

    def add_maps_to_vm_whitelist(self, map_names: Iterable[str]):
        for map_name in map_names:
            self.add_map_to_whitelist(map_name.lower())

    def remove_map_from_vm_whitelist(self, map_name: str):
        whitelist = self.get_map_whitelist()
        whitelist.discard(maps.parse_layer(map_name))
        self.set_map_vm_whitelist(whitelist)

    def remove_maps_from_vm_whitelist(self, map_names):
        for map_name in map_names:
            self.remove_map_from_vm_whitelist(map_name)

    def reset_map_vm_whitelist(self):
        self.set_map_vm_whitelist(self.rcon.get_maps())

    def set_map_vm_whitelist(self, map_names) -> None:
        self.red.set(self.whitelist_key, pickle.dumps(set(map_names)))

    def gen_selection(self):
        config = VoteMapUserConfig.load_from_db()

        logger.debug(
            f"""Generating new map selection for vote map with the following criteria:
            {self.rcon.get_maps()}
            {config}
        """
        )
        selection = suggest_next_maps(
            maps_history=MapsHistory(),
            current_map=self.get_current_map(),
            whitelist_maps=self.get_map_whitelist(),
            num_warfare=config.num_warfare_options,
            num_offensive=config.num_offensive_options,
            num_skirmish_control=config.num_skirmish_control_options,
            exclude_last_n=config.number_last_played_to_exclude,
            consider_offensive_as_same_map=config.consider_offensive_same_map,
            consider_skirmishes_as_same_map=config.consider_skirmishes_as_same_map,
            allow_consecutive_offensive=config.allow_consecutive_offensives,
            allow_consecutive_offensives_of_opposite_side=config.allow_consecutive_offensives_opposite_sides,
        )

        self.set_selection(selection=selection)
        logger.info("Saved new selection: %s", selection)

    def _get_selection(self) -> list[str]:
        """Return the current map suggestions"""
        return [v.decode() for v in self.red.lrange("MAP_SELECTION", 0, -1)]  # type: ignore

    def get_selection(self) -> list[maps.Layer]:
        return sort_maps_by_gamemode(
            [maps.parse_layer(name) for name in self._get_selection()]
        )

    def set_selection(self, selection: Iterable[maps.Layer]) -> None:
        self.red.delete("MAP_SELECTION")
        self.red.lpush("MAP_SELECTION", *[str(map_) for map_ in selection])

    def pick_least_played_map(self, maps):
        maps_history = MapsHistory()

        if not maps:
            raise ValueError("Can't pick a default. No maps to pick from")

        history = [obj["name"] for obj in maps_history]
        index = 0
        for name in maps:
            try:
                idx = history.index(name)
            except ValueError:
                return name
            index = max(idx, index)

        return history[index]

    def pick_default_next_map(self):
        selection = self.get_selection()
        maps_history = MapsHistory()
        config = VoteMapUserConfig.load_from_db()
        all_maps = [maps.parse_layer(m) for m in self.rcon.get_maps()]

        if not config.allow_default_to_offensive:
            logger.debug(
                "Not allowing default to offensive, removing all offensive maps"
            )
            selection = [m for m in selection if m.gamemode != maps.Gamemode.OFFENSIVE]
            all_maps = [m for m in all_maps if m.gamemode != maps.Gamemode.OFFENSIVE]

        if not config.allow_default_to_skirmish:
            logger.debug("Not allowing default to skirmish, removing all skirmish maps")
            selection = [m for m in selection if not m.gamemode.is_small()]
            all_maps = [m for m in all_maps if not m.gamemode.is_small()]

        if not maps_history:
            choice = random.choice([m for m in self.get_map_whitelist()])
            return choice

        return {
            DefaultMethods.least_played_suggestions: partial(
                self.pick_least_played_map, selection
            ),
            DefaultMethods.least_played_all_maps: partial(
                self.pick_least_played_map, all_maps
            ),
            DefaultMethods.random_all_maps: lambda: random.choice(
                list(set(all_maps) - set([maps.parse_layer(maps_history[0]["name"])]))
            ),
            DefaultMethods.random_suggestions: lambda: random.choice(
                list(set(selection) - set([maps.parse_layer(maps_history[0]["name"])]))
            ),
        }[config.default_method]()

    def apply_results(self):
        config = VoteMapUserConfig.load_from_db()
        if not config.enabled:
            return True

        votes = self.get_votes()
        first = Counter(votes.values()).most_common(1)
        if not first:
            next_map = self.pick_default_next_map()
            logger.warning(
                "No votes recorded, defaulting with %s using default winning map %s",
                config.default_method.value,
                next_map,
            )
        else:
            logger.info(f"{votes=}")
            next_map = first[0][0]
            if next_map not in self.rcon.get_maps():
                logger.error(
                    f"{next_map=} is not part of the all map list maps={self.rcon.get_maps()}"
                )
            if next_map not in (selection := self.get_selection()):
                logger.error(f"{next_map=} is not part of vote selection {selection=}")
            logger.info(f"Winning map {next_map=}")

        rcon = get_rcon()
        # Apply rotation safely

        current_rotation = rcon.get_map_rotation()

        while len(current_rotation) > 1:
            # Make sure only 1 map is in rotation
            map_ = current_rotation.pop(1)
            rcon.remove_map_from_rotation(map_.id)

        current_next_map = current_rotation[0]
        if current_next_map != next_map:
            # Replace the only map left in rotation
            rcon.add_map_to_rotation(str(next_map))
            rcon.remove_map_from_rotation(current_next_map.id)

        # Check that it worked
        current_rotation = rcon.get_map_rotation()
        if len(current_rotation) != 1 or current_rotation[0] != next_map:
            raise ValueError(
                f"Applying the winning map {next_map=} failed: {current_rotation=}"
            )

        logger.info(
            f"Successfully applied winning mapp {next_map=}, new rotation {current_rotation=}"
        )
        return True

    def apply_with_retry(self, nb_retry=2):
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

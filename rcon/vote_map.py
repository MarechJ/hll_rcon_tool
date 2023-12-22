import logging
import pickle
import random
import re
from datetime import datetime, timedelta
from functools import partial
from typing import Counter

import redis
from sqlalchemy import and_

from rcon.cache_utils import get_redis_client, get_redis_pool
from rcon.models import PlayerOptins, PlayerSteamID, enter_session
from rcon.player_history import get_player
from rcon.rcon import CommandFailedError, Rcon, StructuredLogLineType
from rcon.settings import SERVER_INFO
from rcon.user_config.vote_map import DefaultMethods, VoteMapUserConfig
from rcon.utils import (
    ALL_MAPS,
    LONG_HUMAN_MAP_NAMES,
    NO_MOD_LONG_HUMAN_MAP_NAMES,
    NO_MOD_SHORT_HUMAN_MAP_NAMES,
    SHORT_HUMAN_MAP_NAMES,
    MapsHistory,
    categorize_maps,
    get_map_side,
    map_name,
    numbered_maps,
)

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


def _get_random_map_selection(maps, nb_to_return, history=None):
    # if history:
    # Calculate weights to stir selection towards least played maps
    try:
        if nb_to_return > 0 and len(maps) < nb_to_return:
            nb_to_return = len(maps)
        return random.sample(maps, k=nb_to_return)
    except (IndexError, ValueError):
        return []


def suggest_next_maps(
    maps_history,
    whitelist_maps,
    selection_size=6,
    exclude_last_n=4,
    offensive_ratio=0.5,
    consider_offensive_as_same_map=True,
    allow_consecutive_offensive=True,
    allow_consecutive_offensives_of_opposite_side=False,
    current_map=None,
):
    try:
        return _suggest_next_maps(
            maps_history,
            whitelist_maps,
            selection_size,
            exclude_last_n,
            offensive_ratio,
            consider_offensive_as_same_map,
            allow_consecutive_offensive,
            allow_consecutive_offensives_of_opposite_side,
            current_map,
        )
    except RestrictiveFilterError:
        logger.warning("Falling back on ALL_MAPS since the filters are too restrictive")
        return _suggest_next_maps(
            maps_history,
            set(ALL_MAPS),
            selection_size,
            exclude_last_n,
            offensive_ratio,
            consider_offensive_as_same_map,
            allow_consecutive_offensive,
            allow_consecutive_offensives_of_opposite_side,
            current_map,
        )


def _suggest_next_maps(
    maps_history,
    allowed_maps,
    selection_size,
    exclude_last_n,
    offsensive_ratio,
    consider_offensive_as_same_map,
    allow_consecutive_offensive,
    allow_consecutive_offensives_of_opposite_side,
    current_map,
):
    if exclude_last_n > 0:
        last_n_map = set(m["name"] for m in maps_history[:exclude_last_n])
    else:
        last_n_map = set()
    logger.info("Excluding last %s player maps: %s", exclude_last_n, last_n_map)
    remaining_maps = allowed_maps - last_n_map
    logger.info("Remaining maps to suggest from: %s", remaining_maps)

    try:
        current_map = current_map or maps_history[0]["name"]
    except (IndexError, KeyError):
        logger.exception("Unable to get current map for generating selection")
        raise

    current_side = get_map_side(current_map)

    if consider_offensive_as_same_map:
        last_names = set(map_name(m) for m in last_n_map)
        logger.info("Considering offensive mode as same map, excluding %s", last_names)
        remaining_maps = set(m for m in remaining_maps if not map_name(m) in last_names)
        logger.info("Remaining maps to suggest from: %s", remaining_maps)

    if not allow_consecutive_offensives_of_opposite_side and current_side:
        opposite_side = ["us", "rus"] if current_side == "ger" else ["ger"]
        logger.info(
            "Not allowing consecutive offensive with opposite side: %s", opposite_side
        )
        remaining_maps = [
            m for m in remaining_maps if get_map_side(m) not in opposite_side
        ]
        logger.info("Remaining maps to suggest from: %s", remaining_maps)

    # Handle case if all maps got excluded
    categorized_maps = categorize_maps(remaining_maps)
    if offsensive_ratio == 0:
        nb_offensive = 0
    else:
        nb_offensive = round(offsensive_ratio * selection_size)
    warfares = []

    offensives = _get_random_map_selection(categorized_maps["offensive"], nb_offensive)

    if not allow_consecutive_offensive and "offensive" in current_map:
        logger.info(
            "Current map %s is offensive. Excluding all offsensives from suggestions",
            current_map,
        )
        offensives = []

    warfares = _get_random_map_selection(
        categorized_maps["warfare"], selection_size - len(offensives)
    )
    selection = offensives + warfares

    if not selection:
        logger.error("No maps can be suggested with the given parameters.")
        raise RestrictiveFilterError("Unable to suggest map")
    logger.info("Suggestion %s", selection)
    return selection


# TODO:  Handle empty selection (None)
class VoteMap:
    def __init__(self) -> None:
        self.red = get_redis_client()
        self.reminder_time_key = "last_vote_reminder"
        self.optin_name = "votemap_reminder"
        self.whitelist_key = "votemap_whitelist"

    def join_vote_options(
        self, join_char, selection, human_name_map, maps_to_numbers, votes, total_votes
    ):
        return join_char.join(
            f"[{maps_to_numbers[m]}] {human_name_map[m]} - {votes[m]}/{total_votes} votes"
            for m in selection
        )

    def format_map_vote(self, format_type="vertical", short_names=True):
        selection = self.get_selection()
        if not selection:
            logger.warning("No vote map selection")
            return ""

        votes = self.get_votes()
        total_votes = len(votes)
        votes = Counter(votes.values())
        human_map = SHORT_HUMAN_MAP_NAMES if short_names else LONG_HUMAN_MAP_NAMES
        human_map_mod = (
            NO_MOD_SHORT_HUMAN_MAP_NAMES if short_names else NO_MOD_LONG_HUMAN_MAP_NAMES
        )
        vote_dict = numbered_maps(selection)
        maps_to_numbers = dict(zip(vote_dict.values(), vote_dict.keys()))
        items = [
            f"[{k}] {human_map.get(v, v)} - {votes[v]}/{total_votes} votes"
            for k, v in vote_dict.items()
        ]

        if format_type == "vertical":
            return "\n".join(items)
        if format_type.startswith("by_mod"):
            categorized = categorize_maps(selection)

            off = self.join_vote_options(
                "  ",
                categorized["offensive"],
                human_map_mod,
                maps_to_numbers,
                votes,
                total_votes,
            )
            warfare = self.join_vote_options(
                "  ",
                categorized["warfare"],
                human_map_mod,
                maps_to_numbers,
                votes,
                total_votes,
            )

            vote_string = ""
            if categorized["warfare"]:
                vote_string = "WARFARES:\n{}".format(
                    self.join_vote_options(
                        "\n",
                        categorized["warfare"],
                        human_map_mod,
                        maps_to_numbers,
                        votes,
                        total_votes,
                    )
                )
            if categorized["offensive"]:
                if vote_string:
                    vote_string += "\n\n"
                vote_string = "{}OFFENSIVES:\n{}".format(
                    vote_string,
                    self.join_vote_options(
                        "\n",
                        categorized["offensive"],
                        human_map_mod,
                        maps_to_numbers,
                        votes,
                        total_votes,
                    ),
                )

            return vote_string

    def get_last_reminder_time(self):
        res = self.red.get(self.reminder_time_key)
        if res is not None:
            res = pickle.loads(res)
        return res

    def set_last_reminder_time(self, the_time: datetime = None):
        dt = the_time or datetime.now()
        self.red.set(self.reminder_time_key, pickle.dumps(dt))

    def reset_last_reminder_time(self):
        self.red.delete(self.reminder_time_key)

    def is_time_for_reminder(self):
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
                rcon.do_message_player(
                    steam_id_64=steamid,
                    message=vote_map_message.format(
                        map_selection=self.format_map_vote("by_mod_vertical_all")
                    ),
                )
            except CommandFailedError:
                logger.warning("Unable to message %s", name)

    def handle_vote_command(self, rcon, struct_log: StructuredLogLineType) -> bool:
        message = struct_log.get("sub_content", "").strip()
        config = VoteMapUserConfig.load_from_db()
        if not message.lower().startswith(("!votemap", "!vm")):
            return config.enabled

        steam_id_64_1 = struct_log["steam_id_64_1"]
        if not config.enabled:
            # rcon.do_message_player(
            #     steam_id_64=steam_id_64_1,
            #     message="Vote map is not enabled on this server",
            # )
            return config.enabled

        if match := re.match(r"(!votemap|!vm)\s*(\d+)", message, re.IGNORECASE):
            logger.info("Registering vote %s", struct_log)
            vote = match.group(2)
            try:
                map_name = self.register_vote(
                    struct_log["player"], struct_log["timestamp_ms"] / 1000, vote
                )
            except InvalidVoteError:
                rcon.do_message_player(
                    steam_id_64=steam_id_64_1, message="Invalid vote."
                )
                if config.help_text:
                    rcon.do_message_player(
                        steam_id_64=steam_id_64_1, message=config.help_text
                    )
            except VoteMapNoInitialised:
                rcon.do_message_player(
                    steam_id_64=steam_id_64_1,
                    message="We can't register you vote at this time.\nVoteMap not initialised",
                )
                raise
            else:
                if msg := config.thank_you_text:
                    msg = msg.format(
                        player_name=struct_log["player"], map_name=map_name
                    )
                    rcon.do_message_player(steam_id_64=steam_id_64_1, message=msg)
            finally:
                self.apply_results()
                return config.enabled

        if (
            re.match(r"(!votemap|!vm)\s*help", message, re.IGNORECASE)
            and config.help_text
        ):
            logger.info("Showing help %s", struct_log)
            rcon.do_message_player(steam_id_64=steam_id_64_1, message=config.help_text)
            return config.enabled

        if re.match(r"(!votemap|!vm)$", message, re.IGNORECASE):
            logger.info("Showing selection %s", struct_log)
            vote_map_message = config.instruction_text
            rcon.do_message_player(
                steam_id_64=steam_id_64_1,
                message=vote_map_message.format(
                    map_selection=self.format_map_vote("by_mod_vertical_all")
                ),
            )
            return config.enabled

        if re.match(r"(!votemap|!vm)\s*never$", message, re.IGNORECASE):
            if not config.allow_opt_out:
                rcon.do_message_player(
                    steam_id_64=steam_id_64_1,
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
                    rcon.do_message_player(
                        steam_id_64=steam_id_64_1, message="VoteMap Unsubscribed OK"
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
                    rcon.do_message_player(
                        steam_id_64=steam_id_64_1, message="VoteMap Subscribed OK"
                    )
                except Exception as e:
                    logger.exception("Unable to update optin. Already exists?")
            return config.enabled

        rcon.do_message_player(steam_id_64=steam_id_64_1, message=config.help_text)
        return config.enabled

    def register_vote(self, player_name, vote_timestamp, vote_content):
        try:
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

        if vote_timestamp < min_time:
            logger.warning(
                f"Vote is too old {player_name=}, {vote_timestamp=}, {vote_content=}, {current_map=}"
            )

        selection = self.get_selection()

        try:
            vote_idx = int(vote_content)
            selected_map = selection[vote_idx]
            self.red.hset("VOTES", player_name, selected_map)
        except (TypeError, ValueError, IndexError):
            raise InvalidVoteError(
                f"Vote must be a number between 0 and {len(selection) - 1}"
            )

        logger.info(
            f"Registered vote from {player_name=} for {selected_map=} - {vote_content=}"
        )
        return selected_map

    def get_vote_overview(self):
        try:
            votes = self.get_votes()
            maps = Counter(votes.values()).most_common()
            return {"total_votes": len(votes), "winning_maps": maps}
        except Exception:
            logger.exception("Can't produce vote overview")

    def clear_votes(self):
        self.red.delete("VOTES")

    def has_voted(self, player_name):
        return self.red.hget("VOTES", player_name) is not None

    def get_votes(self):
        votes = self.red.hgetall("VOTES") or {}
        return {k.decode(): v.decode() for k, v in votes.items()}

    def get_current_map(self):
        map_ = Rcon(SERVER_INFO).get_map()
        if map_.endswith("_RESTART"):
            map_ = map_.replace("_RESTART", "")

        if map_ not in ALL_MAPS:
            raise ValueError("Invalid current map %s", map_)

        return map_

    def get_map_whitelist(self):
        res = self.red.get(self.whitelist_key)
        if res is not None:
            return pickle.loads(res)
        return set(ALL_MAPS)

    def do_add_map_to_whitelist(self, map_name):
        whitelist = self.get_map_whitelist()
        whitelist.add(map_name)
        self.do_set_map_whitelist(whitelist)

    def do_add_maps_to_whitelist(self, map_names):
        for map_name in map_names:
            self.do_add_map_to_whitelist(map_name)

    def do_remove_map_from_whitelist(self, map_name):
        whitelist = self.get_map_whitelist()
        whitelist.discard(map_name)
        self.do_set_map_whitelist(whitelist)

    def do_remove_maps_from_whitelist(self, map_names):
        for map_name in map_names:
            self.do_remove_map_from_whitelist(map_name)

    def do_reset_map_whitelist(self):
        self.do_set_map_whitelist(ALL_MAPS)

    def do_set_map_whitelist(self, map_names):
        self.red.set(self.whitelist_key, pickle.dumps(set(map_names)))

    def gen_selection(self):
        config = VoteMapUserConfig.load_from_db()

        logger.debug(
            f"""Generating new map selection for vote map with the following criteria:
            {ALL_MAPS}
            {config.number_of_options=}
            {config.ratio_of_offensives=}
            {config.number_last_played_to_exclude=}
            {config.consider_offensive_same_map=}
            {config.allow_consecutive_offensives=}
            {config.allow_consecutive_offensives_opposite_sides=}
            {config.default_method.value=}
        """
        )
        selection = suggest_next_maps(
            MapsHistory(),
            self.get_map_whitelist(),
            selection_size=config.number_of_options,
            exclude_last_n=config.number_last_played_to_exclude,
            offensive_ratio=config.ratio_of_offensives,
            consider_offensive_as_same_map=config.consider_offensive_same_map,
            allow_consecutive_offensive=config.allow_consecutive_offensives,
            allow_consecutive_offensives_of_opposite_side=config.allow_consecutive_offensives_opposite_sides,
            current_map=self.get_current_map(),
        )
        self.red.delete("MAP_SELECTION")
        self.red.lpush("MAP_SELECTION", *selection)
        logger.info("Saved new selection: %s", selection)

    def get_selection(self):
        return [v.decode() for v in self.red.lrange("MAP_SELECTION", 0, -1)]

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
        all_maps = ALL_MAPS

        if not config.allow_default_to_offensive:
            logger.debug(
                "Not allowing default to offensive, removing all offensive maps"
            )
            selection = [m for m in selection if not "off" in m]
            all_maps = [m for m in ALL_MAPS if not "off" in m]

        if not maps_history:
            raise ValueError("Map history is empty")

        return {
            DefaultMethods.least_played_suggestions: partial(
                self.pick_least_played_map, selection
            ),
            DefaultMethods.least_played_all_maps: partial(
                self.pick_least_played_map, all_maps
            ),
            DefaultMethods.random_all_maps: lambda: random.choice(
                list(set(all_maps) - set([maps_history[0]["name"]]))
            ),
            DefaultMethods.random_suggestions: lambda: random.choice(
                list(set(selection) - set([maps_history[0]["name"]]))
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
            if next_map not in ALL_MAPS:
                logger.error(f"{next_map=} is not part of the all map list {ALL_MAPS=}")
            if next_map not in (selection := self.get_selection()):
                logger.error(f"{next_map=} is not part of vote selection {selection=}")
            logger.info(f"Winning map {next_map=}")

        rcon = Rcon(SERVER_INFO)
        # Apply rotation safely

        current_rotation = rcon.get_map_rotation()

        while len(current_rotation) > 1:
            # Make sure only 1 map is in rotation
            map_ = current_rotation.pop(1)
            rcon.do_remove_map_from_rotation(map_)

        current_next_map = current_rotation[0]
        if current_next_map != next_map:
            # Replace the only map left in rotation
            rcon.do_add_map_to_rotation(next_map)
            rcon.do_remove_map_from_rotation(current_next_map)

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

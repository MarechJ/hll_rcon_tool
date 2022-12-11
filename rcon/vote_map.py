import enum
import logging
import os
import random
import re
import time
from datetime import datetime, timedelta
from functools import partial
from threading import Thread
from typing import Counter
import pickle
import redis
from sqlalchemy import and_

from rcon.cache_utils import get_redis_client, get_redis_pool
from rcon.discord import dict_to_discord, send_to_discord_audit
from rcon.extended_commands import CommandFailedError, StructuredLogLine
from rcon.models import PlayerOptins, PlayerSteamID, enter_session
from rcon.player_history import get_player
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.user_config import DefaultMethods, VoteMapConfig
from rcon.utils import (
    ALL_MAPS,
    FixedLenList,
    MapsHistory,
    categorize_maps,
    get_map_side,
    map_name,
    numbered_maps,
)
from rcon.workers import (
    record_stats,
    record_stats_worker,
    temp_welcome_standalone,
    temporary_welcome,
    temporary_welcome_in,
)
from rcon.utils import (
    LONG_HUMAN_MAP_NAMES,
    NO_MOD_LONG_HUMAN_MAP_NAMES,
    NO_MOD_SHORT_HUMAN_MAP_NAMES,
    SHORT_HUMAN_MAP_NAMES,
    categorize_maps,
    numbered_maps,
)

logger = logging.getLogger(__name__)

####################
#
#  See hooks.py for the actual initialization of the vote map
#
#
####################


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
    all_maps,
    selection_size=6,
    exclude_last_n=4,
    offsensive_ratio=0.5,
    consider_offensive_as_same_map=True,
    allow_consecutive_offensive=True,
    allow_consecutive_offensives_of_opposite_side=False,
    current_map=None,
):
    if exclude_last_n > 0:
        last_n_map = set(m["name"] for m in maps_history[:exclude_last_n])
    else:
        last_n_map = set()
    logger.info("Excluding last %s player maps: %s", exclude_last_n, last_n_map)
    remaining_maps = set(all_maps) - last_n_map
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
        raise ValueError("Unable to suggest map")
    logger.info("Suggestion %s", selection)
    return selection


class InvalidVoteError(Exception):
    pass


class VoteMapNoInitialised(Exception):
    pass


# TODO:  Handle empty selection (None)
class VoteMap:
    def __init__(self) -> None:
        self.red = get_redis_client()
        self.reminder_time_key = "last_vote_reminder"
        self.optin_name = "votemap_reminder"

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
        reminder_freq_min = VoteMapConfig().get_votemap_reminder_frequency_minutes()
        if reminder_freq_min == 0:
            return False

        last_time = self.get_last_reminder_time()

        if last_time is None:
            logger.warning("No time for last vote reminder")
            return True

        if (datetime.now() - last_time).total_seconds() > reminder_freq_min * 60:
            return True

        return False

    def vote_map_reminder(self, rcon: RecordedRcon, force=False):
        logger.info("Vote MAP reminder")
        vote_map_config = VoteMapConfig()
        vote_map_message = vote_map_config.get_votemap_instruction_text()

        if not vote_map_config.get_vote_enabled():
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
            if self.has_voted(name) or (
                steamid in opted_out and vote_map_config.get_votemap_allow_optout()
            ):
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

    def handle_vote_command(self, rcon, struct_log: StructuredLogLine):
        message = struct_log.get("sub_content", "").strip()
        if not message.startswith("!votemap"):
            return

        steam_id_64_1 = struct_log["steam_id_64_1"]
        config = VoteMapConfig()
        if not config.get_vote_enabled():
            rcon.do_message_player(
                steam_id_64=steam_id_64_1,
                message="Vote map is not enabled on thi server",
            )
            return

        help_text = config.get_votemap_help_text()

        if match := re.match(r"!votemap\s*(\d+)", message):
            logger.info("Registering vote %s", struct_log)
            vote = match.group(1)
            try:
                map_name = self.register_vote(
                    struct_log["player"], struct_log["timestamp_ms"] / 1000, vote
                )
            except InvalidVoteError:
                rcon.do_message_player(
                    steam_id_64=steam_id_64_1, message="Invalid vote."
                )
                if help_text:
                    rcon.do_message_player(steam_id_64=steam_id_64_1, message=help_text)
            except VoteMapNoInitialised:
                rcon.do_message_player(
                    steam_id_64=steam_id_64_1,
                    message="We can't register you vote at this time.\nVoteMap not initialised",
                )
                raise
            else:
                if msg := config.get_votemap_thank_you_text():
                    msg = msg.format(
                        player_name=struct_log["player"], map_name=map_name
                    )
                    rcon.do_message_player(steam_id_64=steam_id_64_1, message=msg)
            finally:
                self.apply_results()
                return

        if re.match(r"!votemap\s*help", message) and help_text:
            logger.info("Showing help %s", struct_log)
            rcon.do_message_player(steam_id_64=steam_id_64_1, message=help_text)
            return

        if re.match(r"!votemap$", message):
            logger.info("Showing selection %s", struct_log)
            vote_map_message = config.get_votemap_instruction_text()
            rcon.do_message_player(
                steam_id_64=steam_id_64_1,
                message=vote_map_message.format(
                    map_selection=self.format_map_vote("by_mod_vertical_all")
                ),
            )
            return

        if re.match(r"!votemap\s*never$", message):
            if not config.get_votemap_allow_optout():
                rcon.do_message_player(
                    steam_id_64=steam_id_64_1,
                    message="You can't opt-out of vote map on this server",
                )
                return

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

            return

        if re.match(r"!votemap\s*allow$", message):
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
            return

        rcon.do_message_player(steam_id_64=steam_id_64_1, message=help_text)
        return

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
        map_ = RecordedRcon(SERVER_INFO).get_map()
        if map_.endswith("_RESTART"):
            map_ = map_.replace("_RESTART", "")

        if map_ not in ALL_MAPS:
            raise ValueError("Invalid current map %s map_")

        return map_

    def gen_selection(self):
        config = VoteMapConfig()

        logger.debug(
            f"""Generating new map selection for vote map with the following criteria:
            {ALL_MAPS}
            {config.get_votemap_number_of_options()=} 
            {config.get_votemap_ratio_of_offensives_to_offer()=} 
            {config.get_votemap_number_of_last_played_map_to_exclude()=} 
            {config.get_votemap_consider_offensive_as_same_map()=} 
            {config.get_votemap_allow_consecutive_offensives()=} 
            {config.get_votemap_allow_consecutive_offensives_of_opposite_side()=} 
            {config.get_votemap_default_method()=}
        """
        )
        selection = suggest_next_maps(
            MapsHistory(),
            ALL_MAPS,
            selection_size=config.get_votemap_number_of_options(),
            exclude_last_n=config.get_votemap_number_of_last_played_map_to_exclude(),
            offsensive_ratio=config.get_votemap_ratio_of_offensives_to_offer(),
            consider_offensive_as_same_map=config.get_votemap_consider_offensive_as_same_map(),
            allow_consecutive_offensive=config.get_votemap_allow_consecutive_offensives(),
            allow_consecutive_offensives_of_opposite_side=config.get_votemap_allow_consecutive_offensives_of_opposite_side(),
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
        config = VoteMapConfig()
        all_maps = ALL_MAPS

        if not config.get_votemap_allow_default_to_offsensive():
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
        }[config.get_votemap_default_method()]()

    def apply_results(self):
        config = VoteMapConfig()
        votes = self.get_votes()
        first = Counter(votes.values()).most_common(1)
        if not first:
            next_map = self.pick_default_next_map()
            logger.warning(
                "No votes recorded, defaulting with %s using default winning map %s",
                config.get_votemap_default_method(),
                next_map,
            )
        else:
            logger.info(f"{votes=}")
            next_map = first[0][0]
            if next_map not in ALL_MAPS:
                raise ValueError(
                    f"{next_map=} is not part of the all map list {ALL_MAPS=}"
                )
            if next_map not in (selection := self.get_selection()):
                raise ValueError(
                    f"{next_map=} is not part of vote selection {selection=}"
                )
            logger.info(f"Winning map {next_map=}")

        # Sanity checks below
        rcon = RecordedRcon(SERVER_INFO)
        current_map = rcon.get_map()
        if current_map.replace("_RESTART", "") not in ALL_MAPS:
            raise ValueError(
                f"{current_map=} is not part of the all map list {ALL_MAPS=}"
            )

        try:
            history_current_map = MapsHistory()[0]["name"]
        except (IndexError, KeyError):
            raise ValueError("History is empty")

        if current_map != history_current_map:
            raise ValueError(
                f"{current_map=} does not match history map {history_current_map=}"
            )

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
            logger.warning("Falling back to adding all maps to the rotation")
            RecordedRcon(SERVER_INFO).set_maprotation(ALL_MAPS)


# DEPRECATED see hooks.py
def on_map_change(old_map: str, new_map: str):
    logger.info("Running on_map_change hooks with %s %s", old_map, new_map)
    # try:
    #     config = VoteMapConfig()

    #     if config.get_vote_enabled():
    #         votemap = VoteMap()
    #         votemap.gen_selection()
    #         votemap.clear_votes()
    #         votemap.apply_with_retry(nb_retry=4)
    #         # temporary_welcome_in(
    #         #    "%s{votenextmap_vertical}" % config.get_votemap_instruction_text(),
    #         #    seconds=60 * 20,
    #         #    restore_after_seconds=60 * 5,
    #         # )
    # except Exception:
    #     logger.exception("Unexpected error while running vote map")
    #try:
    #    record_stats_worker(MapsHistory()[1])
    #except Exception:
    #    logger.exception("Unexpected error while running stats worker")


# DEPRECATED see hooks.py
class MapsRecorder:
    def __init__(self, rcon: RecordedRcon):
        self.rcon = rcon
        self.red = redis.Redis(connection_pool=get_redis_pool())
        self.maps_history = MapsHistory()
        self.prev_map = None
        self._restore_state()

    def _restore_state(self):
        current_map = self.rcon.get_map()
        self.prev_map = current_map

        try:
            last = self.maps_history[0]
        except IndexError:
            logger.warning("Map history is empty, can't restore state")
            return

        started_time = datetime.fromtimestamp(last.get("start"))
        elapsed_time = datetime.now() - started_time

        if last.get("name") == current_map.replace(
            "_RESTART", ""
        ) and elapsed_time < timedelta(minutes=90):
            logging.info("State recovered successfully")
        else:
            logging.warning(
                "The map recorder was offline for too long, the maps history will have gaps"
            )

    def detect_map_change(self):
        try:
            current_map = self.rcon.get_map()
        except Exception:
            logger.info("Faied to get current map. Skipping")
            return

        logger.debug(
            "Checking for map change current: %s prev: %s", current_map, self.prev_map
        )
        if self.prev_map != current_map:
            if (
                self.prev_map
                and self.prev_map.replace("_RESTART", "") in ALL_MAPS
                and current_map
                and current_map.replace("_RESTART", "") in ALL_MAPS
            ):
                self.maps_history.save_map_end(self.prev_map)
            if current_map and current_map.replace("_RESTART", "") in ALL_MAPS:
                self.maps_history.save_new_map(current_map)
                logger.info(
                    "Map change detected updating state. Prev map %s New Map %s",
                    self.prev_map,
                    current_map,
                )
                if not os.getenv("SILENT_MAP_RECORDER", None):
                    send_to_discord_audit(
                        f"map change detected {dict_to_discord(dict(previous=self.prev_map, new=current_map))}",
                        by="MAP_RECORDER",
                        silent=False,
                    )
                on_map_change(self.prev_map, current_map)
                self.prev_map = current_map

            return True

        return False

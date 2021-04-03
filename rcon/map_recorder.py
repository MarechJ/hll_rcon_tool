from functools import partial
from typing import Counter
from rcon.settings import SERVER_INFO
import time
from datetime import datetime, timedelta
import logging
from threading import Thread
import os
import redis
import re
from rcon.discord import send_to_discord_audit, dict_to_discord
from rcon.recorded_commands import RecordedRcon
from rcon.extended_commands import CommandFailedError
from rcon.utils import (
    categorize_maps,
    numbered_maps,
    FixedLenList,
    map_name,
    get_map_side,
    MapsHistory,
    ALL_MAPS,
)
from rcon.user_config import VoteMapConfig, DefaultMethods
from rcon.cache_utils import get_redis_client, get_redis_pool
import enum
import random

logger = logging.getLogger(__name__)


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
    last_n_map = set(m["name"] for m in maps_history[:exclude_last_n])
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
        opposite_side = "us" if current_side == "ger" else "ger"
        logger.info(
            "Not allowing consecutive offensive with opposite side: %s", opposite_side
        )
        remaining_maps = [m for m in remaining_maps if get_map_side(m) != opposite_side]
        logger.info("Remaining maps to suggest from: %s", remaining_maps)

    # Handle case if all maps got excluded
    categorized_maps = categorize_maps(remaining_maps)
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


# TODO:  Handle empty selection (None)
class VoteMap:
    def __init__(self) -> None:
        self.red = get_redis_client()

    def is_vote(self, message):
        match = re.match("(\d)", message)
        if not match:
            match = re.match("!votemap\s*(.*)", message)
        if not match:
            return False
        if not match.groups():
            raise InvalidVoteError("You must specify the number of the map")

        return match.groups()[0]

    def register_vote(self, player_name, vote_timestamp, vote_content):
        try:
            current_map = MapsHistory()[0]
            min_time = current_map["start"]
        except IndexError:
            logger.error("Map history is empty - Can't register vote")
            raise
        except KeyError:
            logger.error("Map history is corrupted - Can't register vote")
            raise

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
            selection = [m for m in selection if not "offensive" in m]
            all_maps = [m for m in ALL_MAPS if not "offensive" in m]

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
                raise ValueError(f"{next_map=} is not part of vote select {selection=}")
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
        try:
            current_map_idx = current_rotation.index(
                current_map.replace("_RESTART", "")
            )
        except ValueError:
            logger.warning(
                f"{current_map=} is not in {current_rotation=} will try to add"
            )
            rcon.do_add_map_to_rotation(current_map.replace("_RESTART", ""))

        current_rotation = rcon.get_map_rotation()
        try:
            current_map_idx = current_rotation.index(
                current_map.replace("_RESTART", "")
            )
        except ValueError as e:
            raise ValueError(
                f"{current_map=} is not in {current_rotation=} addint it failed"
            ) from e

        try:
            next_map_idx = current_rotation.index(next_map)
        except ValueError:
            logger.info(f"{next_map=} no in rotation, adding it {current_rotation=}")
            rcon.do_add_map_to_rotation(next_map)
        else:
            if next_map_idx < current_map_idx:
                logger.info(
                    f"{next_map=} is before {current_map=} removing and re-adding"
                )
                rcon.do_remove_map_from_rotation(next_map)
                rcon.do_add_map_to_rotation(next_map)

        current_rotation = rcon.get_map_rotation()

        try:
            next_map_idx = current_rotation.index(next_map)
            if next_map_idx < current_map_idx:
                raise ValueError(f"{next_map=} is still before {current_map=}")
        except ValueError as e:
            raise ValueError(f"{next_map=} failed to be added to {current_rotation=}")

        maps_to_remove = current_rotation[current_map_idx + 1 : next_map_idx]
        logger.debug(f"{current_map=} {current_rotation=} - {maps_to_remove=}")

        for map in maps_to_remove:
            # Remove the maps that are in between the current map and the desired next map
            rcon.do_remove_map_from_rotation(map)

        for map in maps_to_remove:
            rcon.do_add_map_to_rotation(map)

        # Check that it worked
        current_rotation = rcon.get_map_rotation()
        if (
            not current_rotation[current_map_idx] == current_map
            and current_rotation[current_map_idx + 1] == next_map
        ):
            raise ValueError(
                f"Applying the winning map {next_map=} after the {current_map=} failed: {current_rotation=}"
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


def on_map_change(old_map_info, new_map_info):
    if VoteMapConfig().get_vote_enabled():
        votemap = VoteMap()
        votemap.gen_selection()
        votemap.clear_votes()
        votemap.apply_with_retry()


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


if __name__ == "__main__":
    run()

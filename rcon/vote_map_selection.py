import logging
import random
from dataclasses import dataclass

from rcon import maps
from rcon.maps import (
    GameMode,
    Layer,
    categorize_maps,
    get_all_layers_by_map,
)

logger = logging.getLogger(__name__)


class RestrictiveFilterError(Exception):
    pass


@dataclass(frozen=True)
class MapSelectionCriteria:
    """User-configured rules and context used to build a votemap selection."""

    maps_history: list[Layer]
    current_map: Layer
    allowed_maps: set[Layer]
    number_last_played_to_exclude: int
    num_warfare_options: int
    num_offensive_options: int
    num_skirmish_control_options: int
    consider_offensive_same_map: bool
    consider_skirmishes_as_same_map: bool
    consider_environment_as_same_map: bool
    allow_multiple_maps_with_same_environment: bool
    allow_consecutive_offensives: bool
    allow_consecutive_offensives_opposite_sides: bool
    allow_consecutive_skirmishes: bool


class MapSelectionBuilder:
    """Builds a randomized votemap selection by filtering and sampling map layers."""

    def build(self, criteria: MapSelectionCriteria) -> list[Layer]:
        """Return a filtered, randomized map list for players to vote on."""
        candidates = self._build_candidates(criteria)
        selection = self._sample_selection(candidates, criteria)

        if not selection:
            logger.error("No maps can be suggested with the given parameters.")
            raise RestrictiveFilterError("Unable to suggest map")

        logger.info("Suggestion %s", [m.pretty_name for m in selection])
        return selection

    def _log_candidates(self, step: str, candidates: set[Layer]) -> None:
        """Log the candidate pool remaining after a filter step."""
        logger.info(
            "%s - remaining maps to suggest from: %s",
            step,
            [m.pretty_name for m in candidates],
        )

    def _history_exclusions(self, criteria: MapSelectionCriteria) -> set[Layer]:
        """Return layers excluded because they were played too recently."""
        if criteria.number_last_played_to_exclude <= 0:
            return set()

        last_n_maps = criteria.maps_history[: criteria.number_last_played_to_exclude]
        if criteria.consider_environment_as_same_map:
            excluded = {
                variant
                for layer in last_n_maps
                for variant in get_all_layers_by_map(
                    layer.map, layer.game_mode, layer.attackers
                )
            }
        else:
            excluded = set(last_n_maps)

        logger.info(
            "Excluding last %s played maps: %s",
            criteria.number_last_played_to_exclude,
            [m.pretty_name for m in excluded],
        )
        return excluded

    def _exclude_same_map_variants(
        self,
        candidates: set[Layer],
        history_excluded: set[Layer],
        criteria: MapSelectionCriteria,
    ) -> set[Layer]:
        """Remove all modes on a map when offensive/skirmish should count as the same map."""
        if not (
            criteria.consider_offensive_same_map
            or criteria.consider_skirmishes_as_same_map
        ):
            return candidates

        excluded_map_ids = {layer.map for layer in history_excluded}
        logger.info(
            "Considering offensive/skirmish mode as same map, excluding %s",
            excluded_map_ids,
        )
        return {layer for layer in candidates if layer.map not in excluded_map_ids}

    def _exclude_consecutive_mode_maps(
        self, candidates: set[Layer], criteria: MapSelectionCriteria
    ) -> set[Layer]:
        """Remove offensive or skirmish layers when the current map disallows back-to-back modes."""
        current_map = criteria.current_map

        if (
            not criteria.allow_consecutive_offensives
            and current_map.game_mode == GameMode.OFFENSIVE
        ):
            logger.info(
                "Current map %s is offensive. Excluding all offensives from suggestions",
                current_map,
            )
            candidates = {
                layer for layer in candidates if layer.game_mode != GameMode.OFFENSIVE
            }

        if not criteria.allow_consecutive_skirmishes and current_map.game_mode in (
            GameMode.SKIRMISH,
            GameMode.PHASED,
            GameMode.MAJORITY,
        ):
            logger.info(
                "Current map %s is skirmish. Excluding all skirmishes from suggestions",
                current_map,
            )
            candidates = {
                layer for layer in candidates if layer.game_mode != GameMode.SKIRMISH
            }

        return candidates

    def _exclude_opposite_side_offensives(
        self, candidates: set[Layer], criteria: MapSelectionCriteria
    ) -> set[Layer]:
        """Remove offensives that would make the same team defend twice in a row."""
        current_map = criteria.current_map
        if (
            criteria.allow_consecutive_offensives_opposite_sides
            or current_map.game_mode != GameMode.OFFENSIVE
        ):
            return candidates

        if current_map.attackers:
            logger.info(
                "Not allowing consecutive offensive with opposite side: %s",
                maps.get_opposite_side(current_map.attackers),
            )
        return {
            layer
            for layer in candidates
            if layer.opposite_side != current_map.attackers
        }

    def _build_candidates(self, criteria: MapSelectionCriteria) -> set[Layer]:
        """Apply all exclusion rules to the whitelist and return the remaining candidates."""
        history_excluded = self._history_exclusions(criteria)
        candidates = criteria.allowed_maps - history_excluded
        self._log_candidates("After excluding recently played maps", candidates)

        candidates = self._exclude_same_map_variants(
            candidates, history_excluded, criteria
        )
        self._log_candidates("After excluding same-map variants", candidates)

        candidates = self._exclude_consecutive_mode_maps(candidates, criteria)
        self._log_candidates("After excluding consecutive mode maps", candidates)

        candidates = self._exclude_opposite_side_offensives(candidates, criteria)
        self._log_candidates("After excluding opposite-side offensives", candidates)

        return candidates

    def _get_random_map_selection(
        self,
        maps_pool: list[Layer],
        nb_to_return: int,
        allow_multiple_maps_with_same_environment: bool,
    ) -> list[Layer]:
        """Pick up to `nb_to_return` random layers, optionally limiting to one environment per map/mode/team."""
        try:
            if nb_to_return > 0 and len(maps_pool) < nb_to_return:
                nb_to_return = len(maps_pool)

            if not allow_multiple_maps_with_same_environment:
                selected_maps: list[Layer] = []
                pool = list(maps_pool)
                while len(pool) > 0 and len(selected_maps) < nb_to_return:
                    pick = random.choice(pool)
                    selected_maps.append(pick)
                    pool = [
                        layer
                        for layer in pool
                        if not (
                            layer.map == pick.map
                            and layer.game_mode == pick.game_mode
                            and layer.attackers == pick.attackers
                        )
                    ]
                return selected_maps

            return random.sample(maps_pool, k=nb_to_return)
        except (IndexError, ValueError):
            return []

    def _sample_selection(
        self, candidates: set[Layer], criteria: MapSelectionCriteria
    ) -> list[Layer]:
        """Randomly sample warfare, offensive, and skirmish options from the filtered candidates."""
        categorized_maps = categorize_maps(candidates)
        return (
            self._get_random_map_selection(
                categorized_maps[GameMode.OFFENSIVE],
                criteria.num_offensive_options,
                criteria.allow_multiple_maps_with_same_environment,
            )
            + self._get_random_map_selection(
                categorized_maps[GameMode.WARFARE],
                criteria.num_warfare_options,
                criteria.allow_multiple_maps_with_same_environment,
            )
            + self._get_random_map_selection(
                categorized_maps[GameMode.SKIRMISH],
                criteria.num_skirmish_control_options,
                criteria.allow_multiple_maps_with_same_environment,
            )
        )

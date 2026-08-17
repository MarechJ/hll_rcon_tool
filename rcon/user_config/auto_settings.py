import logging

from rcon.game import get_game_profile
from rcon.types import GameEnum
from rcon.user_config.utils import (
    GameSelector,
    _add_conf,
    _remove_conf,
    _set_default,
    get_user_config_game,
    get_user_config,
    set_user_config,
)

logger = logging.getLogger(__name__)


class AutoSettingsConfig:
    NAME = "AutoSettings"

    def __init__(
        self,
        *,
        game: GameSelector | None = None,
        server_number: int | str | None = None,
    ):
        self.SETTINGS = self.NAME
        self.game = game
        self.server_number = server_number

    def seed_db(self, sess):
        _set_default(
            sess,
            self.SETTINGS,
            DEFAULT_AUTO_SETTINGS,
            game=self.game,
            server_number=self.server_number,
        )

    def reset_settings(self, sess):
        _remove_conf(
            sess,
            self.SETTINGS,
            game=self.game,
            server_number=self.server_number,
        )
        _add_conf(
            sess,
            self.SETTINGS,
            DEFAULT_AUTO_SETTINGS,
            game=self.game,
            server_number=self.server_number,
        )

    def get_settings(self):
        return get_user_config(
            self.SETTINGS,
            game=self.game,
            server_number=self.server_number,
        )

    def set_settings(self, dict_):
        self.validate_settings(dict_)
        return set_user_config(
            self.SETTINGS,
            dict(dict_),
            game=self.game,
            server_number=self.server_number,
        )

    def validate_settings(self, settings) -> None:
        """Validate game-specific references embedded in auto-setting rules."""
        if not isinstance(settings, dict):
            raise ValueError("Auto settings must be a JSON object")
        rules = settings.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError("Auto settings rules must be a list")
        profile = get_game_profile(GameEnum.from_int(get_user_config_game(self.game)))
        valid_layers = {layer_id.casefold() for layer_id in profile.layers}
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise ValueError(f"Auto-settings rule {index} must be an object")
            conditions = rule.get("conditions", {})
            if not isinstance(conditions, dict):
                raise ValueError(
                    f"Auto-settings rule {index} conditions must be an object"
                )
            current_map = conditions.get("current_map")
            if current_map is None:
                continue
            if not isinstance(current_map, dict):
                raise ValueError(
                    f"Auto-settings rule {index} current_map must be an object"
                )
            map_names = current_map.get("map_names", [])
            if not isinstance(map_names, list):
                raise ValueError(
                    f"Auto-settings rule {index} current_map.map_names must be a list"
                )
            invalid_maps = sorted(
                str(map_name)
                for map_name in map_names
                if str(map_name).casefold() not in valid_layers
            )
            if invalid_maps:
                raise ValueError(
                    f"Maps are not valid for {profile.game.value}: "
                    + ", ".join(invalid_maps)
                )


DEFAULT_AUTO_SETTINGS = {
    "always_apply_defaults": False,
    "can_invoke_multiple_rules": False,
    "defaults": {},
    "rules": [],
    "_available_settings": {
        "always_apply_defaults": "Whether or not to apply the settings defined in the default section in each iteration. Allowed values: true / false",
        "can_invoke_multiple_rules": "Whether or not to allow the invocation of multiple rules e.g. don't stop after the first fulfilled rule. Allowed values: true / false",
    },
    "_available_commands": {},
    "_available_conditions": {
        "player_count": {"min": 0, "max": 100, "not": False},
        "time_of_day": {
            "min": "00:00",
            "max": "24:00",
            "timezone": "UTC",
            "not": False,
        },
        "online_mods": {"min": 0, "max": 100, "not": False},
        "ingame_mods": {"min": 0, "max": 100, "not": False},
        "current_map": {"map_names": ["stmariedumont_warfare", "..."], "not": False},
    },
}

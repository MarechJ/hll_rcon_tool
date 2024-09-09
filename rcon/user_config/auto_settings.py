import logging

from rcon.user_config.utils import (
    _add_conf,
    _remove_conf,
    _set_default,
    get_user_config,
    set_user_config,
)
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)


class AutoSettingsConfig:
    def __init__(self):
        server_number = get_server_number()
        self.SETTINGS = f"{server_number}_auto_settings"

    def seed_db(self, sess):
        _set_default(sess, self.SETTINGS, DEFAULT_AUTO_SETTINGS)

    def reset_settings(self, sess):
        _remove_conf(sess, self.SETTINGS)
        _add_conf(sess, self.SETTINGS, DEFAULT_AUTO_SETTINGS)

    def get_settings(self):
        return get_user_config(self.SETTINGS)

    def set_settings(self, dict_):
        return set_user_config(self.SETTINGS, dict(dict_))


DEFAULT_AUTO_SETTINGS = {
    "always_apply_defaults": False,
    "can_invoke_multiple_rules": False,
    "defaults": {
    },
    "rules": [],
    "_available_settings": {
        "always_apply_defaults": "Whether or not to apply the settings defined in the default section in each iteration. Allowed values: true / false",
        "can_invoke_multiple_rules": "Whether or not to allow the invocation of multiple rules e.g. don't stop after the first fulfilled rule. Allowed values: true / false",
    },
    "_available_commands": {
    },
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

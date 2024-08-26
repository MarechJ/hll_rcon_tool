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
        "set_idle_autokick_time": {"minutes": 10},
        "set_autobalance_threshold": {"max_diff": 3},
        "set_max_ping_autokick": {"max_ms": 500},
        "set_team_switch_cooldown": {"minutes": 15},
    },
    "rules": [],
    "_available_settings": {
        "always_apply_defaults": "Whether or not to apply the settings defined in the default section in each iteration. Allowed values: true / false",
        "can_invoke_multiple_rules": "Whether or not to allow the invocation of multiple rules e.g. don't stop after the first fulfilled rule. Allowed values: true / false",
    },
    "_available_commands": {
        "ban_profanities": {"profanities": ["word1", "word2"]},
        "unban_profanities": {"profanities": ["word1", "word2"]},
        "set_profanities": {"profanities": ["word1", "word2"]},
        "set_autobalance_enabled": {"value": "on/off"},
        "set_welcome_message": {"message": "A welcome message"},
        "set_map": {"map_name": "stmariedumont_warfare"},
        "set_idle_autokick_time": {"minutes": 0},
        "set_max_ping_autokick": {"max_ms": 0},
        "set_autobalance_threshold": {"max_diff": 0},
        "set_team_switch_cooldown": {"minutes": 0},
        "set_queue_length": {"num": 6},
        "set_vip_slots_num": {"num": 1},
        "set_broadcast": {"message": "A broadcast message", "save": True},
        "set_votekick_enabled": {"value": "on/off"},
        "set_votekick_threshold": {
            "threshold_pairs_str": "PlayerCount,Threshold[,PlayerCount,Threshold,...]"
        },
        "reset_votekick_threshold": {},
        "switch_player_on_death": {"player_name": "12345678901234567"},
        "switch_player_now": {"player_name": "12345678901234567"},
        "add_map_to_rotation": {"map_name": "stmariedumont_warfare"},
        "add_maps_to_rotation": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "remove_map_from_rotation": {"map_name": "stmariedumont_warfare"},
        "remove_maps_from_rotation": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "set_maprotation": {
            "rotation": [
                "Overwrites the current rotation",
                "Yes the spelling is intentional",
            ]
        },
        "set_map_shuffle_enabled": {"enabled": False},
        "punish": {"player_name": "12345678901234567", "reason": "Get rekt"},
        "kick": {"player_name": "12345678901234567", "reason": "Get rekt"},
        "temp_ban": {
            "player_name": "Optional, a player's name",
            "player_id": "Required if player_name not provided, a player's steam_id_64 or windows store ID",
            "duration_hours": "Optional, defaults to 2",
            "reason": "Optional, defaults to nothing",
            "admin_name": "Optional, defaults to nothing",
        },
        "perma_ban": {
            "player_name": "Optional, a player's name",
            "player_id": "Required if player_name not provided, a player's steam_id_64 or windows store ID",
            "reason": "Optional, defaults to nothing",
            "admin_name": "Optional, defaults to nothing",
        },
        "unban": {"player_id": "12345678901234567"},
        "add_admin": {
            "player_id": "1234567890123456",
            "role": "senior",
            "description": "A comment",
        },
        "remove_admin": {"player_id": "1234567890123456"},
        "add_vip": {"player_id": "1234567890123456", "description": "A comment"},
        "remove_vip": {"player_id": "1234567890123456"},
        "remove_all_vips": {},
        "add_map_to_votemap_whitelist": {"map_name": "stmariedumont_warfare"},
        "add_maps_to_votemap_whitelist": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "remove_map_from_votemap_whitelist": {"map_name": "stmariedumont_warfare"},
        "remove_maps_from_votemap_whitelist": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "reset_map_votemap_whitelist": {},
        "set_map_votemap_whitelist": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
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

import logging
import os

from rcon.models import enter_session
from rcon.user_config.utils import (
    _add_conf,
    _remove_conf,
    _set_default,
    get_user_config,
    set_user_config,
)

logger = logging.getLogger(__name__)


class AutoSettingsConfig:
    def __init__(self):
        server_number = os.getenv("SERVER_NUMBER", 0)
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
    "rules": [
        {
            "conditions": {"player_count": {"min": 0, "max": 30}},
            "commands": {
                "set_idle_autokick_time": {"minutes": 0},
                "set_autobalance_threshold": {"max_diff": 1},
                "set_max_ping_autokick": {"max_ms": 0},
                "set_team_switch_cooldown": {"minutes": 5},
            },
        },
        {
            "conditions": {"player_count": {"min": 30, "max": 50}},
            "commands": {
                "set_idle_autokick_time": {"minutes": 0},
                "set_autobalance_threshold": {"max_diff": 2},
                "set_max_ping_autokick": {"max_ms": 1000},
                "set_team_switch_cooldown": {"minutes": 10},
            },
        },
    ],
    "_available_settings": {
        "always_apply_defaults": "Whether or not to apply the settings defined in the default section in each iteration. Allowed values: true / false",
        "can_invoke_multiple_rules": "Whether or not to allow the invocation of multiple rules e.g. don't stop after the first fulfilled rule. Allowed values: true / false",
    },
    "_available_commands": {
        "do_ban_profanities": {"profanities": ["word1", "word2"]},
        "do_unban_profanities": {"profanities": ["word1", "word2"]},
        "set_profanities": {"profanities": ["word1", "word2"]},
        "set_autobalance_enabled": {"bool_str": "on/off"},
        "set_welcome_message": {"msg": "A welcome message", "save": True},
        "set_map": {"map_name": "stmariedumont_warfare"},
        "set_idle_autokick_time": {"minutes": 0},
        "set_max_ping_autokick": {"max_ms": 0},
        "set_autobalance_threshold": {"max_diff": 0},
        "set_team_switch_cooldown": {"minutes": 0},
        "set_queue_length": {"num": 6},
        "set_vip_slots_num": {"num": 1},
        "set_broadcast": {"msg": "A broadcast message", "save": True},
        "set_votekick_enabled": {"bool_str": "on/off"},
        "set_votekick_threshold": {
            "threshold_pairs_str": "PlayerCount,Threshold[,PlayerCount,Threshold,...]"
        },
        "do_reset_votekick_threshold": {},
        "do_switch_player_on_death": {"player": "12345678901234567"},
        "do_switch_player_now": {"player": "12345678901234567"},
        "do_add_map_to_rotation": {"map_name": "stmariedumont_warfare"},
        "do_add_maps_to_rotation": {
            "maps": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "do_remove_map_from_rotation": {"map_name": "stmariedumont_warfare"},
        "do_remove_maps_from_rotation": {
            "maps": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "do_randomize_map_rotation": {
            "maps": [
                "An optional list of maps",
                "that will replace the current rotation",
            ]
        },
        "set_maprotation": {
            "rotation": [
                "Overwrites the current rotation",
                "Yes the spelling is intentional",
            ]
        },
        "set_map_shuffle_enabled": {"enabled": False},
        "do_punish": {"player": "12345678901234567", "reason": "Get rekt"},
        "do_kick": {"player": "12345678901234567", "reason": "Get rekt"},
        "do_temp_ban": {
            "player_name": "Optional, a player's name",
            "steam_id_64": "Required if player_name not provided, a player's steam64id",
            "duration_hours": "Optional, defaults to 2",
            "reason": "Optional, defaults to nothing",
            "admin_name": "Optional, defaults to nothing",
        },
        "do_perma_ban": {
            "player_name": "Optional, a player's name",
            "steam_id_64": "Required if player_name not provided, a player's steam64id",
            "reason": "Optional, defaults to nothing",
            "admin_name": "Optional, defaults to nothing",
        },
        "do_unban": {"steam_id_64": "12345678901234567"},
        "do_add_admin": {
            "steam_id_64": "1234567890123456",
            "role": "senior",
            "name": "A comment",
        },
        "do_remove_admin": {"steam_id_64": "1234567890123456"},
        "do_add_vip": {"steam_id_64": "1234567890123456", "name": "A comment"},
        "do_remove_vip": {"steam_id_64": "1234567890123456"},
        "do_remove_all_vips": {},
        "do_add_map_to_whitelist": {"map_name": "stmariedumont_warfare"},
        "do_add_maps_to_whitelist": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "do_remove_map_from_whitelist": {"map_name": "stmariedumont_warfare"},
        "do_remove_maps_from_whitelist": {
            "map_names": ["stmariedumont_warfare", "kursk_offensive_rus"]
        },
        "do_reset_map_whitelist": {},
        "do_set_map_whitelist": {
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
        "current_map": {"maps": ["stmariedumont_warfare", "..."], "not": False},
    },
}


def seed_default_config():
    logger.info("Seeding DB")
    try:
        with enter_session() as sess:
            AutoSettingsConfig().seed_db(sess)
            sess.commit()
    except Exception as e:
        logger.exception("Failed to seed DB")

import logging
import random
import re
import time

from rcon.commands import CommandFailedError
from rcon.message_variables import populate_message_variables, format_message_string
from rcon.types import MessageVariable
from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.chat_commands import MESSAGE_VAR_RE

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 20

subs = {
    "nextmap": MessageVariable.next_map,
    "maprotation": MessageVariable.map_rotation,
    "servername": MessageVariable.server_name,
    "admins": MessageVariable.admin_names,
    "owners": MessageVariable.owner_names,
    "seniors": MessageVariable.senior_names,
    "juniors": MessageVariable.junior_names,
    "vips": MessageVariable.vip_names,
    "randomvip": MessageVariable.random_vip_name,
    "votenextmap_line": MessageVariable.votenextmap_line,
    "votenextmap_noscroll": MessageVariable.votenextmap_noscroll,
    "votenextmap_vertical": MessageVariable.votenextmap_vertical,
    "votenextmap_by_mod_line": MessageVariable.votenextmap_by_mod_line,
    "votenextmap_by_mod_vertical": MessageVariable.votenextmap_by_mod_vertical,
    "votenextmap_by_mod_vertical_all": MessageVariable.votenextmap_by_mod_vertical_all,
    "votenextmap_by_mod_split": MessageVariable.votenextmap_by_mod_split,
    "total_votes": MessageVariable.total_votes,
    "winning_maps_short": MessageVariable.winning_maps_short,
    "winning_maps_all": MessageVariable.winning_maps_all,
    "scrolling_votemap": MessageVariable.scrolling_votemap,
    "online_mods": MessageVariable.online_mods,
    "ingame_mods": MessageVariable.ingame_mods,
}


def format_message(ctl, msg):
    for sub in subs:
        msg = msg.replace(f"{{{sub}}}", f"{{{subs[sub].value}}}")
    message_vars: list[str] = re.findall(MESSAGE_VAR_RE, msg)
    populated_variables = populate_message_variables(
        vars=message_vars, player_id=None, rcon=ctl
    )

    try:
        return format_message_string(
            msg,
            populated_variables=populated_variables,
            context={},
        )
    except KeyError as e:
        logger.warning(
            "Can't broadcast message correctly, variable does not exists %s", e
        )
        return msg


def run():
    # avoid circular import
    from rcon.rcon import get_rcon

    ctl = get_rcon()

    while True:
        config = AutoBroadcastUserConfig.load_from_db()
        if not config.enabled or not config.messages:
            logger.debug(
                "Auto broadcasts are disabled. Sleeping %s seconds", CHECK_INTERVAL
            )
            time.sleep(CHECK_INTERVAL)
            continue

        if config.randomize:
            logger.debug("Auto broadcasts. Radomizing")
            random.shuffle(config.messages)

        for msg in config.messages:
            if not config.enabled:
                break

            formatted = format_message(ctl, msg.message)
            logger.debug("Broadcasting for %s seconds: %s", msg.time_sec, formatted)
            try:
                ctl.set_broadcast(formatted)
            except CommandFailedError:
                logger.exception("Unable to broadcast %s %s", msg.time_sec, msg.message)
            time.sleep(int(msg.time_sec))


if __name__ == "__main__":
    run()

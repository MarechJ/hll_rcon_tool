import logging
import math
import random
import time
from functools import partial
from typing import Sequence

from rcon import maps
from rcon.audit import ingame_mods, online_mods
from rcon.commands import CommandFailedError
from rcon.maps import categorize_maps, numbered_maps
from rcon.rcon import Rcon
from rcon.settings import SERVER_INFO
from rcon.types import VoteOverview
from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.vote_map import VoteMap


class LazyPrinter:
    def __init__(self, func, default="", is_list=False, list_separator=", "):
        self.func = func
        self.is_list = is_list
        self.default = default
        self.list_separator = list_separator

    def __str__(self):
        try:
            if self.is_list:
                return self.list_separator.join(self.func())
            return str(self.func())
        except:
            logger.exception("Unable to get data for broacasts")
            return self.default


def get_votes_status(none_on_fail=False) -> VoteOverview | None:
    return VoteMap().get_vote_overview()


def format_winning_map(
    ctl: Rcon,
    winning_maps: Sequence[tuple[maps.Layer, int]],
    display_count=2,
    default=None,
):
    nextmap: str = ctl.get_next_map()
    if not winning_maps:
        if default:
            return str(default)
        return f"{nextmap}"
    wins = winning_maps[:display_count]
    if display_count == 0:
        wins = winning_maps

    # Example warfare map: Carentan Warfare (2 vote(s))
    # Example offensive map: Driel Off. AXIS (2 vote(s))
    return ", ".join(
        f"{map_.pretty_name} ({num_votes} vote(s))" for map_, num_votes in wins
    )


logger = logging.getLogger(__name__)

CHECK_INTERVAL = 20


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def scrolling_votemap(rcon, winning_maps, repeat=10):
    config = VoteMapUserConfig.load_from_db()
    vote_options = format_map_vote(rcon, "line")
    if not vote_options:
        return ""
    separator = "  ***  "
    options = separator.join([vote_options] * repeat)
    instructions = config.instruction_text.replace("\n", " ")
    repeat_instructions = max(
        int(len(options) / (len(instructions) + len(separator))), 1
    )
    instructions = separator.join([instructions] * repeat_instructions)

    winning_maps = format_winning_map(
        rcon, winning_maps, display_count=0, default=config.no_vote_text
    )
    repeat_winning_maps = max(
        int(len(options) / (len(winning_maps) + len(separator))), 1
    )
    winning_maps = separator.join([winning_maps] * repeat_winning_maps)

    return "{}\n{}\n{}".format(options, instructions, winning_maps)


def format_by_line_length(possible_votes, max_length=50):
    """
    Note: I've tried to format with a nice aligned table but it's not
    possible to get it right (unless you hardcode it maybe)
    because the font used in the game does not have consistent characters (varying width)
    """
    lines = []
    line = ""
    for i in possible_votes:
        line += i + " "
        if len(line) > max_length:
            lines.append(line)
            line = ""
    lines.append(line)
    return "\n".join(lines)


def join_vote_options(
    selection: list[maps.Layer],
    maps_to_numbers: dict[maps.Layer, str],
    join_char: str = " ",
):
    return join_char.join(f"[{maps_to_numbers[m]}] {m.pretty_name}" for m in selection)


def format_map_vote(rcon, format_type="line"):
    selection = VoteMap().get_selection()
    if not selection:
        return ""

    # 0: map 1, 1: map 2, etc.
    vote_dict = numbered_maps(selection)
    # map 1: 0, map 2: 1, etc.
    maps_to_numbers = dict(zip(vote_dict.values(), vote_dict.keys()))
    items = [f"[{k}] {v.pretty_name}" for k, v in vote_dict.items()]
    if format_type == "line":
        return " // ".join(items)
    if format_type == "max_length":
        return format_by_line_length(items)
    if format_type == "vertical":
        return "\n".join(items)
    if format_type.startswith("by_mod"):
        categorized = categorize_maps(selection)
        off = join_vote_options(
            selection=categorized[maps.Gamemode.OFFENSIVE],
            maps_to_numbers=maps_to_numbers,
        )
        warfare = join_vote_options(
            selection=categorized[maps.Gamemode.WARFARE],
            maps_to_numbers=maps_to_numbers,
        )
        control_skirmish = join_vote_options(
            selection=categorized[maps.Gamemode.CONTROL],
            maps_to_numbers=maps_to_numbers,
        )
        if format_type == "by_mod_line":
            return "OFFENSIVE: {} WARFARE: {} CONTROL SKIRMISH: {}".format(
                off, warfare, control_skirmish
            )
        if format_type == "by_mod_vertical":
            return "OFFENSIVE:\n{}\nWARFARE:\n{}\nCONTROL SKIRMISH:\n{}".format(
                off, warfare, control_skirmish
            )
        if format_type == "by_mod_split":
            return "OFFENSIVE: {}\nWARFARE: {}\nCONTROL SKIRMISH: {}".format(
                off, warfare, control_skirmish
            )
        if format_type == "by_mod_vertical_all":
            return "OFFENSIVE:\n{}\nWARFARE:\n{}\nCONTROL SKIRMISH:\n{}".format(
                join_vote_options(
                    selection=categorized[maps.Gamemode.OFFENSIVE],
                    maps_to_numbers=maps_to_numbers,
                    join_char="\n",
                ),
                join_vote_options(
                    selection=categorized[maps.Gamemode.WARFARE],
                    maps_to_numbers=maps_to_numbers,
                    join_char="\n",
                ),
                join_vote_options(
                    selection=categorized[maps.Gamemode.CONTROL],
                    maps_to_numbers=maps_to_numbers,
                    join_char="\n",
                ),
            )


def get_online_mods():
    return [mod["username"] for mod in online_mods()]


def get_ingame_mods():
    return [mod["username"] for mod in ingame_mods()]


def _get_vars(ctl: Rcon):
    get_vip_names = lambda: [d["name"] for d in ctl.get_vip_ids()]
    get_admin_names = lambda: [d["name"] for d in ctl.get_admin_ids()]
    get_owner_names = lambda: [
        d["name"] for d in ctl.get_admin_ids() if d["role"] == "owner"
    ]
    get_senior_names = lambda: [
        d["name"] for d in ctl.get_admin_ids() if d["role"] == "senior"
    ]
    get_junior_names = lambda: [
        d["name"] for d in ctl.get_admin_ids() if d["role"] == "junior"
    ]

    def get_next_map():
        map_name: str = ctl.get_next_map().pretty_name
        smart_map = maps.parse_layer(map_name)
        return smart_map.pretty_name

    vote_status = get_votes_status()

    subs = {
        "nextmap": LazyPrinter(get_next_map),
        "maprotation": LazyPrinter(
            ctl.get_map_rotation, is_list=True, list_separator=" -> "
        ),
        "servername": LazyPrinter(ctl.get_name),
        "admins": LazyPrinter(get_admin_names, is_list=True),
        "owners": LazyPrinter(get_owner_names, is_list=True),
        "seniors": LazyPrinter(get_senior_names, is_list=True),
        "juniors": LazyPrinter(get_junior_names, is_list=True),
        "vips": LazyPrinter(get_vip_names, is_list=True),
        "randomvip": LazyPrinter(lambda: random.choice(get_vip_names() or [""])),
        "votenextmap_line": LazyPrinter(
            partial(format_map_vote, ctl, format_type="line")
        ),
        "votenextmap_noscroll": LazyPrinter(
            partial(format_map_vote, ctl, format_type="max_length")
        ),
        "votenextmap_vertical": LazyPrinter(
            partial(format_map_vote, ctl, format_type="vertical")
        ),
        "votenextmap_by_mod_line": LazyPrinter(
            partial(format_map_vote, ctl, format_type="by_mod_line")
        ),
        "votenextmap_by_mod_vertical": LazyPrinter(
            partial(format_map_vote, ctl, format_type="by_mod_vertical")
        ),
        "votenextmap_by_mod_vertical_all": LazyPrinter(
            partial(format_map_vote, ctl, format_type="by_mod_vertical_all")
        ),
        "votenextmap_by_mod_split": LazyPrinter(
            partial(format_map_vote, ctl, format_type="by_mod_split")
        ),
        # TODO: fix this after verifying Redis format
        "total_votes": vote_status.get("total_votes") if vote_status else math.nan,
        "winning_maps_short": LazyPrinter(
            partial(
                format_winning_map, ctl, vote_status["winning_maps"], display_count=2
            )
        ),
        "winning_maps_all": LazyPrinter(
            partial(
                format_winning_map, ctl, vote_status["winning_maps"], display_count=0
            )
        ),
        "scrolling_votemap": LazyPrinter(
            partial(scrolling_votemap, ctl, vote_status["winning_maps"])
        ),
        "online_mods": LazyPrinter(get_online_mods, is_list=True),
        "ingame_mods": LazyPrinter(get_ingame_mods, is_list=True),
    }

    return subs


def format_message(ctl, msg):
    subs = _get_vars(ctl)

    try:
        return msg.format(**subs)
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

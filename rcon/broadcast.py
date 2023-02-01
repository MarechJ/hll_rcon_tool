import asyncio
import logging
import random
from functools import partial

from rcon.audit import ingame_mods, online_mods
from rcon.commands import CommandFailedError
from rcon.extended_commands import Rcon
from rcon.recorded_commands import RecordedRcon
from rcon.user_config import AutoBroadcasts, VoteMapConfig
from rcon.utils import (
    LONG_HUMAN_MAP_NAMES,
    NO_MOD_LONG_HUMAN_MAP_NAMES,
    NO_MOD_SHORT_HUMAN_MAP_NAMES,
    SHORT_HUMAN_MAP_NAMES,
    categorize_maps,
    numbered_maps,
)
from rcon.vote_map import VoteMap


logger = logging.getLogger(__name__)

CHECK_INTERVAL = 20


class LazyPrinter:
    def __init__(self, log: logging.Logger, func, default="", is_list=False, list_separator=", "):
        self.logger = log
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
            self.logger.exception("Unable to get data for broacasts")
            return self.default


def get_votes_status():
    return VoteMap().get_vote_overview()


def format_winning_map(ctl, winning_maps, display_count=2, default=None):
    nextmap = ctl.get_next_map()
    if not winning_maps:
        if default:
            return str(default)
        return f"{nextmap}"
    wins = winning_maps[:display_count]
    if display_count == 0:
        wins = winning_maps
    return ", ".join(
        f"{LONG_HUMAN_MAP_NAMES[m]} ({count} vote(s))" for m, count in wins
    )


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def scrolling_votemap(rcon, winning_maps, repeat=10):
    config = VoteMapConfig()
    vote_options = format_map_vote("line", short_names=False)
    if not vote_options:
        return ""
    separator = "  ***  "
    options = separator.join([vote_options] * repeat)
    instructions = config.get_votemap_instruction_text().replace("\n", " ")
    repeat_instructions = max(
        int(len(options) / (len(instructions) + len(separator))), 1
    )
    instructions = separator.join([instructions] * repeat_instructions)

    winning_maps = format_winning_map(
        rcon, winning_maps, display_count=0, default=config.get_votemap_no_vote_text()
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


def join_vote_options(join_char, selection, human_name_map, maps_to_numbers):
    return join_char.join(
        f"[{maps_to_numbers[m]}] {human_name_map[m]}" for m in selection
    )


def format_map_vote(format_type="line", short_names=True):
    selection = VoteMap().get_selection()
    if not selection:
        return ""
    human_map = SHORT_HUMAN_MAP_NAMES if short_names else LONG_HUMAN_MAP_NAMES
    human_map_mod = (
        NO_MOD_SHORT_HUMAN_MAP_NAMES if short_names else NO_MOD_LONG_HUMAN_MAP_NAMES
    )
    vote_dict = numbered_maps(selection)
    maps_to_numbers = dict(zip(vote_dict.values(), vote_dict.keys()))
    items = [f"[{k}] {human_map.get(v, v)}" for k, v in vote_dict.items()]
    if format_type == "line":
        return " // ".join(items)
    if format_type == "max_length":
        return format_by_line_length(items)
    if format_type == "vertical":
        return "\n".join(items)
    if format_type.startswith("by_mod"):
        categorized = categorize_maps(selection)
        off = join_vote_options(
            "  ", categorized["offensive"], human_map_mod, maps_to_numbers
        )
        warfare = join_vote_options(
            "  ", categorized["warfare"], human_map_mod, maps_to_numbers
        )
        if format_type == "by_mod_line":
            return "OFFENSIVE: {} WARFARE: {}".format(off, warfare)
        if format_type == "by_mod_vertical":
            return "OFFENSIVE:\n{}\nWARFARE:\n{}".format(off, warfare)
        if format_type == "by_mod_split":
            return "OFFENSIVE: {}\nWARFARE: {}".format(off, warfare)
        if format_type == "by_mod_vertical_all":
            return "OFFENSIVE:\n{}\nWARFARE:\n{}".format(
                join_vote_options(
                    "\n", categorized["offensive"], human_map_mod, maps_to_numbers
                ),
                join_vote_options(
                    "\n", categorized["warfare"], human_map_mod, maps_to_numbers
                ),
            )


def get_online_mods():
    return [mod["username"] for mod in online_mods()]


def get_ingame_mods():
    return [mod["username"] for mod in ingame_mods()]


def _get_vars(log: logging.Logger, ctl: Rcon):
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
        m = ctl.get_next_map()
        return LONG_HUMAN_MAP_NAMES.get(m, m)

    vote_status = get_votes_status()

    subs = {
        "nextmap": LazyPrinter(log, get_next_map),
        "maprotation": LazyPrinter(
            log, ctl.get_map_rotation, is_list=True, list_separator=" -> "
        ),
        "servername": LazyPrinter(log, ctl.get_name),
        "admins": LazyPrinter(log, get_admin_names, is_list=True),
        "owners": LazyPrinter(log, get_owner_names, is_list=True),
        "seniors": LazyPrinter(log, get_senior_names, is_list=True),
        "juniors": LazyPrinter(log, get_junior_names, is_list=True),
        "vips": LazyPrinter(log, get_vip_names, is_list=True),
        "randomvip": LazyPrinter(log, lambda: random.choice(get_vip_names() or [""])),
        "votenextmap_line": LazyPrinter(
            log, partial(format_map_vote, format_type="line")
        ),
        "votenextmap_noscroll": LazyPrinter(
            log, partial(format_map_vote, format_type="max_length")
        ),
        "votenextmap_vertical": LazyPrinter(
            log, partial(format_map_vote, format_type="vertical")
        ),
        "votenextmap_by_mod_line": LazyPrinter(
            log, partial(format_map_vote, format_type="by_mod_line")
        ),
        "votenextmap_by_mod_vertical": LazyPrinter(
            log, partial(format_map_vote, format_type="by_mod_vertical")
        ),
        "votenextmap_by_mod_vertical_all": LazyPrinter(
            log, partial(format_map_vote, format_type="by_mod_vertical_all")
        ),
        "votenextmap_by_mod_split": LazyPrinter(
            log, partial(format_map_vote, format_type="by_mod_split")
        ),
        "total_votes": vote_status.get("total_votes"),
        "winning_maps_short": LazyPrinter(
            log, partial(
                format_winning_map, ctl, vote_status["winning_maps"], display_count=2
            )
        ),
        "winning_maps_all": LazyPrinter(
            log, partial(
                format_winning_map, ctl, vote_status["winning_maps"], display_count=0
            )
        ),
        "scrolling_votemap": LazyPrinter(
            log, partial(scrolling_votemap, ctl, vote_status["winning_maps"])
        ),
        "online_mods": LazyPrinter(log, get_online_mods, is_list=True),
        "ingame_mods": LazyPrinter(log, get_ingame_mods, is_list=True),
    }

    return subs


def format_message(log: logging.Logger, ctl: Rcon, msg):
    subs = _get_vars(log, ctl)

    try:
        return msg.format(**subs)
    except KeyError as e:
        log.warning(
            "Can't broadcast message correctly, variable does not exists %s", e
        )
        return msg


async def run(log: logging.Logger, rcon: RecordedRcon):
    config = AutoBroadcasts()

    while True:
        msgs = config.get_messages()

        if not config.get_enabled() or not msgs:
            log.debug(
                "Auto broadcasts are disabled. Sleeping %s seconds", CHECK_INTERVAL
            )
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        if config.get_randomize():
            log.debug("Auto broadcasts. Randomizing")
            random.shuffle(msgs)

        for time_sec, msg in msgs:
            if not config.get_enabled():
                break

            formatted = format_message(log, rcon, msg)
            log.debug("Broadcasting for %s seconds: %s", time_sec, formatted)
            try:
                rcon.set_broadcast(formatted)
            except CommandFailedError:
                log.exception("Unable to broadcast %s", msg)
            await asyncio.sleep(int(time_sec))

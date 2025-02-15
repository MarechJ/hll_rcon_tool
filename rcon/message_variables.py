import math
import random
from datetime import datetime
from functools import partial
from itertools import takewhile
from logging import getLogger
from typing import Any, Iterable, Sequence

from rcon import maps
from rcon.audit import ingame_mods, online_mods
from rcon.maps import Layer, categorize_maps, numbered_maps
from rcon.rcon import Rcon, get_rcon
from rcon.scoreboard import get_cached_live_game_stats, get_stat
from rcon.types import CachedLiveGameStats, MessageVariable, StatTypes, VipIdType
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.user_config.webhooks import AdminPingWebhooksUserConfig
from rcon.utils import SafeStringFormat
from rcon.vote_map import VoteMap

logger = getLogger(__name__)


def populate_message_variables(
    vars: Iterable[str],
    player_id: str | None = None,
    rcon: Rcon | None = None,
) -> dict[MessageVariable, str | None]:
    """Return globally available info for message formatting"""
    populated_variables: dict[MessageVariable, str | None] = {}
    if rcon is None:
        rcon = get_rcon()

    vote_results: list[tuple[Layer, int]] | None = None
    def fetch_vote_results():
        nonlocal vote_results
        if vote_results is None:
            vote_results = vote_status()
        return vote_results

    message_variable_to_lookup = {
        MessageVariable.vip_status: lambda: _is_vip(player_id=player_id, rcon=rcon),
        MessageVariable.vip_expiration: lambda: _vip_expiration(
            player_id=player_id, rcon=rcon
        ),
        MessageVariable.server_name: rcon.get_name,
        MessageVariable.server_short_name: _server_short_name,
        MessageVariable.discord_invite_url: _discord_invite_url,
        MessageVariable.admin_ping_trigger_words: _admin_ping_trigger_words,
        MessageVariable.num_online_mods: lambda: str(len(online_mods())),
        MessageVariable.num_ingame_mods: lambda: str(len(ingame_mods())),
        MessageVariable.next_map: _next_map,
        MessageVariable.next_map_id: _next_map_id,
        MessageVariable.map_rotation: _map_rotation,
        MessageVariable.top_kills_player_name: lambda: _generic_score_ties(
            stat_key=StatTypes.top_killers, tie_key="kills", result_key="player"
        ),
        MessageVariable.top_kills_player_score: lambda: _generic_score_top_only(
            stat_key=StatTypes.top_killers, result_key="kills"
        ),
        MessageVariable.top_kill_streak_player_name: lambda: _generic_score_ties(
            stat_key=StatTypes.top_kill_streak,
            tie_key="kills_streak",
            result_key="player",
        ),
        MessageVariable.top_kill_streak_player_score: lambda: _generic_score_top_only(
            stat_key=StatTypes.top_kill_streak, result_key="kills_streak"
        ),
        MessageVariable.votenextmap_line: partial(format_map_vote, format_type="line"),
        MessageVariable.votenextmap_noscroll: partial(
            format_map_vote, format_type="max_length"
        ),
        MessageVariable.votenextmap_vertical: partial(
            format_map_vote, format_type="vertical"
        ),
        MessageVariable.votenextmap_by_mod_line: partial(
            format_map_vote, format_type="by_mod_line"
        ),
        MessageVariable.votenextmap_by_mod_vertical: partial(
            format_map_vote, format_type="by_mod_vertical"
        ),
        MessageVariable.votenextmap_by_mod_vertical_all: partial(
            format_map_vote, format_type="by_mod_vertical_all"
        ),
        MessageVariable.votenextmap_by_mod_split: partial(
            format_map_vote, format_type="by_mod_split"
        ),
        MessageVariable.total_votes: lambda: (
            sum(v for m, v in fetch_vote_results()) if fetch_vote_results() else math.nan
        ),
        MessageVariable.winning_maps_short: lambda: format_winning_map(rcon, fetch_vote_results(), 2),
        MessageVariable.winning_maps_all: lambda: format_winning_map(rcon, fetch_vote_results(), 0),
        MessageVariable.scrolling_votemap: lambda: scrolling_votemap(rcon, fetch_vote_results()),
        # Deprecated: Taken over from previous auto-broadcast
        MessageVariable.admin_names: lambda: [d["name"] for d in rcon.get_admin_ids()],
        MessageVariable.owner_names: lambda: [
            d["name"] for d in rcon.get_admin_ids() if d["role"] == "owner"
        ],
        MessageVariable.senior_names: lambda: [
            d["name"] for d in rcon.get_admin_ids() if d["role"] == "senior"
        ],
        MessageVariable.junior_names: lambda: [
            d["name"] for d in rcon.get_admin_ids() if d["role"] == "junior"
        ],
        MessageVariable.vip_names: lambda: [d["name"] for d in rcon.get_vip_ids()],
        MessageVariable.random_vip_name: lambda: random.choice(
            [d["name"] for d in rcon.get_vip_ids()]
        ),
        MessageVariable.online_mods: lambda: [mod["username"] for mod in online_mods()],
        MessageVariable.ingame_mods: lambda: [mod["username"] for mod in ingame_mods()],
    }

    for raw_var in vars:
        try:
            var = MessageVariable[raw_var]
        except KeyError:
            # Not logging this because otherwise any context passed variables would
            # clutter the logs every single message
            continue

        populated_variables[var] = message_variable_to_lookup[var]()

    return populated_variables


def scrolling_votemap(rcon, winning_maps, repeat=10):
    config = VoteMapUserConfig.load_from_db()
    vote_options = format_map_vote("line")
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


def format_winning_map(
    ctl: Rcon,
    winning_maps: Sequence[tuple[maps.Layer, int]],
    display_count=2,
    default=None,
):
    nextmap = ctl.get_next_map()
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


def vote_status() -> list[tuple[Layer, int]]:
    logger.info(f"Crunching vote_status")
    vote_results = VoteMap().get_vote_overview()
    if vote_results:
        return [(m, v) for m, v in vote_results.items()]
    else:
        return []


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


def format_map_vote(format_type="line"):
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
            selection=categorized[maps.GameMode.OFFENSIVE],
            maps_to_numbers=maps_to_numbers,
        )
        warfare = join_vote_options(
            selection=categorized[maps.GameMode.WARFARE],
            maps_to_numbers=maps_to_numbers,
        )
        control_skirmish = join_vote_options(
            selection=categorized[maps.GameMode.CONTROL],
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
                    selection=categorized[maps.GameMode.OFFENSIVE],
                    maps_to_numbers=maps_to_numbers,
                    join_char="\n",
                ),
                join_vote_options(
                    selection=categorized[maps.GameMode.WARFARE],
                    maps_to_numbers=maps_to_numbers,
                    join_char="\n",
                ),
                join_vote_options(
                    selection=categorized[maps.GameMode.CONTROL],
                    maps_to_numbers=maps_to_numbers,
                    join_char="\n",
                ),
            )


def format_message_string(
    format_str: str,
    populated_variables: dict[MessageVariable, str | None] | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    """Safely fill format_str"""
    if context is None:
        context = {}

    if populated_variables is None:
        populated_variables = {}

    combined = {k.value: v for k, v in populated_variables.items()} | context

    formatted_str = format_str.format_map(SafeStringFormat(**combined))
    return formatted_str


def _vip_status(
    player_id: str | None = None, rcon: Rcon | None = None
) -> VipIdType | None:
    if rcon is None:
        rcon = get_rcon()

    vip = [v for v in rcon.get_vip_ids() if v["player_id"] == player_id]
    logger.info(f"{vip=}")

    if vip:
        return vip[0]


def _is_vip(player_id: str | None = None, rcon: Rcon | None = None) -> bool:
    vip = _vip_status(player_id=player_id, rcon=rcon)

    return vip is not None


def _vip_expiration(
    player_id: str | None = None, rcon: Rcon | None = None
) -> datetime | None:
    vip = _vip_status(player_id=player_id, rcon=rcon)

    return vip["vip_expiration"] if vip else None


def _server_short_name(config: RconServerSettingsUserConfig | None = None) -> str:
    if config is None:
        config = RconServerSettingsUserConfig.load_from_db()
    return config.short_name


def _discord_invite_url(config: RconServerSettingsUserConfig | None = None) -> str:
    if config is None:
        config = RconServerSettingsUserConfig.load_from_db()
    return (
        str(config.discord_invite_url)
        if config.discord_invite_url
        else "Discord invite URL not set"
    )


def _admin_ping_trigger_words(config: AdminPingWebhooksUserConfig | None = None) -> str:
    if config is None:
        config = AdminPingWebhooksUserConfig.load_from_db()
    return ", ".join(config.trigger_words[:])


def _next_map(rcon: Rcon | None = None) -> str:
    if rcon is None:
        rcon = get_rcon()
    return rcon.get_next_map().pretty_name


def _next_map_id(rcon: Rcon | None = None) -> str:
    if rcon is None:
        rcon = get_rcon()
    return rcon.get_next_map().id


def _map_rotation(rcon: Rcon | None = None):
    if rcon is None:
        rcon = get_rcon()
    map_rot = rcon.get_map_rotation()
    map_names = [map_.pretty_name for map_ in map_rot]
    return ", ".join(map_names)


def _generic_score_ties(
    stat_key: StatTypes,
    tie_key: str,
    result_key: str,
    stats: CachedLiveGameStats | None = None,
    num_ties=3,
):
    if stats is None:
        stats = get_cached_live_game_stats()

    print(stats)
    metric_stats = get_stat(stats["stats"], key=stat_key, limit=num_ties)
    collect_ties = takewhile(
        lambda x: x[tie_key] == metric_stats[0][tie_key], metric_stats
    )
    return ", ".join(p[result_key] for p in collect_ties)


def _generic_score_top_only(
    stat_key: StatTypes,
    result_key: str,
    stats: CachedLiveGameStats | None = None,
):
    stats = get_cached_live_game_stats()
    metric_stats = get_stat(stats["stats"], key=stat_key, limit=1)
    return str(metric_stats[0][result_key])

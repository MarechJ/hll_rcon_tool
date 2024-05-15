from datetime import datetime
from itertools import takewhile
from logging import getLogger
from typing import Any, Iterable

from rcon.audit import ingame_mods, online_mods
from rcon.rcon import Rcon, get_rcon
from rcon.scoreboard import get_cached_live_game_stats, get_stat
from rcon.settings import SERVER_INFO
from rcon.types import CachedLiveGameStats, MessageVariable, StatTypes, VipIdType
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import AdminPingWebhooksUserConfig
from rcon.utils import SafeStringFormat

logger = getLogger(__name__)


def populate_message_variables(
    vars: Iterable[str],
    player_id: str | None = None,
) -> dict[MessageVariable, str | None]:
    """Return globally available info for message formatting"""
    populated_variables: dict[MessageVariable, str | None] = {}
    rcon = get_rcon()

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


def _next_map(rcon: Rcon | None = None):
    if rcon is None:
        rcon = get_rcon()
    return rcon.next_map.pretty_name


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

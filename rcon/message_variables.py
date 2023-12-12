from itertools import takewhile
from logging import getLogger
from typing import Any, Iterable

from rcon.audit import ingame_mods, online_mods
from rcon.rcon import Rcon
from rcon.scoreboard import get_cached_live_game_stats, get_stat
from rcon.settings import SERVER_INFO
from rcon.types import MessageVariable, StatTypes
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import AdminPingWebhooksUserConfig
from rcon.utils import SHORT_HUMAN_MAP_NAMES, SafeStringFormat

logger = getLogger(__name__)

rcon = None


def _get_rcon():
    global rcon
    if rcon is None:
        rcon = Rcon(SERVER_INFO)

    return rcon


def populate_message_variables(
    vars: Iterable[str],
) -> dict[MessageVariable, str | None]:
    populated_variables: dict[MessageVariable, str | None] = {}
    rcon = Rcon(SERVER_INFO)

    message_variable_to_lookup = {
        MessageVariable.server_name: rcon.get_name,
        MessageVariable.server_short_name: _server_short_name,
        MessageVariable.discord_invite_url: _discord_invite_url,
        MessageVariable.admin_ping_trigger_words: _admin_ping_trigger_words,
        MessageVariable.num_online_mods: lambda: str(len(online_mods())),
        MessageVariable.num_ingame_mods: lambda: str(len(ingame_mods())),
        MessageVariable.next_map: _next_map,
        MessageVariable.map_rotation: _map_rotation,
        MessageVariable.top_kills_player_name: _top_kills_player_name,
        MessageVariable.top_kills_player_score: _top_kills_player_score,
    }

    for raw_var in vars:
        try:
            var = MessageVariable(raw_var)
        except ValueError:
            logger.error("%s is not a valid MessageVariable", raw_var)
            continue

        populated_variables[var] = message_variable_to_lookup[var]()

    return populated_variables


def format_message_string(
    format_str: str,
    populated_variables: dict[MessageVariable, str | None],
    context: dict[str, Any] | None = None,
) -> str:
    if context is None:
        context = {}

    combined = {k.value: v for k, v in populated_variables.items()} | context

    logger.info(f"{combined=}")
    logger.error(f"{format_str=}")

    res = format_str.format_map(SafeStringFormat(combined))
    logger.error(f"{res=}")
    return res


def _server_short_name(config: RconServerSettingsUserConfig | None = None):
    if config is None:
        config = RconServerSettingsUserConfig.load_from_db()
    return config.short_name


def _discord_invite_url(config: RconServerSettingsUserConfig | None = None):
    if config is None:
        config = RconServerSettingsUserConfig.load_from_db()
    return (
        str(config.discord_invite_url)
        if config.discord_invite_url
        else config.discord_invite_url
    )


def _admin_ping_trigger_words(config: AdminPingWebhooksUserConfig | None = None):
    if config is None:
        config = AdminPingWebhooksUserConfig.load_from_db()
    return ", ".join(config.trigger_words[:])


def _next_map(rcon: Rcon | None = None):
    if rcon is None:
        rcon = _get_rcon()
    map_name = rcon.get_gamestate().get("next_map")
    return SHORT_HUMAN_MAP_NAMES.get(map_name, map_name)


def _map_rotation(rcon: Rcon | None = None):
    if rcon is None:
        rcon = _get_rcon()
    map_rot = rcon.get_map_rotation()
    map_names = [SHORT_HUMAN_MAP_NAMES.get(map_name, map_name) for map_name in map_rot]
    return ", ".join(map_names)


def _top_kills_player_name(stats=None, num_ties=3):
    if stats is None:
        stats = get_cached_live_game_stats()

    metric_stats = get_stat(stats["stats"], key=StatTypes.top_killers, limit=num_ties)
    collect_ties = takewhile(
        lambda x: x["kills"] == metric_stats[0]["kills"], metric_stats
    )
    return ", ".join(p["player"] for p in collect_ties)


def _top_kills_player_score(stats=None):
    stats = get_cached_live_game_stats()
    metric_stats = get_stat(stats["stats"], key=StatTypes.top_killers, limit=1)
    return str(metric_stats[0]["kills"])

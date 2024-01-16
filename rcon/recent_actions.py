from collections import defaultdict
from logging import getLogger

from rcon.cache_utils import invalidates, ttl_cache
from rcon.game_logs import on_kill, on_tk
from rcon.rcon import Rcon
from rcon.types import MostRecentEvents, StructuredLogLineWithMetaData

logger = getLogger(__name__)

RECENT_ACTIONS: defaultdict[str, MostRecentEvents] | None = None


@ttl_cache(60, is_method=False)
def get_recent_actions() -> defaultdict[str, MostRecentEvents]:
    global RECENT_ACTIONS
    if RECENT_ACTIONS is None:
        RECENT_ACTIONS = defaultdict(MostRecentEvents)

    return RECENT_ACTIONS


def set_recent_actions(recent_actions: defaultdict[str, MostRecentEvents]):
    global RECENT_ACTIONS
    with invalidates(get_recent_actions):
        RECENT_ACTIONS = recent_actions


@on_kill
def update_kills(rcon: Rcon, log: StructuredLogLineWithMetaData):
    killer_name = log["player"]
    killer_steam_id = log["steam_id_64_1"]
    victim_name = log["player2"]
    victim_steam_id = log["steam_id_64_2"]
    weapon = log["weapon"]

    if not killer_steam_id or not victim_steam_id:
        logger.error(
            "update_kills called with killer_steam_id=%s victim_steam_id=%s",
            killer_steam_id,
            victim_steam_id,
        )
        return

    cached_actions = get_recent_actions()
    killer = cached_actions[killer_steam_id]
    victim = cached_actions[victim_steam_id]

    killer.player_name = killer_name
    killer.last_victim_steam_id_64 = victim_steam_id
    killer.last_victim_name = victim_name
    killer.last_victim_weapon = weapon

    victim.player_name = victim_name
    victim.last_nemesis_steam_id_64 = killer_steam_id
    victim.last_nemesis_name = killer_name
    victim.last_nemesis_weapon = weapon

    set_recent_actions(cached_actions)


@on_tk
def update_tks(rcon: Rcon, log: StructuredLogLineWithMetaData):
    killer_name = log["player"]
    killer_steam_id = log["steam_id_64_1"]
    victim_name = log["player2"]
    victim_steam_id = log["steam_id_64_2"]
    weapon = log["weapon"]

    if not killer_steam_id or not victim_steam_id:
        logger.error(
            "update_kills called with killer_steam_id=%s victim_steam_id=%s",
            killer_steam_id,
            victim_steam_id,
        )
        return

    cached_actions = get_recent_actions()
    killer = cached_actions[killer_steam_id]
    victim = cached_actions[victim_steam_id]

    killer.player_name = killer_name
    killer.last_tk_victim_steam_id_64 = victim_steam_id
    killer.last_tk_victim_name = victim_name
    killer.last_tk_victim_weapon = weapon

    victim.player_name = victim_name
    victim.last_tk_nemesis_steam_id_64 = killer_steam_id
    victim.last_tk_nemesis_name = killer_name
    victim.last_tk_nemesis_weapon = weapon

    set_recent_actions(cached_actions)

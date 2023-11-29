from rcon.game_logs import on_kill, on_tk
from rcon.cache_utils import ttl_cache, invalidates
from rcon.rcon import Rcon
from rcon.types import MostRecentEvents, StructuredLogLineWithMetaData
from collections import defaultdict

from logging import getLogger

logger = getLogger(__name__)

RECENT_ACTIONS = None


@ttl_cache(60, is_method=False)
def recent_actions(recent_actions) -> defaultdict[str, MostRecentEvents]:
    global RECENT_ACTIONS
    if not RECENT_ACTIONS:
        RECENT_ACTIONS = defaultdict(MostRecentEvents)

    if recent_actions:
        RECENT_ACTIONS = recent_actions

    return RECENT_ACTIONS


@on_kill
def update_kills(rcon: Rcon, log: StructuredLogLineWithMetaData):
    with invalidates(recent_actions):
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

        cached_actions = recent_actions(RECENT_ACTIONS)
        killer = cached_actions[killer_steam_id]
        victim = cached_actions[victim_steam_id]

        killer.last_victim = victim_steam_id
        killer.last_victim_weapon = weapon
        killer.player_name = killer_name

        victim.last_nemesis = killer_steam_id
        victim.last_nemesis_weapon = weapon
        victim.player_name = victim_name

        recent_actions(cached_actions)


@on_tk
def update_tks(rcon: Rcon, log: StructuredLogLineWithMetaData):
    with invalidates(recent_actions):
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

        cached_actions = recent_actions(RECENT_ACTIONS)
        killer = cached_actions[killer_steam_id]
        victim = cached_actions[victim_steam_id]

        killer.last_tk_victim = victim_steam_id
        killer.last_tk_victim_weapon = weapon
        killer.player_name = killer_name

        victim.last_tk_nemesis = killer_steam_id
        victim.last_tk_nemesis_weapon = weapon
        victim.player_name = victim_name

        recent_actions(cached_actions)

import os
import time
import logging
import random
from functools import partial
import json

import redis

import redis
from rcon.cache_utils import get_redis_pool
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from rcon.user_config import AutoBroadcasts
from rcon.audit import online_mods, get_registered_mods
from rcon.utils import HUMAN_MAP_NAMES, number_to_map
from functools import wraps


def get_votes_status():
    try:
        red = redis.StrictRedis(connection_pool=get_redis_pool())
        data = red.get("votes")
        if data:
            return json.loads(data)
    except:
        logger.exception("Unable to retrieve votes")
    return {'total_votes': 0, "winning_maps": []}
        

def format_winning_map(winning_maps, display_count=2, default=''):
    if not winning_maps:
        return f'Defaulting to: {default}'
    return ', '.join(f'{HUMAN_MAP_NAMES[m]} ({count} vote(s))' for m, count in winning_maps[:display_count])

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 20

def safe(func, default=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.exception("Unable to get data for broacasts")
            return default
    return wrapper

def ingame_admins(ctl):
    return ctl.get_ingame_mods(get_registered_mods())
    
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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


def format_map_vote(rcon):
    vote_dict = number_to_map(rcon)
    items = [f"[{k}] {HUMAN_MAP_NAMES.get(v, v)}"  for k, v in vote_dict.items()]
    return format_by_line_length(items)
    

def run():
    ctl = Rcon(
        SERVER_INFO
    )

    config = AutoBroadcasts()

    while True: 
        msgs = config.get_messages()

        if not config.get_enabled() or not msgs:
            logger.debug("Auto broadcasts are disabled. Sleeping %s seconds", CHECK_INTERVAL)
            time.sleep(CHECK_INTERVAL)
            continue
     
        if config.get_randomize():
            logger.debug("Auto broadcasts. Radomizing")
            random.shuffle(msgs)

        for time_sec, msg in msgs:
            if not config.get_enabled():
                break
            vote_status = get_votes_status()
            nextmap = safe(ctl.get_next_map, "")()
            subs = {
                'nextmap': nextmap,
                'maprotation': ' -> '.join(safe(ctl.get_map_rotation, [])()),
                'servername': safe(ctl.get_name, "")(),
                'onlineadmins': safe(online_mods, "")(),
                'ingameadmins': safe(ingame_admins, "")(ctl), 
                'votenextmap': safe(format_map_vote, '')(ctl),
                'total_votes': vote_status['total_votes'],
                'winning_maps': format_winning_map(vote_status['winning_maps'], default=nextmap)
            }
            formatted = msg.format(**subs)
            logger.debug("Broadcasting for %s seconds: %s", time_sec, formatted)
            ctl.set_broadcast(formatted) 
            time.sleep(int(time_sec)) 



if __name__ == "__main__":
    run()
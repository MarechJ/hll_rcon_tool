import os
import time
import logging
import random
from functools import partial
import json

import redis

from rcon.cache_utils import get_redis_pool
from rcon.extended_commands import Rcon, CommandFailedError
from rcon.settings import SERVER_INFO
from rcon.user_config import AutoBroadcasts
from rcon.audit import online_mods, get_registered_mods
from rcon.utils import (
    LONG_HUMAN_MAP_NAMES, 
    SHORT_HUMAN_MAP_NAMES, 
    NO_MOD_LONG_HUMAN_MAP_NAMES, 
    NO_MOD_SHORT_HUMAN_MAP_NAMES, 
    numbered_maps, 
    categorize_maps, 
    get_current_selection 
)
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
        return f'{default}'
    wins = winning_maps[:display_count]
    if display_count == 0:
        wins = winning_maps
    return ', '.join(f'{LONG_HUMAN_MAP_NAMES[m]} ({count} vote(s))' for m, count in wins)

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

def scrolling_votemap(rcon, winning_maps, repeat=20):
    vote_options = format_map_vote(rcon, "line", short_names=False)
    separator = '    *    '
    options = separator.join([vote_options] * repeat)
    instructions = os.getenv('VOTE_MAP_INSTRUCTIONS', 'To vote write the map number in the chat')
    repeat_instructions = max(int(len(options) / (len(instructions) + len(separator))), 1)
    instructions = separator.join([instructions] * repeat_instructions)

    winning_maps = format_winning_map(winning_maps, display_count=0, default='No votes recorded')
    repeat_winning_maps = max(int(len(options) / (len(winning_maps) + len(separator))), 1)
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
    return join_char.join(f"[{maps_to_numbers[m]}] {human_name_map[m]}" for m in selection)

def format_map_vote(rcon, format_type="line", short_names=True):
    selection = get_current_selection()
    if not selection:
        return "No votes possible"
    human_map = SHORT_HUMAN_MAP_NAMES if short_names else LONG_HUMAN_MAP_NAMES
    human_map_mod = NO_MOD_SHORT_HUMAN_MAP_NAMES if short_names else NO_MOD_LONG_HUMAN_MAP_NAMES
    vote_dict = numbered_maps(selection)
    maps_to_numbers = dict(zip(vote_dict.values(), vote_dict.keys()))
    items = [f"[{k}] {human_map.get(v, v)}"  for k, v in vote_dict.items()]
    if format_type == "line":
        return ' '.join(items)
    if format_type == "max_length":
        return format_by_line_length(items)
    if format_type == 'vertical':
        return '\n'.join(items)
    if format_type.startswith('by_mod'):
        categorized = categorize_maps(selection)
        off = join_vote_options(' ', categorized['offensive'], human_map_mod, maps_to_numbers)
        warfare = join_vote_options(' ', categorized['warfare'], human_map_mod, maps_to_numbers)
        if format_type == 'by_mod_line':
            return "OFFENSIVE: {} WARFARE: {}".format(off, warfare)
        if format_type == 'by_mod_vertical':
            return "OFFENSIVE:\n{}\nWARFARE:\n{}".format(off, warfare)
        if format_type == 'by_mod_split':
            return "OFFENSIVE: {}\nWARFARE: {}".format(off, warfare)
        if format_type == 'by_mod_vertical_all':
            return "OFFENSIVE:\n{}\nWARFARE:\n{}".format(
                join_vote_options('\n', categorized['offensive'], human_map_mod, maps_to_numbers),
                join_vote_options('\n', categorized['warfare'], human_map_mod, maps_to_numbers)
            )
    
    

def format_message(ctl, msg):
    get_vip_names = lambda: [d['name'] for d in ctl.get_vip_ids()]
    get_admin_names = lambda: [d['name'] for d in ctl.get_admin_ids()]
    get_owner_names = lambda: [d['name'] for d in ctl.get_admin_ids() if d['role'] == 'owner']
    get_senior_names = lambda: [d['name'] for d in ctl.get_admin_ids() if d['role'] == 'senior']
    get_junior_names = lambda: [d['name'] for d in ctl.get_admin_ids() if d['role'] == 'junior']
    vote_status = get_votes_status()
    nextmap = safe(ctl.get_next_map, "")()
    
    subs = {
        'nextmap': safe(ctl.get_next_map, "")(),
        'maprotation': ' -> '.join(safe(ctl.get_map_rotation, [])()),
        'servername': safe(ctl.get_name, "")(),
        #'onlineadmins': ', '.join(safe(ctl.get_online_admins, [])()),
        'admins': ','.join(safe(get_admin_names, [])()),
        'owners': ','.join(safe(get_owner_names, [])()),
        'seniors': ','.join(safe(get_senior_names, [])()),
        'juniors': ','.join(safe(get_junior_names, [])()),
        'vips': ', '.join(safe(get_vip_names, [])()),
        'randomvip': safe(lambda: random.choice(get_vip_names() or [""]), "")(),
        'votenextmap_line': safe(partial(format_map_vote, format_type='line'), '')(ctl),
        'votenextmap_noscroll': safe(partial(format_map_vote, format_type='max_length'), '')(ctl),
        'votenextmap_vertical': safe(partial(format_map_vote, format_type='vertical'), '')(ctl),
        'votenextmap_by_mod_line': safe(partial(format_map_vote, format_type='by_mod_line'), '')(ctl),
        'votenextmap_by_mod_vertical': safe(partial(format_map_vote, format_type='by_mod_vertical'), '')(ctl),
        'votenextmap_by_mod_vertical_all': safe(partial(format_map_vote, format_type='by_mod_vertical_all'), '')(ctl),
        'votenextmap_by_mod_split': safe(partial(format_map_vote, format_type='by_mod_split'), '')(ctl),
        'total_votes': vote_status['total_votes'],
        'winning_maps_short': format_winning_map(vote_status['winning_maps'], default=nextmap, display_count=2),
        'winning_maps_all': format_winning_map(vote_status['winning_maps'], default=nextmap, display_count=0),
        'scrolling_votemap': scrolling_votemap(ctl, vote_status['winning_maps'])
    }
    try: 
        return msg.format(**subs)
    except KeyError as e:
        logger.warning("Can't broadcast message correctly, variable does not exists %s", e)
        return msg

def run():
    # avoid circular import
    from rcon.extended_commands import Rcon

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
            
            formatted = format_message(ctl, msg)
            logger.debug("Broadcasting for %s seconds: %s", time_sec, formatted)
            try:
                ctl.set_broadcast(formatted) 
            except CommandFailedError:
                logger.exception("Unable to broadcast %s", msg)
            time.sleep(int(time_sec)) 



if __name__ == "__main__":
    run()

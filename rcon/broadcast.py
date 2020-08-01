import os
import time
import logging
import random

from rcon.settings import SERVER_INFO
from rcon.user_config import AutoBroadcasts
from functools import wraps

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


def format_message(ctl, msg):
    get_vip_names = lambda: [d['name'] for d in ctl.get_vip_ids()]
    get_admin_names = lambda: [d['name'] for d in ctl.get_admin_ids()]
    get_owner_names = lambda: [d['name'] for d in ctl.get_admin_ids() if d['role'] == 'owner']
    get_senior_names = lambda: [d['name'] for d in ctl.get_admin_ids() if d['role'] == 'senior']
    get_junior_names = lambda: [d['name'] for d in ctl.get_admin_ids() if d['role'] == 'junior']
    subs = {
        'nextmap': safe(ctl.get_next_map, "")(),
        'maprotation': ' -> '.join(safe(ctl.get_map_rotation, [])()),
        'servername': safe(ctl.get_name, "")(),
        'onlineadmins': ', '.join(safe(ctl.get_online_admins, [])()),
        'admins': ','.join(safe(get_admin_names, [])()),
        'owners': ','.join(safe(get_owner_names, [])()),
        'seniors': ','.join(safe(get_senior_names, [])()),
        'juniors': ','.join(safe(get_junior_names, [])()),
        'vips': ', '.join(safe(get_vip_names, [])()),
        'randomvip': safe(lambda: random.choice(get_vip_names() or [""]), "")()
    }
    return msg.format(**subs)

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
            formatted = format_message(ctl, msg)
            logger.debug("Broadcasting for %s seconds: %s", time_sec, formatted)
            ctl.set_broadcast(formatted) 
            time.sleep(int(time_sec)) 
        # Clear state in case next next iteration disables 
        ctl.set_broadcast('') 


if __name__ == "__main__":
    run()

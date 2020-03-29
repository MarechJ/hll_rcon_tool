import os
import time
import random

from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from rcon.models import init_db, enter_session
from rcon.user_config import get_user_config, set_user_config

if __name__ == '__main__':
    ctl = Rcon(
        SERVER_INFO
    )
    mount_path = os.getenv("BROADCAST_PATH", '')

    set_user_config('randomize_broadcast_available', False)
    
    if os.path.isfile(f"{mount_path}broadcasts.txt"):
        with open(f"{mount_path}broadcasts.txt") as f: 
            default_msgs = [l.split(' ', 1) for l in f]
            default_msgs = [m for m in default_msgs if len(m) == 2] # filtering out badly formated lines

        if type(default_msgs) is list:
            set_user_config('randomize_broadcast_available', True)

            while True:
                msgs = default_msgs.copy()

                if get_user_config('randomize_broadcast'):
                    random.shuffle(msgs)

                for time_sec, msg in msgs:
                    msg = msg.rstrip("\r\n").format(nextmap=ctl.get_next_map())
                    print(f"{time_sec} second(s): {msg}")
                    ctl.set_broadcast(msg) 
                    time.sleep(int(time_sec)) 
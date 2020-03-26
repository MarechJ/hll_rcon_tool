import os
import time
import random

from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
from rcon.user_config import get_user_config

if __name__ == '__main__':
    ctl = Rcon(
        SERVER_INFO
    )
    mount_path = os.getenv("BROADCAST_PATH", '')
    
    with open(f"{mount_path}broadcasts.txt") as f: 
        msgs = [l.split(' ', 1) for l in f]
        msgs = [m for m in msgs if len(m) == 2] # filtering out badly formated lines
 
    while True: 
        if get_user_config('RANDOMIZE_BROADCAST'):
            random.shuffle(msgs)

        for time_sec, msg in msgs:
            msg = msg.rstrip("\n").format(nextmap=ctl.get_next_map())
            print(f"{time_sec} second(s): {msg}")
            ctl.set_broadcast(msg) 
            time.sleep(int(time_sec)) 

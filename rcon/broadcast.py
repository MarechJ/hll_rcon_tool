import os
import time

from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO

if __name__ == '__main__':
    ctl = Rcon(
        SERVER_INFO
    )
    mount_path = os.getenv("BROADCAST_PATH", '')
    
    with open(f"{mount_path}broadcasts.txt") as f: 
        msgs = [l.split(' ', 1) for l in f]
        msgs = [m for m in msgs if len(m) == 2] # filtering out badly formated lines
 
    while True: 
        for time_sec, msg in msgs:
            if msg == '/nextmap\n':
                msg = "Next map: {}".format(ctl.get_next_map())
            print(f"{time_sec} second(s): {msg}")
            ctl.set_broadcast(msg) 
            time.sleep(int(time_sec)) 

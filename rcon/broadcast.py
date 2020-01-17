import os
import time

from rcon.commands import ServerCtl
from rcon.settings import SERVER_INFO

if __name__ == '__main__':
    ctl = ServerCtl(
        SERVER_INFO
    )
    mount_path = os.getenv("BROADCAST_PATH", '')
    
    with open(f"{mount_path}/broadcasts.txt") as f: 
        msgs = [l.split(' ', 1) for l in f] 
 
    while True: 
        for time_min, msg in msgs: 
            ctl.set_broadcast(msg) 
            time.sleep(int(time_min) * 60) 

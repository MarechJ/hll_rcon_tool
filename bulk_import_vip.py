from rcon.extended_commands import Rcon

IP = ""
PORT = 21010
PASSWORD = ""


rcon = Rcon({"host": IP, "port": int(PORT), "password": PASSWORD})

"""
vips.txt:

43434234234234234 The name of some guy
23495823034982342 Antoher dude
"""

with open("vips.txt") as f:
    for line in f:
        steamid, name = line.strip()
        rcon.do_add_vip(name=name, steam_id_64=steamid)
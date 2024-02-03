from rcon import broadcast
from rcon.rcon import get_rcon


# This test requires an actual connection to the game server
def test_smoke_all_variables():
    ctl = get_rcon()
    var_dict = broadcast._get_vars(ctl)

    for k in var_dict.keys():
        print(k, broadcast.format_message(ctl, f"{'{'}{k}{'}'}"))

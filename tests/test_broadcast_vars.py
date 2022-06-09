from rcon import broadcast
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO


# This test requires an actual connection to the game server
def test_smoke_all_variables():
    ctl = Rcon(SERVER_INFO)
    var_dict = broadcast._get_vars(ctl)

    for k in var_dict.keys():
        print(k, broadcast.format_message(ctl, f"{'{'}{k}{'}'}"))
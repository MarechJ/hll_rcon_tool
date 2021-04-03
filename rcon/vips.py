import datetime

from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO
from rcon.player_history import get_profiles


def get_prunable_vips(days_of_inactivity=30):
    rcon = RecordedRcon(SERVER_INFO)

    age_limit = datetime.datetime.now() - datetime.timedelta(days=days_of_inactivity)
    vips = rcon.get_vip_ids()
    vips_by_steam_id = {vip["steam_id_64"]: vip["name"] for vip in vips}
    profiles = get_profiles(list(vips_by_steam_id.keys()), 1)

    for player in profiles:
        try:
            last_session = player["sessions"][0]
        except IndexError:
            print(f"""
                VIP Name: {vips_by_steam_id[player["steam_id_64"]]}
                Last seen: N/A
                AKAs: {'  ||  '.join(n["name"] for n in player["names"])}
            """)
            continue
        last_session = last_session["start"] or last_session["end"] or last_session["created"]
        # TODO: Handle no sessions
        if  last_session < age_limit:
            print(f"""
                VIP Name: {vips_by_steam_id[player["steam_id_64"]]}
                Last seen: {last_session.isoformat()}
                AKAs: {'  ||  '.join(n["name"] for n in player["names"])}
            """)

 

def compare_vips():
    from rcon.commands import ServerCtl
    from rcon.extended_commands import invalidates, Rcon
    rcon_2 = Rcon({"host": "176.57.171.159", "port": 28316, "password": ""})
    rcon_1 = Rcon({"host": "37.187.25.13", "port": 27662, "password": ""})

    with invalidates(Rcon.get_vip_ids):
        vip_1 = rcon_1.get_vip_ids()
        vip_2 = rcon_2.get_vip_ids()

    for vip in vip_1:
        if vip not in vip_2:
            print(vip)
            rcon_2.do_add_vip(name=vip["name"], steam_id_64=vip["steam_id_64"])

    for vip in vip_2:
        if vip not in vip_1:
            print(vip)
            rcon_1.do_add_vip(name=vip["name"], steam_id_64=vip["steam_id_64"])
    #id_1 = set(vip_1)
    #id_2 = set(vip_2)

    #print(id_1.difference(id_2))
    #print(id_2.difference(id_1))


if __name__ == '__main__':
    #print(get_prunable_vips())
    compare_vips()

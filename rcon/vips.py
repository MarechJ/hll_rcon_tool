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


if __name__ == '__main__':
    #print(get_prunable_vips())
    light_get_vips_count(RecordedRcon(SERVER_INFO))

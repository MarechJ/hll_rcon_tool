from dataclasses import dataclass
from rcon.connection import HLLConnection

@dataclass
class Admin:
    steam_id_64: str
    role: str
    name: str

    
class ServerCtl:
    def __init__(self, config):
        self.conn = HLLConnection()
        self.conn.connect(
            config['host'],
            config['port'],
            config['password']
        )

    def _request(self, command: str):
        self.conn.send(command.encode())
        return self.conn.receive().decode()
    
    def _get(self, item, is_list=False):
        res = self._request(f"get {item}")
        
        if not is_list:
            return res
        
        res = res.split('\t')
        if res[-1] == '':
            # There's a trailin \t
            res = res[:-1]
        expected_len = int(res[0])
        actual_len = len(res) - 1 
        if expected_len != actual_len:
            raise RuntimeError(
                f"Server returned incomplete list,"
                f" expected {expected_len} got {actual_len}"
            )
        return res[1:]
        
    def get_name(self):
        return self._get("name")

    def get_map(self):
        # server adds a _RESTART suffix after the name when the map is
        # loading
        return self._get("map")

    def get_players(self):
        return self._get("players", True)

    def get_admin_ids(self):
        admins = []
        for admin in self._get("adminids", True):
            id_, role, name = admin.split(' ')
            admins.append(Admin(steam_id_64=id_, role=role, name=name[1:-1]))
        return admins
        
    def get_temp_bans(self):
        return self._get("tempbans", True)

    def get_permabans(self):
        return self._get("permabans", True)
    
    def get_team_switch_cooldown(self):
        return self._get("teamswitchcooldown")

    def get_autobalance_threshold(self):
        return self._get("autobalancethreshold")

    def get_map_rotation(self):
        return self._request('rotlist').split('\n')[:-1]

    def get_logs(self, since_min_ago, filter_=''):
        return self._request(f'showlog {since_min_ago}')
    
    def set_welcome_message(self, msg):
        return self._request(f"say {msg}")

    def set_map(self, map_name):
        return self._request(f"map {map_name}")

    def set_broadcast(self, msg):
        return self._request(f'broadcast "{msg}"')
    

if __name__ == '__main__':
    import os
    from rcon.settings import SERVER_INFO
    
    ctl = ServerCtl(
        SERVER_INFO
    )
    
    print(ctl.get_map())
    maps = ctl.get_map_rotation()
    #print(ctl.set_map(maps[2]))
    print(ctl.get_map())

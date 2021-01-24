import random
import os
import re
from datetime import datetime, timedelta
import logging
import socket
from rcon.cache_utils import ttl_cache, invalidates, get_redis_client
from rcon.commands import ServerCtl, CommandFailedError
from rcon.steam_utils import get_player_country_code, get_player_has_bans

STEAMID = "steam_id_64"
NAME = "name"
ROLE = "role"


logger = logging.getLogger(__name__)


class Rcon(ServerCtl):
    settings = (
        ('team_switch_cooldown', int),
        ('autobalance_threshold', int),
        ('idle_autokick_time', int), ('max_ping_autokick', int),
        ('queue_length', int), ('vip_slots_num', int)
    )
    slots_regexp = re.compile(r'^\d{1,3}/\d{2,3}$')
    map_regexp = re.compile(r'^(\w+_?)+$') 
    chat_regexp = re.compile(r'CHAT\[((Team)|(Unit))\]\[(.*)\(((Allies)|(Axis))/(\d+)\)\]: (.*)')
    player_info_pattern = r'(.*)\(((Allies)|(Axis))/(\d+)\)'
    player_info_regexp = re.compile(r'(.*)\(((Allies)|(Axis))/(\d+)\)')
    MAX_SERV_NAME_LEN = 1024  # I totally made up that number. Unable to test
    log_time_regexp = re.compile(".*\((\d+)\).*")

    def get_playerids(self, as_dict=False):
        raw_list = super().get_playerids()

        player_list = []
        player_dict = {}
        for playerinfo in raw_list:
            name, steamid = playerinfo.rsplit(':', 1)
            name = name[:-1]
            steamid = steamid[1:]
            player_dict[name] = steamid
            player_list.append((name, steamid))
        
        return player_dict if as_dict else player_list

    @ttl_cache(ttl=60 * 60 * 2, cache_falsy=False)
    def get_player_info(self, player):
        try:
            try:
                raw = super().get_player_info(player)
                name, steam_id_64 = raw.split('\n')
            except CommandFailedError:
                name = player
                steam_id_64 = self.get_playerids(as_dict=True).get(name)
            if not steam_id_64:
                return {}

            country = get_player_country_code(steam_id_64)
            steam_bans = get_player_has_bans(steam_id_64)

        except (CommandFailedError, ValueError):
            # Making that debug instead of exception as it's way to spammy
            logger.exception("Can't get player info for %s", player)
            # logger.exception("Can't get player info for %s", player)
            return {}
        name = name.split(": ", 1)[-1]
        steam_id = steam_id_64.split(": ", 1)[-1]
        if name != player:
            logger.error("get_player_info('%s') returned for a different name: %s %s", player, name, steam_id)
            return {}
        return {
            NAME: name,
            STEAMID: steam_id,
            'country': country,
            'steam_bans': steam_bans
        }

    @ttl_cache(ttl=60 * 60 * 24)
    def get_admin_ids(self):
        res = super().get_admin_ids()
        admins = []
        for item in res:
            steam_id_64, role, name = item.split(" ", 2)
            admins.append(
                {
                    STEAMID: steam_id_64,
                    NAME: name[1:-1],
                    ROLE: role
                }
            )
        return admins
        
    def get_online_console_admins(self):
        admins = self.get_admin_ids()
        players = self.get_players()
        online = []
        admins_ids = set(a['steam_id_64'] for a in admins)
        
        for player in players:
            if player['steam_id_64'] in admins_ids:
                online.append(player['name'])
        
        return online

    def do_add_admin(self, steam_id_64, role, name):
        with invalidates(Rcon.get_admin_ids):
            return super().do_add_admin(steam_id_64, role, name)

    def do_remove_admin(self, steam_id_64):
        with invalidates(Rcon.get_admin_ids):
            return super().do_remove_admin(steam_id_64)

    @ttl_cache(ttl=5)
    def get_players(self):
        # TODO refactor to use get_playerids. Also bacth call to steam API and find a way to cleverly cache the steam results
        names = super().get_players()
        players = []
        for n in names:
            player = {NAME: n}
            player.update(self.get_player_info(n))
            players.append(player)

        return players    

    @ttl_cache(ttl=60)
    def get_perma_bans(self):
        return super().get_perma_bans()

    @ttl_cache(ttl=60)
    def get_temp_bans(self):
        res = super().get_temp_bans()
        logger.debug(res)
        return res

    def _struct_ban(self, ban, type_):
        #name, time = ban.split(', banned on ')
        # '76561197984877751 : nickname "Dr.WeeD" banned for 2 hours on 2020.12.03-12.40.08 for "None" by admin "test"'
        steamd_id_64, rest = ban.split(" :", 1)
        name = None
        reason = None
        by = None

        if 'nickname' in rest:
            name = rest.split('" banned', 1)[0]
            name = name.split(' nickname "', 1)[-1]

        groups = re.match(".*(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}.\d{2}) (.*)", ban)
        if groups and groups.groups():
            date = groups.group(1)
            try:
                reason = groups.group(2)
            except:
                logger.error("Unable to extract reason from ban")
        by = ban.split(" by admin ", -1)[-1]

        return {
            'type': type_,
            'name': name,
            'steam_id_64': steamd_id_64,
            # TODO FIX
            'timestamp': None,
            'ban_time': date,
            'reason': reason,
            'by': by.replace('"', ""),
            'raw': ban
        }

    def get_bans(self):
        temp_bans = [
            self._struct_ban(b, 'temp')
            for b in self.get_temp_bans()
        ]
        bans = [
            self._struct_ban(b, 'perma')
            for b in self.get_perma_bans()
        ]
        # Most recent first
        bans.reverse()
        return temp_bans + bans


    def do_unban(self, steam_id_64):
        bans = self.get_bans()
        type_to_func = {
            "temp": self.do_remove_temp_ban,
            "perma": self.do_remove_perma_ban
        }
        for b in bans:
            if b.get("steam_id_64") == steam_id_64:
                type_to_func[b["type"]](b["raw"])
        

    @ttl_cache(ttl=60 * 60)
    def get_vip_ids(self):
        res = super().get_vip_ids()
        l = []

        for item in res:
            try:
                steam_id_64, name = item.split(" ", 1)
                name = name.replace('"', "")
                name = name.replace("\n", "")
                name = name.strip()
            except ValueError:
                self._reconnect()
                raise
            l.append(dict(zip((STEAMID, NAME), (steam_id_64, name))))

        return l

    def do_remove_vip(self, steam_id_64):
        with invalidates(Rcon.get_vip_ids):
            return super().do_remove_vip(steam_id_64)

    def do_add_vip(self, name, steam_id_64):
        with invalidates(Rcon.get_vip_ids):
            return super().do_add_vip(steam_id_64, name)

    @ttl_cache(ttl=60)
    def get_next_map(self):
        current = self.get_map()
        current = current.replace('_RESTART', '')
        rotation = self.get_map_rotation()
        next_id = rotation.index(current)
        next_id += 1
        if next_id == len(rotation):
            next_id = 0

        return rotation[next_id]

    def set_map(self, map_name):
        with invalidates(Rcon.get_map):
            res = super().set_map(map_name)
            if res != 'SUCCESS':
                raise CommandFailedError(res)

    @ttl_cache(ttl=20)
    def get_map(self):
        current_map = super().get_map()
        if not self.map_regexp.match(current_map):
            raise CommandFailedError("Server returned wrong data")
        return current_map

    @ttl_cache(ttl=60 * 60)
    def get_name(self):
        name = super().get_name()
        if len(name) > self.MAX_SERV_NAME_LEN:
            raise CommandFailedError("Server returned wrong data")
        return name

    @ttl_cache(ttl=60 * 60)
    def get_team_switch_cooldown(self):
        return int(super().get_team_switch_cooldown())

    def set_team_switch_cooldown(self, minutes):
        with invalidates(Rcon.get_team_switch_cooldown):
            return super().set_team_switch_cooldown(minutes)
    
    @ttl_cache(ttl=60 * 60)
    def get_autobalance_threshold(self):
        return int(super().get_autobalance_threshold())

    def set_autobalance_threshold(self, max_diff):
        with invalidates(Rcon.get_autobalance_threshold):
            return super().set_autobalance_threshold(max_diff)
    
    @ttl_cache(ttl=60 * 60)
    def get_idle_autokick_time(self):
        return int(super().get_idle_autokick_time())

    def set_idle_autokick_time(self, minutes):
        with invalidates(Rcon.get_idle_autokick_time):
            return super().set_idle_autokick_time(minutes)
    
    @ttl_cache(ttl=60 * 60)
    def get_max_ping_autokick(self):
        return int(super().get_max_ping_autokick())

    def set_max_ping_autokick(self, max_ms):
        with invalidates(Rcon.get_max_ping_autokick):
            return super().set_max_ping_autokick(max_ms)

    @ttl_cache(ttl=60 * 60)
    def get_queue_length(self):
        return int(super().get_queue_length())

    def set_queue_length(self, num):
        with invalidates(Rcon.get_queue_length):
            return super().set_queue_length(num)

    @ttl_cache(ttl=60 * 60)
    def get_vip_slots_num(self):
        return super().get_vip_slots_num()

    def set_vip_slots_num(self, num):
        with invalidates(Rcon.get_vip_slots_num):
            return super().set_vip_slots_num(num)

    def set_welcome_message(self, msg):
        red = get_redis_client()
        from rcon.broadcast import format_message
        formatted = format_message(self, msg)
        return super().set_welcome_message(formatted)

    def set_broadcast(self, msg):
        from rcon.broadcast import format_message
        formatted = format_message(self, msg)
        return super().set_broadcast(formatted)

    @ttl_cache(ttl=20)
    def get_slots(self):
        res = super().get_slots()
        if not self.slots_regexp.match(res):
            raise CommandFailedError("Server returned crap")
        return res

    @ttl_cache(ttl=5, cache_falsy=False)
    def get_status(self):
        slots = self.get_slots()
        return {
            'name': self.get_name(),
            'map': self.get_map(),
            'nb_players': slots,
            'short_name': os.getenv("SERVER_SHORT_NAME", None) or "HLL Rcon",
            'player_count': slots.split('/')[0]
        }

    @ttl_cache(ttl=60 * 60 * 24)
    def get_maps(self):
        return super().get_maps()

    def get_server_settings(self):
        settings = {}
        for name, type_ in self.settings:
            try:
                settings[name] = type_(getattr(self, f'get_{name}')())
            except: 
                logger.exception("Failed to retrieve settings %s", name)
                raise
        return settings


    def do_save_setting(self, name, value):
        if not name in dict(self.settings):
            raise ValueError(f"'{name}' can't be save with this method")

        return getattr(self, f'set_{name}')(value)

    def _convert_relative_time(self, from_, time_str):
        time, unit = time_str.split(' ')
        if unit == 'ms':
            return from_ - timedelta(milliseconds=int(time))
        if unit == 'sec':
            return from_ - timedelta(seconds=float(time))
        if unit == 'min':
            minutes, seconds = time.split(':')
            return from_ - timedelta(minutes=float(minutes), seconds=float(seconds))
        if unit == 'hours':
            hours, minutes, seconds = time.split(':')
            return from_ - timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds)
            )

    @staticmethod
    def _extract_time(time_str):
        groups = Rcon.log_time_regexp.match(time_str)
        if not groups:
            raise ValueError("Unable to extract time from '%s'", time_str)
        try:
            return datetime.fromtimestamp(int(groups.group(1)))
        except (ValueError, TypeError) as e:
            raise ValueError("Time '%s' is not a valid integer", time_str) from e


    @ttl_cache(ttl=10)
    def get_structured_logs(self, since_min_ago, filter_action=None, filter_player=None):
        try:
            raw = super().get_logs(since_min_ago)
        except socket.timeout:
            # The hll server just hangs when there are no logs for the requested time
            raw = ''

        return self.parse_logs(raw, filter_action, filter_player)

    @ttl_cache(ttl=60 * 60)
    def get_profanities(self):
        return super().get_profanities()

    def set_profanities(self, profanities):
        current = self.get_profanities()
        with invalidates(self.get_profanities):
            removed = set(current) - set(profanities)
            added = set(profanities) - set(current)
            if removed:
                self.do_unban_profanities(list(removed))
            if added:
                self.do_ban_profanities(list(added))
        
        return profanities

    def do_unban_profanities(self, profanities):
        if not isinstance(profanities, list):
            profanities = [profanities]
        with invalidates(self.get_profanities):
            return super().do_unban_profanities(','.join(profanities))

    def do_ban_profanities(self, profanities):
        if not isinstance(profanities, list):
            profanities = [profanities]
        with invalidates(self.get_profanities):
            return super().do_ban_profanities(','.join(profanities))

    def do_kick(self, player, reason):
        with invalidates(Rcon.get_players):
            return super().do_kick(player, reason)

    def do_temp_ban(self, player=None, steam_id_64=None, duration_hours=2, reason="", admin_name=""):
        if player and player in super().get_players():
            # When banning a player by steam id, if he is currently in game he won't be banned immedietly
            steam_id_64 = None
        with invalidates(Rcon.get_players, Rcon.get_temp_bans):
            return super().do_temp_ban(player, steam_id_64, duration_hours, reason, admin_name)

    def do_remove_temp_ban(self, ban_log):
        with invalidates(Rcon.get_temp_bans):
            return super().do_remove_temp_ban(ban_log)

    def do_remove_perma_ban(self, ban_log):
        with invalidates(Rcon.get_perma_bans):
            return super().do_remove_perma_ban(ban_log)

    def do_perma_ban(self, player=None, steam_id_64=None, reason="", admin_name=""):
        if player and player in super().get_players():
            # When banning a player by steam id, if he is currently in game he won't be banned immedietly
            steam_id_64 = None
        with invalidates(Rcon.get_players, Rcon.get_perma_bans):
            return super().do_perma_ban(player, steam_id_64, reason, admin_name)

    @ttl_cache(60 * 5)
    def get_map_rotation(self):
        l = super().get_map_rotation()

        for map_ in l:
            if not self.map_regexp.match(map_):
                raise CommandFailedError("Server return wrong data")
        return l

    def do_add_map_to_rotation(self, map_name):
        return self.do_add_maps_to_rotation([map_name])

    def do_remove_map_from_rotation(self, map_name):
        return self.do_remove_maps_from_rotation([map_name])

    def do_remove_maps_from_rotation(self, maps):
        with invalidates(Rcon.get_map_rotation):
            for map_name in maps:
                super().do_remove_map_from_rotation(map_name)
            return 'SUCCESS'

    def do_add_maps_to_rotation(self, maps):
        with invalidates(Rcon.get_map_rotation):
            for map_name in maps:
                super().do_add_map_to_rotation(map_name)
            return 'SUCCESS'

    def do_randomize_map_rotation(self, maps=None):
        maps = maps or self.get_maps()
        current = self.get_map_rotation()

        random.shuffle(maps)

        for m in maps:
            if m in current:
                self.do_remove_map_from_rotation(m)
            self.do_add_map_to_rotation(m)

        return maps

    def set_maprotation(self, rotation):
        if not rotation:
            raise CommandFailedError("Empty rotation")
        
        rotation = list(rotation)
        logger.info("Apply map rotation %s", rotation)
        
        with invalidates(Rcon.get_map_rotation):
            current = self.get_map_rotation()
            if rotation == current:
                logger.debug("Map rotation is the same, nothing to do")
                return current

            print(rotation, current)
            
            
            if len(current) == 1:
                logger.info("Current rotation is a single map")
                for idx, m in enumerate(rotation):
                    if m not in current:
                        self.do_add_map_to_rotation(m)
                    if m in current and idx != 0:
                        self.do_remove_map_from_rotation(m)
                        self.do_add_map_to_rotation(m)
                if current[0] not in rotation:
                    self.do_remove_map_from_rotation(m)
                return rotation

            first = rotation.pop(0)
            to_remove = set(current) - {first}
            if to_remove == set(current):
                self.do_add_map_to_rotation(first)

            self.do_remove_maps_from_rotation(to_remove)
            self.do_add_maps_to_rotation(rotation)

        return [first] + rotation


    @ttl_cache(ttl=60 * 2)
    def get_scoreboard(self, kill_logs, minutes=180, sort='ratio'):
        logs = kill_logs
        scoreboard = []
        for player in logs['players']:
            if not player:
                continue
            kills = 0
            death = 0
            for log in logs['logs']:
                if log['player_name'] == player:
                    kills += 1
                elif log['player2_name'] == player:
                    death += 1
            if kills == 0 and death == 0:
                continue
            scoreboard.append({ 
                'player': player,
                '(real) kills': kills,
                '(real) death': death,
                'ratio': kills / max(death, 1)
            })

        scoreboard = sorted(
            scoreboard, key=lambda o: o[sort], reverse=True
        )
        for o in scoreboard:
            o["ratio"] = "%.2f" % o["ratio"]

        return scoreboard

    @ttl_cache(ttl=60 * 2)
    def get_teamkills_boards(self, logs, sort='TK Minutes'):
        scoreboard = []
        for player in logs['players']:
            if not player:
                continue
            first_timestamp = float('inf')
            last_timestamp = 0
            tk = 0  
            death_by_tk = 0
            for log in logs['logs']:
                if log['player_name'] == player or log['player2_name'] == player:
                    first_timestamp = min(log['event_time'], first_timestamp)
                    last_timestamp = max(log['event_time'], last_timestamp)
                if log['type'] == 'TEAM KILL':
                    if log['player_name'] == player:
                        tk += 1
                    elif log['player2_name'] == player:
                        death_by_tk += 1
            if tk == 0 and death_by_tk == 0:
                continue
            scoreboard.append({ 
                'player': player,
                'Teamkills': tk,
                'Death by TK': death_by_tk,
                'Estimated play time (minutes)': (last_timestamp - first_timestamp) // 60,
                'TK Minutes': tk / max((last_timestamp - first_timestamp) // 60, 1)
            })

        scoreboard = sorted(
            scoreboard, key=lambda o: o[sort], reverse=True
        )
        for o in scoreboard:
            o['TK Minutes'] = "%.2f" % o['TK Minutes']

        return scoreboard

    @staticmethod
    def parse_logs(raw, filter_action=None, filter_player=None):
        synthetic_actions = ['CHAT[Allies]', 'CHAT[Axis]', 'CHAT', 'VOTE STARTED', "VOTE COMPLETED"]
        now = datetime.now()
        res = []
        actions = set()
        players = set()

        for line in raw.split('\n'):
            if not line:
                continue
            try:
                time, rest = line.split('] ', 1)
                #time = self._convert_relative_time(now, time[1:])
                time = Rcon._extract_time(time[1:])
                sub_content = action = player = player2 = weapon = steam_id_64_1 = steam_id_64_2 = None
                content = rest
                if rest.startswith('DISCONNECTED') or rest.startswith('CONNECTED'):
                    action, content = rest.split(' ', 1)
                elif rest.startswith('KILL') or rest.startswith('TEAM KILL'):
                    action, content = rest.split(': ', 1)
                elif rest.startswith('CHAT'):  
                    match = Rcon.chat_regexp.match(rest)
                    groups = match.groups()
                    scope = groups[0]
                    side = groups[4]
                    player = groups[3]
                    steam_id_64_1 = groups[-2]
                    action = f'CHAT[{side}][{scope}]'
                    sub_content = groups[-1]
                    #import ipdb; ipdb.set_trace()
                    content = f'{player}: {sub_content} ({steam_id_64_1})'
                elif rest.startswith('VOTE'): 
                    #[15:49 min (1606998428)] VOTE Player [[fr]ELsass_blitz] Started a vote of type (PVR_Kick_Abuse) against [拢儿]. VoteID: [1]
                    action = 'VOTE'
                    if rest.startswith('VOTE Player') and ' against ' in rest.lower():
                        action = 'VOTE STARTED'
                        groups = re.match(r'VOTE Player \[(.*)\].* against \[(.*)\]\. VoteID: \[\d+\]', rest)
                        player = groups[1]
                        player2 = groups[2]
                    elif rest.startswith('VOTE Player') and 'voted' in rest.lower():
                        groups = re.match(r'VOTE Player \[(.*)\] voted.*', rest)
                        player = groups[1]
                    elif "completed" in rest.lower():
                        action = "VOTE COMPLETED"
                    elif "kick" in rest.lower():
                        action = "VOTE COMPLETED"
                        groups = re.match(r'VOTE Vote Kick \{(.*)\}.*', rest)
                        player = groups[1]
                    else:
                        player = ""
                        player2 = None
                    sub_content = rest.split('VOTE')[-1]
                    content = rest.split('VOTE')[-1]
                else:
                    logger.error("Unkown type line: '%s'", line)
                    continue
                  
                if action in {'CONNECTED', 'DISCONNECTED'}:
                    player = content
                if action in {'KILL', 'TEAM KILL'}:
                    parts = re.split(Rcon.player_info_pattern + r' -> ', content, 1)
                    player = parts[1]
                    steam_id_64_1 = parts[-2]
                    player2 = parts[-1]
                    player2, weapon = player2.rsplit(' with ', 1)
                    player2, *_, steam_id_64_2 = Rcon.player_info_regexp.match(player2).groups()
               
                players.add(player)
                players.add(player2)
                actions.add(action)
            except:
                logger.exception("Invalid line: '%s'", line)
                continue
            if filter_action and not action.startswith(filter_action):
                continue
            if filter_player and filter_player not in line:
                continue

            res.append({
                'version': 1,
                'timestamp_ms': int(time.timestamp() * 1000),
                'relative_time_ms':  (time - now).total_seconds() * 1000,
                'raw': line,
                'line_without_time': rest,
                'action': action,
                'player': player,
                'steam_id_64_1': steam_id_64_1,
                'player2': player2,
                'steam_id_64_2': steam_id_64_2,
                'weapon': weapon,
                'message': content,
                'sub_content': sub_content,
            })

        res.reverse()
        return {
            'actions': list(actions) + synthetic_actions,
            'players': list(players),
            'logs': res
        }

if __name__ == '__main__':
    from rcon.settings import SERVER_INFO
    r = Rcon(SERVER_INFO)
    print(r.get_map_rotation())
    print(r.do_randomize_map_rotation())
    print(r.get_map_rotation())

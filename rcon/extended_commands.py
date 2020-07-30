import random
import os
import re
from datetime import datetime, timedelta
import logging
import socket
from rcon.cache_utils import ttl_cache, invalidates
from rcon.commands import ServerCtl, CommandFailedError
from rcon.broadcast import format_message

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
    chat_regexp = re.compile(r'CHAT\[((Team)|(Unit))\]\[(.*)\(((Allies)|(Axis))/(\d+)\)\]')
    player_info_regexp = re.compile(r'(.*)\(((Allies)|(Axis))/(\d+)\)')
    MAX_SERV_NAME_LEN = 1024  # I totally made up that number. Unable to test

    @ttl_cache(ttl=60 * 60 * 24, cache_falsy=False)
    def get_player_info(self, player):
        try:
            raw = super().get_player_info(player)
            name, steam_id_64 = raw.split('\n')
            if not steam_id_64:
                return {}
        except CommandFailedError:
            # Making that debug instead of exception as it's way to spammy
            logger.debug("Can't get player info for %s", player)
            # logger.exception("Can't get player info for %s", player)
            return {}
        return {
            NAME: name.split(": ", 1)[-1],
            STEAMID: steam_id_64.split(": ", 1)[-1],
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
        

    def get_online_admins(self):
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
        names = super().get_players()
        players = []
        for n in names:
            player = {NAME: n}
            player.update(self.get_player_info(n))
            players.append(player)

        return players    

    @ttl_cache(ttl=60 * 60)
    def get_perma_bans(self):
        return super().get_perma_bans()

    @ttl_cache(ttl=60 * 60)
    def get_temp_bans(self):
        return super().get_temp_bans()

    def _struct_ban(self, ban, type_):
        name, time = ban.split(', banned on ')
        return {
            'type': type_,
            'name': name,
            # TODO check which timezone the server is using. Assuming UTC here.
            'timestamp': datetime.strptime(time, "%Y.%m.%d-%H.%M.%S").timestamp(),
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

    @ttl_cache(ttl=60)
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
        formatted = format_message(self, msg)
        return super().set_welcome_message(formatted)

    def set_broadcast(self, msg):
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
        return {
            'name': self.get_name(),
            'map': self.get_map(),
            'nb_players': self.get_slots()
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

    @ttl_cache(ttl=10)
    def get_structured_logs(self, since_min_ago, filter_action=None, filter_player=None):
        try:
            raw = super().get_logs(since_min_ago)
        except socket.timeout:
            # The hll server just hangs when there are no logs for the requested time
            raw = ''

        synthetic_actions = ['CHAT[Allies]', 'CHAT[Axis]', 'CHAT']
        now = datetime.now()
        res = []
        actions = set()
        players = set()
        for line in raw.split('\n'):
            if not line:
                continue
            try:
                time, rest = line.split('] ', 1)
                time = self._convert_relative_time(now, time[1:])
                sub_content = action = player = player2 = weapon = steam_id_64_1 = steam_id_64_2 = None
                content = rest
                try:
                    # Bug: '[1:34:22 hours] DISCONNECTED ᚱ A V И E Ν : .',
                    action, content = rest.split(': ', 1)
                except ValueError:
                    action, content = rest.split(' ', 1)
                
                if match := self.chat_regexp.match(action):
                    groups = match.groups()
                    scope = groups[0]
                    side = groups[4]
                    player = groups[3]
                    steam_id_64_1 = groups[-1]
                    action = f'CHAT[{side}][{scope}]'
                    sub_content = content
                    content = f'{player}: {content} ({steam_id_64_1})'
                  
                if action in {'CONNECTED', 'DISCONNECTED'}:
                    player = content
                if action in {'KILL', 'TEAM KILL'}:
                    player, player2 = content.split(' -> ', 1)
                    player2, weapon = player2.split(' with ', 1)
                    player, *_, steam_id_64_1 = self.player_info_regexp.match(player).groups()
                    player2, *_, steam_id_64_2 = self.player_info_regexp.match(player2).groups()
               
                players.add(player)
                players.add(player2)
                actions.add(action)
            except:
                logger.exception("Invalid line: '%s'", line)
            if filter_action and not action.startswith(filter_action):
                continue
            if filter_player and filter_player not in line:
                continue

            res.append({
                'timestamp_ms': int(time.timestamp() * 1000),
                'relative_time_ms':  (time - now).total_seconds() * 1000,
                'raw': line,
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

    def do_kick(self, player, reason):
        with invalidates(Rcon.get_players):
            return super().do_kick(player, reason)

    def do_temp_ban(self, player, reason):
        with invalidates(Rcon.get_players, Rcon.get_temp_bans):
            return super().do_temp_ban(player, reason)

    def do_remove_temp_ban(self, ban_log):
        with invalidates(Rcon.get_temp_bans):
            return super().do_remove_temp_ban(ban_log)

    def do_remove_perma_ban(self, ban_log):
        with invalidates(Rcon.get_perma_bans):
            return super().do_remove_perma_ban(ban_log)

    def do_perma_ban(self, player, reason):
        with invalidates(Rcon.get_players, Rcon.get_perma_bans):
            return super().do_perma_ban(player, reason)


    @ttl_cache(60 * 5)
    def get_map_rotation(self):
        return super().get_map_rotation()

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
        first = rotation.pop(0)

        with invalidates(Rcon.get_map_rotation):
            current = set(self.get_map_rotation())
            self.do_remove_maps_from_rotation(current - set([first]))
            self.do_add_maps_to_rotation(rotation)

        return [first] + rotation

    @ttl_cache(ttl=60 * 2)
    def get_scoreboard(self, minutes=180, sort='ratio'):
        logs = self.get_structured_logs(minutes, 'KILL')
        scoreboard = []
        for player in logs['players']:
            if not player:
                continue
            kills = 0
            death = 0
            for log in logs['logs']:
                if log['player'] == player:
                    kills += 1
                elif log['player2'] == player:
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

if __name__ == '__main__':
    from rcon.settings import SERVER_INFO
    r = Rcon(SERVER_INFO)
    print(r.get_map_rotation())
    print(r.do_randomize_map_rotation())
    print(r.get_map_rotation())

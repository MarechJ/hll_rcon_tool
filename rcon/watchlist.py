from discord_webhook import DiscordWebhook, DiscordEmbed
from typing import List
import re

from rcon.models import PlayerSteamID, WatchList, enter_session
from rcon.config import get_config
from rcon.player_history import _get_set_player, get_player
from rcon.extended_commands import CommandFailedError, Rcon
from rcon.user_config import DiscordHookConfig
from rcon.game_logs import on_connected

def make_allowed_mentions(roles):
    allowed_mentions = {}
    for r in roles:
        if match := re.match(r'<@\!(\d+)>', r):
            allowed_mentions.setdefault("users", []).append(match.group(1))
        if match := re.match(r'<@&(\d+)>', r):
            allowed_mentions.setdefault("roles", []).append(match.group(1))
        if r == '@everyone' or r == '@here':
            allowed_mentions['parse'] = r.replace('@', '')
    print(allowed_mentions)
    allowed_mentions = {"parse": ["users"]}
    return allowed_mentions

def get_prepared_watch_hooks() -> List[DiscordWebhook]:
    config = DiscordHookConfig("watchlist")
    hooks = config.get_hooks()

    return [
        DiscordWebhook(
            url=hook.hook,
            allowed_mentions=make_allowed_mentions(hook.roles),
            content=" ".join(hook.roles),
        )
        for hook in hooks.hooks
    ]


@on_connected
def watchdog(rcon: Rcon, log):
    steam_id_64 = rcon.get_player_info(log["player"])['steam_id_64']
    watcher = PlayerWatch(steam_id_64)
    if watcher.is_watched():
        if hooks := get_prepared_watch_hooks():
            watched_player = watcher.get_watch()
            embed = DiscordEmbed(
                title=f'{log["player"]}  - {watched_player["steam_id_64"]}',
                description=f"""AKA: {", ".join(n["name"] for n in watched_player["names"])}
                
                Reason: __{watched_player['watchlist']['reason']}__
                """,
                color=242424,
            )
            for h in hooks:
                h.add_embed(embed)
                h.execute()


class PlayerWatch:
    def __init__(self, steam_id_64):
        self.steam_id_64 = steam_id_64

    def get_watch(self):
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if not player:
                return None
            return player.to_dict()

    def is_watched(self):
        watch = self.get_watch()
        return watch and watch["watchlist"]["is_watched"]

    def unwatch(self):
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if not player:
                raise CommandFailedError(
                    "Can't remove player to wathlist, player not found"
                )
            if player.watchlist:
                player.watchlist.is_watched = False

        return True

    def watch(self, reason, comment, player_name=""):
        with enter_session() as sess:
            player = _get_set_player(
                sess, player_name=player_name, steam_id_64=self.steam_id_64
            )
            if player.watchlist:
                player.watchlist.is_watched = True
            else:
                watch = WatchList(
                    steamid=player, comment=comment, reason=reason, is_watched=True
                )
                sess.add(watch)
                sess.commit()
                
        return True

from discord_webhook import DiscordWebhook, DiscordEmbed

from rcon.models import PlayerSteamID, WatchList, enter_session
from rcon.config import get_config
from rcon.player_history import get_player
from rcon.extended_commands import CommandFailedError, Rcon
from rcon.user_config import DiscordHookConfig
from rcon.game_logs import on_connected


def get_prepared_watch_hooks() -> DiscordWebhook:
    config = DiscordHookConfig("playerwatch")
    urls = config.get_hooks()
    roles = config.get_roles()
    if not urls:
        return None
    webhook = DiscordWebhook(url=urls, content=' '.join(roles))
    return webhook


@on_connected
def watchdog(rcon: Rcon, log):
    steam_id_64 = rcon.get_player_info(log['player'])
    watcher = PlayerWatch(steam_id_64)
    if watcher.is_watched():
        if hooks := get_prepared_watch_hooks():
            watched_player = watcher.get_watch()
            embed = DiscordEmbed(
                title=f'{log["player"]}  - {watched_player["steam_id_64"]}', 
                description=f"""AKA: {", ".join(n["name"] for n in watched_player)}
                
                Reason: __{watched_player['watchlist']['reason']}__
                """, 
                color=242424
            )
            hooks.add_embed(embed)
            hooks.execute()
        

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
        watch = self.get_watch(self.steam_id_64)
        return watch and watch["is_watched"]

    def unwatch(self):
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if not player:
                raise CommandFailedError(
                    "Can't remove player to wathlist, player not found"
                )
            if player.watchlist:
                player.watchlist.is_watched = False

    def watch(self, reason, comment):
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if player.watchlist:
                player.watchlist.is_watched = True
            else:
                WatchList(
                    steamid=player, comment=comment, reason=reason, is_watched=True
                )
                sess.add(WatchList)
                sess.commit()
    


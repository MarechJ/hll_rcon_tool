import re
from typing import List

from discord_webhook import DiscordEmbed

from rcon.config import get_config
from rcon.discord import get_prepared_discord_hooks
from rcon.extended_commands import CommandFailedError, Rcon
from rcon.game_logs import on_connected
from rcon.hooks import inject_player_ids
from rcon.models import PlayerSteamID, WatchList, enter_session
from rcon.player_history import _get_set_player, get_player


@on_connected
@inject_player_ids
def watchdog(rcon: Rcon, log, name, steam_id_64):
    watcher = PlayerWatch(steam_id_64)
    if watcher.is_watched():
        if hooks := get_prepared_discord_hooks("watchlist"):
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
        return watch and watch["watchlist"] and watch["watchlist"]["is_watched"]

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

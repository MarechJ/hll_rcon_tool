from datetime import datetime

from discord_webhook import DiscordEmbed

from rcon.discord import get_prepared_discord_hooks
from rcon.rcon import CommandFailedError, Rcon
from rcon.game_logs import on_connected
from rcon.hooks import inject_player_ids
from rcon.models import WatchList, enter_session
from rcon.player_history import _get_set_player, get_player
from rcon.types import PlayerProfileType


@on_connected
@inject_player_ids
def watchdog(rcon: Rcon, log, name: str, steam_id_64: str):
    watcher = PlayerWatch(steam_id_64)
    if watcher.is_watched():
        watcher.increment_watch()
        if hooks := get_prepared_discord_hooks("watchlist"):
            watched_player = watcher.get_watch()
            player_name = log["player"]

            if watched_player and watched_player["watchlist"]:
                timestamp = int(watched_player["watchlist"]["modified"].timestamp())
                steam_id_64 = watched_player["steam_id_64"]
                watched_by = watched_player["watchlist"]["by"]
                session_count = watched_player["watchlist"]["count"]
                reason = watched_player["watchlist"]["reason"]
                names = ", ".join(n["name"] for n in watched_player["names"])

                embed = DiscordEmbed(
                    title=f"{player_name}  - {steam_id_64}",
                    description=f"""AKA: {names}
                    
                    Watched on: <t:{timestamp}:f> (<t:{timestamp}:R>)
                    By: {watched_by}
                    Sessions Since Watch: {session_count}
                    Reason: __{reason}__
                    """,
                    color=242424,
                )
                for h in hooks:
                    h.add_embed(embed)
                    h.execute()


class PlayerWatch:
    def __init__(self, steam_id_64):
        self.steam_id_64 = steam_id_64

    def increment_watch(self) -> None:
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if not player:
                raise ValueError(
                    "Tried to increase the watch count of a non-existent player"
                )
            player.watchlist.count += 1

    def get_watch(self) -> PlayerProfileType | None:
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if not player:
                return None
            return player.to_dict()

    def is_watched(self) -> bool:
        watch = self.get_watch()
        return watch and watch["watchlist"] and watch["watchlist"]["is_watched"]

    def unwatch(self):
        with enter_session() as sess:
            player = get_player(sess, self.steam_id_64)
            if not player:
                raise CommandFailedError(
                    "Can't remove player to watchlist, player not found"
                )
            if player.watchlist:
                player.watchlist.modified = None
                player.watchlist.is_watched = False
                player.watchlist.count = 0

        return True

    def watch(self, reason: str, by: str, player_name: str = ""):
        with enter_session() as sess:
            player = _get_set_player(
                sess, player_name=player_name, steam_id_64=self.steam_id_64
            )
            if player.watchlist:
                player.watchlist.modified = datetime.utcnow()
                player.watchlist.is_watched = True
                player.watchlist.reason = reason
                player.watchlist.by = by
                player.watchlist.count = 0
            else:
                watch = WatchList(
                    steamid=player,
                    is_watched=True,
                    reason=reason,
                    by=by,
                    count=0,
                )
                sess.add(watch)

        return True

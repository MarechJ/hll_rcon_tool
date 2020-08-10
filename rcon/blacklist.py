import logging

from rcon.models import (
    enter_session, PlayerSteamID, BlacklistedPlayer, PlayerBanLog
)
from rcon.queries import get_player, get_set_player, add_player_action
from rcon.commands import CommandFailedError
from rcon.cache_utils import invalidates
from rcon.extended_commands import Rcon

logger = logging.getLogger(__name__)

def ban_if_blacklisted(rcon, steam_id_64, name):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        
        if not player:
            logger.error(
                "Can't check blacklist, player not found %s", steam_id_64)
            return

        if player.blacklist and player.blacklist.is_blacklisted:
            logger.warning("Player %s is blacklisted and has been banned, reason: %s", str(
                player), player.blacklist.reason)
            # TODO save author of blacklist
            add_player_action(action_type="PERMABAN", steamid=player, reason=player.blacklist.reason, by='BLACKLIST')
            try:
                ban_and_add_log(rcon, steam_id_64, name, player.blacklist.reason)
                sess.commit()
            except:
                logger.warning("Something went wrong banning player %s", str(player))


def add_player_to_blacklist(steam_id_64, reason, name=None):
    # TODO save author of blacklist
    with enter_session() as sess:
        player = get_set_player(sess, steam_id_64=steam_id_64, player_name=name)
        if not player:
            raise CommandFailedError(
                f"Player with steam id {steam_id_64} not found")

        if player.blacklist:
            if player.blacklist.is_blacklisted:
                logger.info("Player %s was already blacklisted with %s, updating reason to %s", str(
                    player), player.blacklist.reason, reason)
            player.blacklist.is_blacklisted = True
            player.blacklist.reason = reason
        else:
            logger.info("Player %s blacklisted for %s", str(player), reason)
            sess.add(
                BlacklistedPlayer(
                    steamid=player, is_blacklisted=True, reason=reason)
            )

        sess.commit()


def _find_and_remove_perma_bans_by_ban_log(rcon, ban_logs, sess):
    counter = 0
    perma_bans = rcon.get_perma_bans()
    for ban_log_entry in ban_logs:
        if ban_log_entry.ban_log:
            if ban_log_entry.ban_log in perma_bans:
                invalidates(Rcon.get_perma_bans)
                rcon.do_remove_perma_ban(ban_log_entry.ban_log, 'BLACKLIST_REMOVE', False)
                sess.delete(ban_log_entry)
                counter += 1
    return counter


def remove_player_from_blacklist(steam_id_64, rcon=None):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        if not player:
            raise CommandFailedError(
                f"Player with steam id {steam_id_64} not found")

        if not player.blacklist:
            raise CommandFailedError(f"Player {player} was not blacklisted")

        player.blacklist.is_blacklisted = False

        if rcon:
            _find_and_remove_perma_bans_by_ban_log(rcon, player.ban_logs, sess)

        sess.commit()


def remove_player_from_blacklist_using_ban_log(ban_log):
   with enter_session() as sess:
       players = sess.query(
         PlayerSteamID
       ).join(
         PlayerSteamID.ban_logs
       ).filter(
         PlayerBanLog.ban_log == ban_log
       ).all()

       if not players:
           return

       for player in players:
           remove_player_from_blacklist(player.steam_id_64)


def _get_players_who_are_not_blacklisted_but_have_ban_log(sess):
    return sess.query(
        PlayerSteamID
    ).join(
        PlayerSteamID.ban_logs
    ).join(
        PlayerSteamID.blacklist
    ).filter(
        PlayerBanLog.ban_log != None
    ).filter(
        BlacklistedPlayer.is_blacklisted == False
    ).all()


def _banned_unblacklisted_players(rcon, sess):
    return_list = []
    players = _get_players_who_are_not_blacklisted_but_have_ban_log(sess)

    perma_bans = rcon.get_perma_bans()
    for player in players:
        for ban_log in [ban_log.ban_log for ban_log in player.ban_logs]:
            if ban_log in perma_bans:
                return_list.append(player)
                break

    return return_list


def banned_unblacklisted_players(rcon):
    with enter_session() as sess:
        return [p.to_dict() for p in _banned_unblacklisted_players(rcon, sess)]


def unban_unblacklisted_players(rcon):
    counter = 0
    with enter_session() as sess:
        players = _banned_unblacklisted_players(rcon, sess)
        for player in players:
            counter += _find_and_remove_perma_bans_by_ban_log(rcon, player.ban_logs, sess)
    return counter


def add_ban_log(steam_id_64, ban_log):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)
        # a user can have multiple ban logs if banned on multiple servers
        player_ban_log = PlayerBanLog(steamid=player, ban_log=ban_log)
        player.ban_logs.append(player_ban_log)
        sess.add(player_ban_log)
        sess.commit()


def ban_and_add_log(rcon, steam_id_64, name, reason):
    _, ban_log = rcon.do_perma_ban_and_return_ban_log(name, reason)
    add_ban_log(steam_id_64, ban_log)

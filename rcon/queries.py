import logging
from rcon.models import enter_session, PlayerSteamID, PlayersAction, PlayerName

logger = logging.getLogger(__name__)

def get_player(sess, steam_id_64):
    return sess.query(PlayerSteamID).filter(
        PlayerSteamID.steam_id_64 == steam_id_64
    ).one_or_none()

def get_profiles(steam_ids, nb_sessions=0):
    with enter_session() as sess:
        players = sess.query(PlayerSteamID).filter(
            PlayerSteamID.steam_id_64.in_(steam_ids)
        ).all()

    return [p.to_dict(limit_sessions=nb_sessions) for p in players]

def get_set_player(sess, player_name, steam_id_64):
    player = get_player(sess, steam_id_64)
    if player is None:
        player = save_steam_id(sess, steam_id_64)
    if player_name:
        save_player_alias(sess, player, player_name)

    return player

def add_player_action(sess, action_type, steamid, reason, by):
    sess.add(
        PlayersAction(
            action_type=action_type.upper(),
            steamid=steamid,
            reason=reason,
            by=by
        )
    )

def save_steam_id(sess, steam_id_64):
    steamid = get_player(sess, steam_id_64)

    if not steamid:
        steamid = PlayerSteamID(steam_id_64=steam_id_64)
        sess.add(steamid)
        logger.info("Adding first time seen steamid %s", steam_id_64)
        sess.commit()

    return steamid

def save_player_alias(sess, steamid, player_name):
    name = sess.query(PlayerName).filter(
        PlayerName.name == player_name,
        PlayerName.steamid == steamid
    ).one_or_none()

    if not name:
        name = PlayerName(name=player_name, steamid=steamid)
        sess.add(name)
        logger.info("Adding player %s with new name %s",
                    steamid.steam_id_64, player_name)
        sess.commit()

    return name

def save_player(player_name, steam_id_64):
    with enter_session() as sess:
        steamid = save_steam_id(sess, steam_id_64)
        save_player_alias(sess, steamid, player_name)

def save_player_action(rcon, action_type, player_name, by, reason='', steam_id_64=None):
    with enter_session() as sess:
        if not steam_id_64:
            steam_id_64 = rcon.get_player_info(player_name)['steam_id_64']
        player = get_set_player(sess, player_name, steam_id_64)
        add_player_action(sess, action_type, player, reason, by)

def safe_save_player_action(rcon, action_type, player_name, by, reason=''):
    try:
        return save_player_action(rcon, action_type, player_name, by, reason)
    except Exception as e:
        logger.exception("Failed to record player action: %s %s", action_type, player_name)
        return False

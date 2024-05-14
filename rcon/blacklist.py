from datetime import datetime
import logging
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Sequence

from rcon.discord import dict_to_discord, send_to_discord_audit
from rcon.models import BlacklistSyncMethod, PlayerSteamID, Blacklist, BlacklistRecord, enter_session
from rcon.player_history import _get_set_player
from rcon.rcon import Rcon
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)

def get_server_number_mask():
    server_number = int(get_server_number())
    return 1 << (server_number - 1)

def get_player_blacklists(steam_id_64: str) -> list[BlacklistRecord]:
    with enter_session() as sess:
        stmt = (
            select(BlacklistRecord)
            .join(BlacklistRecord.steamid)
            .join(BlacklistRecord.blacklist)
            .filter(
                # Record must target the given player
                PlayerSteamID.steam_id_64 == steam_id_64,
                # Record must not have expired yet
                or_(
                    BlacklistRecord.expires_at.is_(None),
                    BlacklistRecord.expires_at < func.now(),
                ),
                # Blacklist must be enabled on the given server
                or_(
                    Blacklist.servers.is_(None),
                    Blacklist.servers.bitwise_and(get_server_number_mask())
                )
            )
        )
        blacklists = sess.execute(stmt).scalars().all()
        return blacklists

def is_player_blacklisted(steam_id_64: str) -> BlacklistRecord | None:
    """Determine whether a player is blacklisted, and return
    the blacklist record with the highest priority.

    Parameters
    ----------
    steam_id_64 : str
        The player's Steam64ID or Windows UUID

    Returns
    -------
    BlacklistRecord | None
        The blacklist record with highest priority if the
        player has unexpired blacklists. Returns `None` if
        no such record exists.
    """
    blacklists = get_player_blacklists(steam_id_64)
    
    if not blacklists:
        return
    
    return get_highest_priority_record(blacklists)
        
def is_higher_priority_record(record: BlacklistRecord, other: BlacklistRecord):
    # If both records expire at the same time, select the record
    # that was created most recently
    if record.expires_at == other.expires_at:
        return record.created_at > other.created_at
    
    # After having asserted that their expiration dates differ, if
    # either record has no expiration date, it must have the highest
    # priority
    elif record.expires_at is None:
        return True
    elif other.expires_at is None:
        return False
    
    # Otherwise, both have an expiration date. Select the record that
    # takes the longest to expire.
    return record.expires_at > other.expires_at

def get_highest_priority_record(records: Sequence[BlacklistRecord]):
    if not records:
        return None
    
    # Find record with highest priority
    highest = records[0]
    for record in records[1:]:
        if is_higher_priority_record(record, highest):
            highest = record
    return highest

def format_reason(reason: str):
    # TODO: Inject variables
    return reason

def apply_blacklist(rcon: Rcon, record: BlacklistRecord, player_name: str):
    try:
        player_id = record.steamid.steam_id_64
        reason = format_reason(record.reason)

        if record.blacklist.sync == BlacklistSyncMethod.KICK_ONLY:
            logger.info(
                "Player %s was kicked due to blacklist, reason: %s",
                player_name,
                reason,
            )
            rcon.kick(
                player_name=player_name,
                reason=reason,
                by=f"BLACKLIST: {record.admin_name}",
                player_id=player_id
            )
        
        elif record.expires_at:
            hours = round(record.expires_in().total_seconds() / (60 * 60))
            logger.info(
                "Player %s was banned until %s due to blacklist, reason: %s",
                player_name,
                record.expires_at,
                reason,
            )
            rcon.temp_ban(
                player_id=player_id,
                duration_hours=hours,
                reason=reason,
                by=f"BLACKLIST: {record.admin_name}",
            )

        else:
            logger.info(
                "Player %s was banned due to blacklist, reason: %s",
                player_name,
                reason,
            )
            rcon.perma_ban(
                player_id=player_id,
                reason=reason,
                by=f"BLACKLIST: {record.admin_name}",
            )

    except:
        send_to_discord_audit(
            message="Failed to apply blacklist, please check the logs and report the error",
            command_name="blacklist",
            by="ERROR",
        )
    
    else:
        try:
            send_to_discord_audit(
                message=f"{dict_to_discord(dict(player=player_name, reason=reason))}",
                command_name="blacklist",
                by="BLACKLIST",
            )
        except:
            logger.error("Unable to send blacklist to audit log")

def get_blacklist(sess: Session, blacklist_id: int):
    return sess.get(Blacklist, blacklist_id)

def blacklist_player(player_id: str, blacklist_id: int, reason: str, expires_at: datetime = None, admin_name: str = ""):
    with enter_session() as sess:
        player = _get_set_player(sess, player_id)
        if not player:
            raise RuntimeError("Unable to create player Steam ID, check the DB connection")

        blacklist = sess.get(Blacklist, blacklist_id)
        if not blacklist:
            raise ValueError("No blacklist found with ID %s" % blacklist_id)

        record = BlacklistRecord(
            steamid=player,
            blacklist=blacklist,
            reason=reason,
            expires_at=expires_at,
            admin_name=admin_name,
        )
        sess.add(record)
        # Should there be any integrity errors FSR, raise them now
        sess.flush()



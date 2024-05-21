from datetime import datetime, timedelta, timezone
from enum import IntEnum, auto
import orjson
import logging
import struct
from pydantic import BaseModel, field_validator
from pydantic.dataclasses import dataclass
from sqlalchemy import ScalarResult, func, or_, select
from sqlalchemy.orm import Session
from typing import Literal, Sequence, overload

from rcon.cache_utils import get_redis_client
from rcon.commands import CommandFailedError
from rcon.discord import dict_to_discord, send_to_discord_audit
from rcon.models import BlacklistSyncMethod, PlayerID, Blacklist, BlacklistRecord, enter_session
from rcon.player_history import _get_set_player
from rcon.rcon import Rcon, get_rcon
from rcon.types import BlacklistRecordType, BlacklistType
from rcon.utils import MISSING, get_server_number

logger = logging.getLogger(__name__)
red = get_redis_client()

SERVER_NUMBER = int(get_server_number())

def get_server_number_mask():
    server_number = SERVER_NUMBER
    return 1 << (server_number - 1)


@overload
def get_blacklist(sess: Session, blacklist_id: int, strict: Literal[True]) -> Blacklist: ...
@overload
def get_blacklist(sess: Session, blacklist_id: int, strict: Literal[False]) -> Blacklist | None: ...
@overload
def get_blacklist(sess: Session, blacklist_id: int, strict: bool = False) -> Blacklist | None: ...

def get_blacklist(sess: Session, blacklist_id: int, strict: bool = False) -> Blacklist | None:
    blacklist = sess.get(Blacklist, blacklist_id)
    if not blacklist and strict:
        raise CommandFailedError("No blacklist found with ID %s" % blacklist_id)
    return blacklist

@overload
def get_record(sess: Session, record_id: int, strict: Literal[True]) -> BlacklistRecord: ...
@overload
def get_record(sess: Session, record_id: int, strict: Literal[False]) -> BlacklistRecord | None: ...
@overload
def get_record(sess: Session, record_id: int, strict: bool = False) -> BlacklistRecord | None: ...

def get_record(sess: Session, record_id: int, strict: bool = False):
    record = sess.get(BlacklistRecord, record_id)
    if not record and strict:
        raise CommandFailedError("No record found with ID %s" % record_id)
    return record


def get_active_blacklist_records(sess: Session, blacklist_id: int):
    stmt = select(BlacklistRecord).filter(
        # Record must not have expired yet
        BlacklistRecord.blacklist_id == blacklist_id,
        or_(
            BlacklistRecord.expires_at.is_(None),
            BlacklistRecord.expires_at < func.now(),
        )
    )
    return sess.scalars(stmt)

def get_player_blacklist_records(
    sess: Session,
    player_id: str,
    include_expired = True,
    include_other_servers = True,
    exclude: set[int] = None
) -> ScalarResult[BlacklistRecord]:
    stmt = (
        select(BlacklistRecord)
        .join(BlacklistRecord.player)
        .join(BlacklistRecord.blacklist)
        .filter(
            # Record must target the given player
            PlayerID.player_id == player_id,
        )
    )

    if not include_expired:
        stmt = stmt.filter(
            # Record must not have expired yet
            or_(
                BlacklistRecord.expires_at.is_(None),
                BlacklistRecord.expires_at < func.now(),
            )
        )
    
    if not include_other_servers:
        stmt = stmt.filter(
            # Blacklist must be enabled on the given server
            or_(
                Blacklist.servers.is_(None),
                Blacklist.servers.bitwise_and(get_server_number_mask())
            )
        )
    
    if exclude:
        stmt = stmt.filter(
            BlacklistRecord.id.not_in(exclude)
        )

    blacklists = sess.scalars(stmt)
    return blacklists

def is_player_blacklisted(sess: Session, player_id: str, exclude: set[int] = {}) -> BlacklistRecord | None:
    """Determine whether a player is blacklisted, and return
    the blacklist record with the highest priority.

    Parameters
    ----------
    player_id : str
        The player's Steam64ID or Windows UUID
    exclude : set[int]
        An optional set of record IDs to exclude

    Returns
    -------
    BlacklistRecord | None
        The blacklist record with highest priority if the
        player has unexpired records. Returns `None` if no
        such record exists.
    """
    records = get_player_blacklist_records(
        sess,
        player_id,
        include_expired=False,
        include_other_servers=False,
        exclude=exclude,
    )
    
    if not records:
        return
    
    return get_highest_priority_record(records)

def is_higher_priority_record(record: BlacklistRecord, other: BlacklistRecord):
    return _is_higher_priority_record(
        record.created_at,
        record.expires_at,
        other.created_at,
        other.expires_at,
    )

def _is_higher_priority_record(
    record_created_at: datetime,
    record_expires_at: datetime | None,
    other_created_at: datetime,
    other_expires_at: datetime | None,
):
    # If both records expire at the same time, select the record
    # that was created most recently
    if record_expires_at == other_expires_at:
        return record_created_at > other_created_at
    
    # After having asserted that their expiration dates differ, if
    # either record has no expiration date, it must have the highest
    # priority
    elif record_expires_at is None:
        return True
    elif other_expires_at is None:
        return False
    
    # Otherwise, both have an expiration date. Select the record that
    # takes the longest to expire.
    return record_expires_at > other_expires_at

def get_highest_priority_record(records: Sequence[BlacklistRecord]):
    if not records:
        return None
    
    # Find record with highest priority
    highest = records[0]
    for record in records[1:]:
        if is_higher_priority_record(record, highest):
            highest = record
    return highest


def format_reason(record: BlacklistRecord):
    # TODO: Inject variables
    return record.reason

def round_timedelta_to_hours(td: timedelta):
    return min(round(td.total_seconds() / (60 * 60)), 1)

class BanState(IntEnum):
    NONE = 0
    TEMP = 1
    PERMA = 2

def get_ban_state_from_record(record: BlacklistRecord | BlacklistRecordType | None):
    if record is None:
        return BanState.NONE
    
    if isinstance(record, BlacklistRecord):
        sync = record.blacklist.sync
        expires_at = record.expires_at
        # is_other_servers = record.blacklist and SERVER_NUMBER not in record.blacklist.get_server_numbers()
        # is_expired = record.is_expired()
    else:
        sync = record["blacklist"]["sync"]
        expires_at = record["expires_at"]
        # is_other_servers = record["blacklist"] and SERVER_NUMBER not in record["blacklist"]["servers"]
        # is_expired = expires_at and expires_at < datetime.now(tz=timezone.utc)

    # if is_other_servers or is_expired:
    #     return BanState.NONE

    if sync == BlacklistSyncMethod.KICK_ONLY:
        return BanState.NONE
    elif expires_at is None:
        return BanState.PERMA
    else:
        return BanState.TEMP

def synchronize_ban(rcon: Rcon, player_id: str, new_record: BlacklistRecord | None, old_state: BanState):
    """Update a ban associated with a blacklist record.

    Be aware that this method does not verify whether the record has expired
    and/or does not affect the player on the current server.

    Parameters
    ----------
    rcon : Rcon
        A RCON client
    player_id : str
        The Steam64ID or Windows Store UUID of the player
    new_record : BlacklistRecord | None
        The updated blacklist record, or None if the record was removed
    old_state : BanState
        The current (and possibly outdated) state of the player's ban
    """
    new_state = get_ban_state_from_record(new_record)

    # Remove the existing ban if it will not be overwritten later
    if new_state != old_state:
        if old_state == BanState.TEMP:
            rcon.remove_temp_ban(player_id)
        elif old_state == BanState.PERMA:
            rcon.remove_perma_ban(player_id)

    # If there is no new record we are done and can return
    if new_record is None:
        return
    
    # Check whether the player is online (and grab their name)
    player_name = rcon.get_playerids(as_dict=True).get(player_id)
    is_online = player_name is not None

    if new_record.blacklist.sync != BlacklistSyncMethod.BAN_IMMEDIATELY and not is_online:
        # We only kick or ban the player once they come online, so
        # we don't need to do anything as of now.
        return
    
    apply_blacklist_punishment(
        rcon,
        new_record,
        player_id=player_id,
        player_name=player_name
    )

def apply_blacklist_punishment(
    rcon: Rcon,
    record: BlacklistRecord,
    player_id: str = None,
    player_name: str = None,
):
    try:
        state = get_ban_state_from_record(record)
        reason = format_reason(record)

        if player_id is None:
            player_id = record.player.player_id
        if player_name is None:
            player_name = record.player.names[0].name

        # Apply any bans/kicks
        match state:
            case BanState.NONE:
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
        
            case BanState.TEMP:
                hours = round_timedelta_to_hours(record.expires_at)
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

            case BanState.PERMA:
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
        return False
    
    else:
        try:
            send_to_discord_audit(
                message=f"{dict_to_discord(dict(player=player_name, reason=reason))}",
                command_name="blacklist",
                by="BLACKLIST",
            )
        except:
            logger.error("Unable to send blacklist to audit log")
        return True


def add_record_to_blacklist(player_id: str, blacklist_id: int, reason: str, expires_at: datetime | None = None, admin_name: str = ""):
    with enter_session() as sess:
        player = _get_set_player(sess, player_id)
        if not player:
            raise RuntimeError("Unable to create player Steam ID, check the DB connection")

        blacklist = get_blacklist(sess, blacklist_id, True)

        record = BlacklistRecord(
            steamid=player,
            blacklist=blacklist,
            reason=reason,
            expires_at=expires_at,
            admin_name=admin_name,
        )
        sess.add(record)
        sess.commit()

        res = record.to_dict()

    BlacklistCommandHandler.send(
        BlacklistCommand(
            command=BlacklistCommandType.CREATE_RECORD,
            server_mask=blacklist.servers,
            payload=BlacklistCreateRecordCommand(
                player_id=player_id,
                record_id=record.id,
            )
        )
    )
    
    return res

def edit_record_from_blacklist(
    record_id: int,
    blacklist_id: int = MISSING,
    reason: str = MISSING,
    expires_at: datetime | None = MISSING,
):
    with enter_session() as sess:
        record = get_record(sess, record_id, True)
        # Save old state
        old_record = record.to_dict()
        old_server_mask = record.blacklist.servers

        # Update attributes
        if blacklist_id != MISSING:
            record.blacklist_id = blacklist_id
        if reason != MISSING:
            record.reason = reason
        if expires_at != MISSING:
            record.expires_at = expires_at

        # Return if nothing was modified
        if not sess.is_modified(record):
            return old_record
        
        sess.commit()
        new_record = record.to_dict()

        # Check whether there were any changes made which would require resyncing a ban
        if (
            old_record["blacklist"]["sync"] != new_record["blacklist"]["sync"]
            or old_record["expires_at"] != new_record["expires_at"]
            or old_record["reason"] != new_record["reason"]
        ):
            # Merge old and new mask
            if old_server_mask is None or record.blacklist.servers is None:
                server_mask = (2 ** 32) - 1
            else:
                server_mask = old_server_mask | record.blacklist.servers
            
            # Send edit command to both old and new servers
            BlacklistCommandHandler.send(
                BlacklistCommand(
                    command=BlacklistCommandType.EDIT_RECORD,
                    server_mask=server_mask,
                    payload=BlacklistEditRecordCommand(
                        old_record=old_record
                    )
                )
            )
    
        return new_record

def remove_record_from_blacklist(record_id: str):
    with enter_session() as sess:
        record = get_record(sess, record_id)
        if not record:
            return False
        
        res = record.to_dict()

        sess.delete(record)
        sess.commit()
    
        if not record.is_expired():
            BlacklistCommandHandler.send(
                BlacklistCommand(
                    command=BlacklistCommandType.DELETE_RECORD,
                    server_mask=record.blacklist.servers,
                    payload=BlacklistDeleteRecordCommand(
                        old_record=res,
                    )
                )
            )

    return True



def create_blacklist(name: str, sync: BlacklistSyncMethod, servers: Sequence[int] | None):
    with enter_session() as sess:
        blacklist = Blacklist(
            name=name,
            sync=sync,
            servers=0,
        )
        blacklist.set_server_numbers(servers)
        sess.add(blacklist)
        sess.commit()
        return blacklist.to_dict()

def edit_blacklist(
    blacklist_id: int,
    name: str = MISSING,
    sync: BlacklistSyncMethod = MISSING,
    servers: Sequence[int] | None = MISSING
):
    with enter_session() as sess:
        blacklist = get_blacklist(sess, blacklist_id, True)
        # Save old state
        old_blacklist = blacklist.to_dict()
        old_server_mask = blacklist.servers

        # Update attributes
        if name != MISSING:
            blacklist.name = name
        if sync != MISSING:
            blacklist.sync = sync
        if servers != MISSING:
            blacklist.set_server_numbers(servers)

        # Return if nothing was modified
        if not sess.is_modified(blacklist):
            return old_blacklist
        
        sess.commit()
        new_blacklist = blacklist.to_dict()

        # Merge old and new mask
        if old_server_mask is None or blacklist.servers is None:
            server_mask = (2 ** 32) - 1
        else:
            server_mask = old_server_mask | blacklist.servers

        # Send edit command to both old and new servers
        BlacklistCommandHandler.send(
            BlacklistCommand(
                command=BlacklistCommandType.EDIT_LIST,
                server_mask=server_mask,
                payload=BlacklistEditListCommand(
                    old_blacklist=old_blacklist,
                    new_blacklist=new_blacklist
                )
            )
        )
    
        return new_blacklist

def delete_blacklist(blacklist_id: int):
    with enter_session() as sess:
        blacklist = get_blacklist(sess, blacklist_id)
        if not blacklist:
            return False
        
        res = blacklist.to_dict()

        # Since we're about to delete all records we need to
        # first capture all details needed to determine whether
        # the report had priority or not.
        records = get_active_blacklist_records(sess, blacklist_id)
        if not records:
            # If there's no active records on this blacklist we do not need to
            # worry about ban syncing and can just delete straight away.
            sess.delete(blacklist)
            sess.commit()
            return True
        
        # Iterate over all records and extract all necessary details
        # Format is {player_id: (r.created_at, r.expired_at)}
        banned_players: dict[str, tuple[datetime, datetime | None]] = {}
        for record in records:
            player_id = record.player.player_id

            # Players can be on the same blacklist multiple times. Here we check
            # whether we have already seen a record of that player and if it has
            # a lower priority, replace it.
            if other := banned_players.get(player_id):
                if not _is_higher_priority_record(
                    record.created_at,
                    record.expires_at,
                    *other
                ):
                    continue
                    
            banned_players[player_id] = (record.created_at, record.expires_at)

        sess.delete(blacklist)
        sess.commit()
    
        BlacklistCommandHandler.send(
            BlacklistCommand(
                command=BlacklistCommandType.DELETE_LIST,
                server_mask=blacklist.servers,
                payload=BlacklistDeleteRecordCommand(
                    blacklist=res,
                    banned_players=banned_players,
                )
            )
        )

        return True



def blacklist_or_ban(
    rcon: Rcon,
    blacklist_id: int | None,
    player_id: str,
    reason: str,
    expires_at: datetime | None = None,
    admin_name: str = "",
):
    # First try blacklisting the player if a blacklist_id is provided
    if blacklist_id is not None:
        try:
            # Note the "return"
            return add_record_to_blacklist(
                player_id=player_id,
                blacklist_id=blacklist_id,
                reason=reason,
                expires_at=expires_at,
                admin_name=admin_name,
            )
        except:
            logger.exception("Failed to blacklist player, banning them instead")

    if expires_at:
        rcon.temp_ban(
            player_id=player_id,
            reason=reason,
            duration_hours=round_timedelta_to_hours(
                expires_at - datetime.now(tz=timezone.utc)
            ),
            by=admin_name
        )
    else:
        rcon.perma_ban(
            player_id=player_id,
            reason=reason,
            by=admin_name
        )

def expire_all_player_blacklists(player_id: str):
    with enter_session() as sess:
        records = get_player_blacklist_records(
            sess,
            player_id=player_id,
            include_expired=False,
        )

        if not records:
            return
        
        expire_time = datetime.now(tz=timezone.utc)
        server_mask = 0

        for record in records:
            record.expires_at = expire_time
            server_mask |= record.blacklist.servers
        sess.commit()
        
        BlacklistCommandHandler.send(
            BlacklistCommand(
                command=BlacklistCommandType.EXPIRE_ALL,
                # server_mask=server_mask,
                server_mask=2**32 - 1,
            )
        )




class BlacklistCommandType(IntEnum):
    CREATE_RECORD = auto()
    EDIT_RECORD = auto()
    DELETE_RECORD = auto()
    # CREATE_LIST = auto()
    EDIT_LIST = auto()
    DELETE_LIST = auto()
    EXPIRE_ALL = auto()


class BlacklistCreateRecordCommand(BaseModel):
    player_id: str
    record_id: str

class BlacklistEditRecordCommand(BaseModel):
    old_record: BlacklistRecordType

class BlacklistDeleteRecordCommand(BaseModel):
    old_record: BlacklistRecordType

class BlacklistEditListCommand(BaseModel):
    old_blacklist: BlacklistType
    new_blacklist: BlacklistType

class BlacklistDeleteListCommand(BaseModel):
    blacklist: BlacklistType
    banned_players: dict[str, tuple[datetime, datetime | None]]
    perma_banned: list[str]

class BlacklistExpireAllCommand(BaseModel):
    player_id: str

@dataclass
class BlacklistCommand:
    command: BlacklistCommandType
    server_mask: int
    payload: dict

    @field_validator("server_mask", mode="before")
    @classmethod
    def convert_none_to_mask(cls, v: int | None) -> int:
        if v is None:
            # Create mask with the first 32 bits flipped
            return 2**32 - 1
        return v
    
    def encode(self):
        return struct.pack("II", self.command) + orjson.dumps(self.payload)
    
    @classmethod
    def decode(cls, data: bytes):
        split_at = struct.calcsize("II")

        command_id, server_mask = struct.unpack("II", data[:split_at])
        command = BlacklistCommandType(command_id)

        payload = orjson.loads(data[split_at:])
        
        return cls(command=command, server_mask=server_mask, payload=payload)

class BlacklistCommandHandler:
    CHANNEL = "blacklist"

    def __init__(self) -> None:
        self.pubsub = red.pubsub(ignore_subscribe_messages=True)
        self.rcon = get_rcon()
    
    def run(self):
        """Run the command handler loop. This is a blocking call."""

        # Subscribe to channel
        self.pubsub.subscribe(self.CHANNEL)
        
        # Start listening
        for message in self.pubsub.listen():
            try:
                data: bytes = message["data"]
                cmd = BlacklistCommand.decode(data)

                if not (cmd.server_mask & get_server_number_mask()):
                    # Command is not meant for this server
                    return

                try:
                    match cmd.command:
                        case BlacklistCommandType.CREATE_RECORD:
                            self.handle_create_record(
                                BlacklistCreateRecordCommand.model_validate(cmd.payload)
                            )
                        case BlacklistCommandType.EDIT_RECORD:
                            self.handle_edit_record(
                                BlacklistEditRecordCommand.model_validate(cmd.payload)
                            )
                        case BlacklistCommandType.DELETE_RECORD:
                            self.handle_delete_record(
                                BlacklistDeleteRecordCommand.model_validate(cmd.payload)
                            )
                        case BlacklistCommandType.EDIT_LIST:
                            self.handle_edit_list(
                                BlacklistEditListCommand.model_validate(cmd.payload)
                            )
                        case BlacklistCommandType.DELETE_LIST:
                            self.handle_delete_list(
                                BlacklistDeleteListCommand.model_validate(cmd.payload)
                            )
                        case BlacklistCommandType.EXPIRE_ALL:
                            self.handle_expire_all(
                                BlacklistExpireAllCommand.model_validate(cmd.payload)
                            )
                except:
                    logger.exception("Error whilst executing %s command with payload %s", cmd.command.name, cmd.payload)

            except:
                logger.exception("Failed to parse data %s", data)
    
    @staticmethod
    def send(cmd: BlacklistCommand):
        if cmd.server_mask == 0:
            # Command will be ignored by all servers, don't bother sending it.
            return
        
        red.publish(BlacklistCommandHandler.CHANNEL, cmd.encode())

    def handle_create_record(self, payload: BlacklistCreateRecordCommand):
        """Handle a new record being created."""
        with enter_session() as sess:
            new_record = is_player_blacklisted(sess, player_id=payload.player_id)
            
            if new_record is None or new_record.id != payload.record_id:
                # The new ban does not have priority, so we don't
                # have to do anything
                return
            
            old_record = is_player_blacklisted(
                sess,
                player_id=payload.player_id,
                exclude={payload.record_id}
            )

            synchronize_ban(
                self.rcon,
                player_id=payload.player_id,
                new_record=new_record,
                old_state=get_ban_state_from_record(old_record)
            )
            
    def handle_edit_record(self, payload: BlacklistEditRecordCommand):
        """Handle a record being edited.
        
        This simply will synchronize the player's ban if either the old
        or new ban had or has priority. If none of the attributes below
        were changed, this method may be avoided.
        - record.expires_at
        - record.reason
        - record.blacklist.sync"""
        old_record = payload.old_record
        with enter_session() as sess:
            new_record = is_player_blacklisted(sess, player_id=old_record["player_id"])

            # Check whether the old or new record had or has priority
            if (
                new_record.id == old_record["id"]
                or _is_higher_priority_record(
                    old_record["created_at"],
                    old_record["expires_at"],
                    new_record.created_at,
                    new_record.expires_at
                )
            ):
                synchronize_ban(
                    self.rcon,
                    player_id=old_record["player_id"],
                    new_record=new_record,
                    old_state=get_ban_state_from_record(old_record),
                )

    def handle_delete_record(self, payload: BlacklistDeleteRecordCommand):
        """Handle a record being deleted.
        
        This assumes that the record has not expired and is active on the current
        server.
        """
        old_record = payload.old_record
        with enter_session() as sess:
            new_record = is_player_blacklisted(sess, player_id=old_record["player_id"])

            if (
                # Check whether the removed record had a higher priority
                # than the current top record
                new_record is None
                or _is_higher_priority_record(
                    old_record["created_at"],
                    old_record["expires_at"],
                    new_record.created_at,
                    new_record.expires_at,
                )
            ):
                synchronize_ban(
                    self.rcon,
                    player_id=old_record["player_id"],
                    new_record=new_record,
                    old_state=get_ban_state_from_record(old_record),
                )
        
    def handle_edit_list(self, payload: BlacklistEditListCommand):
        """Handle a blacklist being edited.
        
        This must be called only on servers targeted by the blacklist
        before and/or after editing."""
        old_blacklist = payload.old_blacklist
        new_blacklist = payload.new_blacklist

        was_banned = (
            SERVER_NUMBER in old_blacklist["servers"]
            and old_blacklist["sync"] != BlacklistSyncMethod.KICK_ONLY
        )

        is_banned = (
            SERVER_NUMBER in new_blacklist["servers"]
            and new_blacklist["sync"] != BlacklistSyncMethod.KICK_ONLY
        )

        if was_banned != is_banned:
            with enter_session() as sess:
                records = get_active_blacklist_records(sess, new_blacklist["id"])
                for record in records:
                    if not was_banned:
                        old_state = BanState.NONE
                    elif record.expires_at is None:
                        old_state = BanState.PERMA
                    else:
                        old_state = BanState.TEMP

                    synchronize_ban(
                        rcon=self.rcon,
                        player_id=record.player.player_id,
                        new_record=record if is_banned else None,
                        old_state=old_state
                    )

    def handle_delete_list(self, payload: BlacklistDeleteListCommand):
        """Handle a blacklist being deleted.
        
        If no active records are on the given blacklist this method is obsolete.
        Assumes that the highest priority record for each player is included
        in the payload, but only if they are active. Expired records should be
        omitted."""
        if not payload.banned_players:
            return
        
        with enter_session() as sess:
            for player_id, (created_at, expires_at) in payload.banned_players.items():
                try:
                    new_record = is_player_blacklisted(sess, player_id)
                    if (
                        # Check whether the removed record had a higher priority
                        # than the current top record
                        new_record is None
                        or _is_higher_priority_record(
                            created_at,
                            expires_at,
                            new_record.created_at,
                            new_record.expires_at,
                        )
                    ):
                        if payload.blacklist["sync"] == BlacklistSyncMethod.KICK_ONLY:
                            old_state = BanState.NONE
                        elif expires_at is None:
                            old_state = BanState.PERMA
                        else:
                            old_state = BanState.TEMP
                        synchronize_ban(self.rcon, player_id, new_record, old_state)
                except:
                    logger.exception("Failed to synchronize ban for player %s after deleting blacklist", player_id)

    def handle_expire_all(self, payload: BlacklistExpireAllCommand):
        """Handle all of a player's active blacklist records being expired.
        
        Since this is typically done as a means of """
        self.rcon.remove_temp_ban(payload.player_id)
        self.rcon.remove_perma_ban(payload.player_id)

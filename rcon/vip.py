"""For managing VIP lists"""

# Unlike a blacklist that can be actioned with a KICK when a player joins;
# VIP has to be applied to the player before they join the server or it's pointless
# For this reason; VIP lists when they sync to the game server, need to ADD any new
# entries and REMOVE any expired/inactive entries and UNKNOWN entries (depending on sync method)

# They also need to periodically (on a timer) remove anyones VIP that has expired, these
# entries can remain on the list (or be purged) but need to be removed from the game server
# A sync needs to handle/reattempt errors since it must fetch a current list, and vipadd/vipdel
# potentially many entries

# Players can be on multiple VIP lists; but they will always get the highest expiration date
# amongst the list, and the entries applied to the server will be a UNION of all of the lists
# that are applied to the server; if you toggle a list, removal may or may not actually occur
# on the game server for any specific player; it depends if they still have an active/applicable
# record on a different list

# A VIP list can be configured to ignore extra VIP on the server (added from other sources like BM)
# or to remove people not on the list
# IF someone is ON the list regardless of this setting; and their VIP has expired, they'll be removed
# when the list is synced
# If the sync method of a list is REMOVE_UNKNOWN and a player ID has VIP on the game server but is not
# on ANY list that applies to the game server, their VIP is removed; otherwise they are ignored when
# the list is synced
# Multiple lists can apply to the server and they can have different sync methods; but users just need
# to pay attention and understand the system when managing lists; the default will be IGNORE_UNKNOWN
# so they will have to explicitly configure this, and most people will likely use a single list
# At not point will we automatically create records for players based on their existing VIP status
# on the game server


# Because command forwarding is weird and can fail, and you can only forward commands and not get info
# back, and one game server only knows about itself, and internal CRCON details
# when a list is edited, applied or removed from a server each CRCON instance is responsible for syncing
# the list to the game server, this is done via redis to notify the other game servers when list changes
# are made

# In the interest of making it easier for people to track info, VIP records can exist but not be active
# for a player to get VIP, their record must be active AND have an indefinite expiration date OR the
# expiration date needs to be in the future

# inactive OR expired VIP is removed when a list is synced

import os
import struct
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from enum import IntEnum, auto
from logging import getLogger
from typing import Iterable, Self, Sequence

import orjson
import redis
from dateutil import parser
from pydantic import BaseModel, field_validator
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from rcon.cache_utils import get_redis_client
from rcon.commands import CommandFailedError
from rcon.models import PlayerID, PlayerName, VipList, VipListRecord, enter_session
from rcon.player_history import _get_set_player, remove_accent, unaccent
from rcon.steam_utils import is_steam_id_64
from rcon.types import (
    VipListRecordEditType,
    VipListRecordType,
    VipListRecordTypeNoId,
    VipListSyncMethod,
    VipListType,
)
from rcon.utils import (
    MISSING,
    SERVER_NUMBER,
    MissingType,
    get_server_number_mask,
    strtobool,
)
from rcon.win_store_utils import is_windows_store_id

logger = getLogger(__name__)
red = get_redis_client()


DEFAULT_LIST_ID = 0
ALL_SERVERS_MASK = 2**32 - 1


def convert_old_style_vip_records(
    records: Iterable[str], vip_list_id: int = DEFAULT_LIST_ID
):
    errors = []

    timestamp = datetime.now(tz=timezone.utc)
    vips: list[VipListRecordTypeNoId] = []
    for idx, line in enumerate(records):
        idx += 1
        expiration_timestamp = None
        try:
            player_id, *name_chunks, possible_timestamp = line.strip().split()
            # No possible time stamp if name_chunks is empty (only a 2 element list)
            if not name_chunks:
                description = possible_timestamp
                possible_timestamp = None
            else:
                # This will collapse whitespace that was originally in a player's name
                description = " ".join(name_chunks)
                try:
                    expiration_timestamp = parser.parse(possible_timestamp)
                except:
                    logger.warning(
                        f"#{idx} Unable to parse {possible_timestamp=} for {description=} {player_id=}"
                    )
                    # The last chunk should be treated as part of the players name if it's not a valid date
                    description += possible_timestamp

            if not is_steam_id_64(player_id) and not is_windows_store_id(player_id):
                errors.append(
                    f"#{idx} {line} has an invalid player ID: `{player_id}`, expected a 17 digit steam id or a windows store id. {is_steam_id_64(player_id)=} {is_windows_store_id(player_id)=}"
                )
                continue
            if not description:
                errors.append(
                    f"#{idx}  {line} doesn't have a name attached to the player ID"
                )
                continue

            if expiration_timestamp and expiration_timestamp >= datetime(
                year=2100, month=1, day=1, tzinfo=timezone.utc
            ):
                expiration_timestamp = None

            vips.append(
                {
                    "vip_list_id": vip_list_id,
                    "player_id": player_id,
                    "admin_name": "CRCON",
                    "is_active": True,
                    "is_expired": (
                        expiration_timestamp <= timestamp
                        if expiration_timestamp
                        else True
                    ),
                    "expires_at": expiration_timestamp,
                    "description": description,
                    "notes": None,
                }
            )
        except Exception as e:
            errors.append(f"Error on line #{idx} {line}: {e}")

    if vips:
        logger.info(f"{len(vips)=}")
        bulk_add_vip_records(records=vips)

    return {
        "vips": vips,
        "errors": errors,
    }


def get_vip_lists(sess: Session) -> Sequence[VipList]:
    """Return all VIP lists ordered by ID"""
    return sess.scalars(select(VipList).order_by(VipList.id)).all()


def get_vip_lists_for_server(sess: Session, server_number: int) -> list[VipList]:
    """Return all VIP lists that apply to server_number"""
    applicable_lists: list[VipList] = []
    vip_lists = get_vip_lists(sess=sess)
    for lst in vip_lists:
        server_numbers = lst.get_server_numbers() or set([server_number])
        if server_number in server_numbers:
            applicable_lists.append(lst)

    return applicable_lists


def get_vip_list(
    sess: Session, vip_list_id: int, strict: bool = False
) -> VipList | None:
    """Return a specific VIP list if it exists"""
    vip_list = sess.get(VipList, vip_list_id)
    if not vip_list and strict:
        raise CommandFailedError(f"No vip list found with ID {vip_list_id}")
    return vip_list


def get_or_create_vip_list(
    sess: Session,
    vip_list_id: int,
    name: str,
    sync: VipListSyncMethod = VipListSyncMethod.IGNORE_UNKNOWN,
    servers: Sequence[int] | None = None,
) -> VipList:
    """Return a VIP list if it exists or create it with the parameters"""
    logger.info(f"{vip_list_id=}")
    vip_list = get_vip_list(sess=sess, vip_list_id=vip_list_id, strict=False)

    logger.info(f"{vip_list.to_dict() if vip_list else None}")
    if vip_list is None:
        new_list = create_vip_list(name=name, sync=sync, servers=servers)
        logger.info(f"{new_list=}")
        vip_list = get_vip_list(sess=sess, vip_list_id=new_list["id"], strict=False)
        logger.info(f"{vip_list.to_dict() if vip_list else None}")
        if vip_list is None:
            raise RuntimeError(
                "No VIP list found and an error occurred while creating a new one"
            )

    return vip_list


def create_vip_list(
    name: str, sync: VipListSyncMethod, servers: Sequence[int] | None
) -> VipListType:
    """Create a new VIP list"""
    with enter_session() as sess:
        vip_list = VipList(name=name, sync=sync)
        vip_list.set_server_numbers(servers)
        sess.add(vip_list)
        sess.commit()

        # VipLists are created empty; so no commands need to be sent to the handler
        return vip_list.to_dict()


def edit_vip_list(
    vip_list_id: int,
    name: str | MissingType = MISSING,
    sync: VipListSyncMethod | MissingType = MISSING,
    servers: Sequence[int] | MissingType = MISSING,
) -> VipListType | None:
    """Edit an existing VIP list if it exists"""
    with enter_session() as sess:
        # Let the exception bubble up to the API or wherever this was called
        # if we try to edit a list that doesn't exist
        vip_list = get_vip_list(sess=sess, vip_list_id=vip_list_id, strict=True)

        # Make type checking happy even though it's impossible to get here
        # if the list doesn't exist
        if not vip_list:
            return

        old_server_mask = vip_list.servers

        if name != MISSING:
            vip_list.name = name  # type: ignore
        if sync != MISSING:
            vip_list.sync = sync  # type: ignore
        if servers != MISSING:
            vip_list.set_server_numbers(servers)  # type: ignore

        if not sess.is_modified(vip_list):
            return vip_list.to_dict()

        # If either the new or old mask applied to all servers;
        # we have to send the command to every server
        if old_server_mask is None or vip_list.servers is None:
            server_mask = ALL_SERVERS_MASK
        # Otherwise OR the two masks together to find which servers
        # need to be notified
        else:
            server_mask = old_server_mask | vip_list.servers

        # Save our changes
        sess.commit()
        new_vip_list = vip_list.to_dict()

        VipListCommandHandler.send(
            VipListCommand(
                command=VipListCommandType.EDIT_LIST,
                server_mask=server_mask,
                payload=VipListEditListCommand(vip_list_id=vip_list.id).model_dump(),
            )
        )

        return new_vip_list


def delete_vip_list(vip_list_id: int) -> bool:
    """Delete an existing VipList, preventing the default list ID of 0 from being deleted

    When the list is deleted; all records on it are also deleted
    """

    if vip_list_id == DEFAULT_LIST_ID:
        raise ValueError("The default VIP list cannot be deleted")

    with enter_session() as sess:
        vip_list = get_vip_list(sess, vip_list_id=vip_list_id)
        if not vip_list:
            return False

        player_ids: set[str] = set()
        for record in vip_list.records:
            # Record the affected player IDs to send to the handler
            player_ids.add(record.player.player_id)
            sess.delete(record)

        sess.delete(vip_list)
        sess.commit()

        # This is handled on model validation; but it makes type checking unhappy
        server_mask = vip_list.servers or ALL_SERVERS_MASK

        VipListCommandHandler.send(
            VipListCommand(
                command=VipListCommandType.DELETE_LIST,
                server_mask=server_mask,
                payload=VipListDeleteListCommand(player_ids=player_ids).model_dump(),
            )
        )
        return True


def get_vip_record(
    sess: Session, record_id: int, strict: bool = False
) -> VipListRecord | None:
    """Return a specific VIP list record by ID if it exists"""
    record = sess.get(VipListRecord, record_id)
    if not record and strict:
        raise CommandFailedError(f"No vip list record found with ID {record_id}")
    return record


def bulk_add_vip_records(records: Iterable[VipListRecordTypeNoId]) -> None:
    with enter_session() as sess:
        for record in records:
            player = _get_set_player(sess, record["player_id"])
            if not player:
                raise RuntimeError(
                    "Unable to create PlayerID record, check the DB connection"
                )

            vip_list = get_vip_list(
                sess=sess, vip_list_id=record["vip_list_id"], strict=True
            )
            # Make type checking happy even though it's impossible to get here
            # if the list doesn't exist
            if not vip_list:
                return

            create_vip_record(
                sess=sess,
                player=player,
                vip_list=vip_list,
                description=record["description"],
                active=record["is_active"],
                expires_at=record["expires_at"],
                notes=record["notes"],
            )

            # Synchronize now since we deferred it earlier while editing
            VipListCommandHandler.send(
                VipListCommand(
                    command=VipListCommandType.SYNCH_GAME_SERVER,
                    server_mask=ALL_SERVERS_MASK,
                    payload=VipListSynchCommand().model_dump(),
                )
            )


def bulk_delete_vip_records(record_ids: Iterable[int]):
    with enter_session() as sess:
        for record_id in record_ids:
            delete_vip_list_record(record_id=record_id, synchronize=False)

        VipListCommandHandler.send(
            VipListCommand(
                command=VipListCommandType.SYNCH_GAME_SERVER,
                server_mask=ALL_SERVERS_MASK,
                payload=VipListSynchCommand().model_dump(),
            )
        )


def bulk_edit_vip_records(records: Iterable[VipListRecordEditType]) -> None:
    """Update all the provided records, deferring gameserver updates until the end"""
    with enter_session() as sess:
        for record in records:
            edit_vip_list_record(
                sess=sess,
                record_id=record["id"],
                vip_list_id=record.get("vip_list_id", MISSING),
                description=record.get("description", MISSING),
                active=record.get("is_active", MISSING),
                expires_at=record.get("expires_at", MISSING),
                notes=record.get("notes", MISSING),
                synchronize=False,
            )

    # Synchronize now since we deferred it earlier while editing
    VipListCommandHandler.send(
        VipListCommand(
            command=VipListCommandType.SYNCH_GAME_SERVER,
            server_mask=ALL_SERVERS_MASK,
            payload=VipListSynchCommand().model_dump(),
        )
    )


def create_vip_record(
    sess: Session,
    player: PlayerID,
    vip_list: VipList,
    description: str | None = None,
    active: bool = True,
    expires_at: datetime | None = None,
    notes: str | None = None,
    admin_name: str = "CRCON",
) -> VipListRecord:
    record = VipListRecord(
        admin_name=admin_name,
        active=active,
        description=description,
        notes=notes,
        expires_at=expires_at,
        player=player,
        vip_list=vip_list,
    )
    sess.add(record)
    logger.info(
        "Creating VIP list record for %s on list: name: %s ID: %s",
        player.player_id,
        vip_list.name,
        vip_list.id,
    )
    sess.commit()
    return record


def add_record_to_vip_list(
    player_id: str,
    vip_list_id: int,
    description: str | None = None,
    active: bool = True,
    expires_at: datetime | None = None,
    notes: str | None = None,
    admin_name: str = "CRCON",
) -> VipListRecordType | None:
    """Create and add a VipListRecord to the specified list"""
    with enter_session() as sess:
        player = _get_set_player(sess, player_id)
        if not player:
            raise RuntimeError(
                "Unable to create PlayerID record, check the DB connection"
            )

        vip_list = get_vip_list(sess=sess, vip_list_id=vip_list_id, strict=True)
        # Make type checking happy even though it's impossible to get here
        # if the list doesn't exist
        if not vip_list:
            return

        # The schema allows people to make as many records as they want for a
        # specific player, tracked by unique IDs; differentiated by expiration
        # date and then by creation date to sort priority
        record = create_vip_record(
            sess=sess,
            player=player,
            vip_list=vip_list,
            description=description,
            active=active,
            expires_at=expires_at,
            notes=notes,
            admin_name=admin_name,
        )

        res = record.to_dict()

        # This is handled on model validation; but it makes type checking unhappy
        server_mask = vip_list.servers or ALL_SERVERS_MASK

        VipListCommandHandler.send(
            VipListCommand(
                command=VipListCommandType.CREATE_RECORD,
                server_mask=server_mask,
                # No actual payload is needed; this command causes a resynch
                # with the game server
                payload=VipListCreateRecordCommand().model_dump(),
            )
        )

        return res


def edit_vip_list_record(
    record_id: int,
    vip_list_id: int | MissingType = MISSING,
    description: str | MissingType = MISSING,
    active: bool | MissingType = MISSING,
    expires_at: datetime | MissingType = MISSING,
    notes: str | MissingType = MISSING,
    admin_name: str = "CRCON",
    synchronize: bool = True,
    sess: Session | None = None,
) -> VipListRecordType | None:
    def _edit_vip_list_record(
        sess: Session,
        record_id: int,
        vip_list_id: int | MissingType = MISSING,
        description: str | MissingType = MISSING,
        active: bool | MissingType = MISSING,
        expires_at: datetime | MissingType = MISSING,
        notes: str | MissingType = MISSING,
        admin_name: str = "CRCON",
        synchronize: bool = True,
    ):
        active = strtobool(active)
        record = get_vip_record(sess=sess, record_id=record_id, strict=True)

        # Make type checking happy even though it's impossible to get here
        # if the list doesn't exist
        if not record:
            return

        old_record = record.to_dict()
        old_server_mask = record.vip_list.servers

        # Update any included attributes
        if vip_list_id != MISSING:
            record.vip_list_id = vip_list_id  # type: ignore
        if description != MISSING:
            record.description = description  # type: ignore
        if active != MISSING:
            record.active = active  # type: ignore
        if expires_at != MISSING:
            record.expires_at = expires_at  # type: ignore
        if notes != MISSING:
            record.notes = notes  # type: ignore

        # Update to the latest person who touched the record
        # or the default 'CRCON' if used internally
        record.admin_name = admin_name

        # Return if nothing was modified
        if not sess.is_modified(record):
            return old_record

        new_record = record.to_dict()

        # If either the new or old mask applied to all servers;
        # we have to send the command to every server
        if old_server_mask is None or record.vip_list.servers is None:
            server_mask = ALL_SERVERS_MASK
        # Otherwise OR the two masks together to find which servers
        # need to be notified
        else:
            server_mask = old_server_mask | record.vip_list.servers

        # Allow skipping synchronization; this is done on a 5 minute timer
        # anyway; and if we're doing bulk edits we can do all of the edits
        # and then manually trigger a synchronization
        if synchronize:
            VipListCommandHandler.send(
                VipListCommand(
                    command=VipListCommandType.EDIT_RECORD,
                    server_mask=server_mask,
                    # No actual payload is needed; this command causes a resynch
                    # with the game server
                    payload=VipListEditRecordCommand().model_dump(),
                )
            )

        return new_record

    if sess is None:
        with enter_session() as sess:
            return _edit_vip_list_record(
                sess=sess,
                record_id=record_id,
                vip_list_id=vip_list_id,
                description=description,
                active=active,
                expires_at=expires_at,
                notes=notes,
                admin_name=admin_name,
                synchronize=synchronize,
            )
    else:
        return _edit_vip_list_record(
            sess=sess,
            record_id=record_id,
            vip_list_id=vip_list_id,
            description=description,
            active=active,
            expires_at=expires_at,
            notes=notes,
            admin_name=admin_name,
            synchronize=synchronize,
        )


def delete_vip_list_record(record_id: int, synchronize: bool = True) -> bool:
    """Delete the specified VIP list record if it exists"""
    with enter_session() as sess:
        record = get_vip_record(sess=sess, record_id=record_id)

        if not record:
            return False

        player_id = record.player.player_id
        # This is handled on model validation; but it makes type checking unhappy
        server_mask = record.vip_list.servers or ALL_SERVERS_MASK
        sess.delete(record)
        sess.commit()

        if synchronize:
            # If we remove a record; that player may or may not still have VIP
            # from other lists, the handler will resynch with the game server
            # and handle it appropriately
            VipListCommandHandler.send(
                VipListCommand(
                    command=VipListCommandType.DELETE_RECORD,
                    server_mask=server_mask,
                    # No actual payload is needed; this command causes a resynch
                    # with the game server
                    payload=VipListDeleteRecordCommand(
                        player_id=player_id
                    ).model_dump(),
                )
            )

    return True


def get_highest_priority_records(vip_list_id: int) -> dict[str, VipListRecordType]:
    """They shouldn't; but a player can have multiple records on a list

    Get all the records for a list and return the top record for each player by player ID
    """
    records_by_player: defaultdict[str, list[VipListRecord]] = defaultdict(list)
    top_record_by_player: dict[str, VipListRecordType] = {}
    with enter_session() as sess:
        vip_list = get_vip_list(sess=sess, vip_list_id=vip_list_id)

        if not vip_list:
            return top_record_by_player

        for record in vip_list.records:
            records_by_player[record.player.player_id].append(record)

        for player_id, records in records_by_player.items():
            top_record = get_highest_priority_record(records=records)
            if top_record:
                top_record_by_player[player_id] = top_record.to_dict()

        return top_record_by_player


def get_vip_status_for_player_ids(player_ids: set[str]) -> dict[str, VipListRecordType]:
    records_by_player: defaultdict[str, list[VipListRecord]] = defaultdict(list)
    top_record_by_player: dict[str, VipListRecordType] = {}
    with enter_session() as sess:
        stmt = (
            select(VipListRecord)
            .join(VipListRecord.player)
            .filter(PlayerID.player_id.in_(player_ids))
        )
        server_records = sess.execute(stmt).scalars().all()
        # A player can have multiple records; group by player
        # # TODO: There's probably some SQL we can write to offload this to postgres
        # but for now do it in Python
        for record in server_records:
            records_by_player[record.player.player_id].append(record)

        for player_id, records in records_by_player.items():
            top_record = get_highest_priority_record(records=records)
            if top_record:
                top_record_by_player[player_id] = top_record.to_dict()

        return top_record_by_player


def get_active_vip_records(sess: Session, vip_list_id: int) -> Sequence[VipListRecord]:
    """Return all VipListRecords on a list that are flagged as active and haven't expired"""
    stmt = (
        select(VipListRecord)
        .filter(VipListRecord.vip_list_id == vip_list_id)
        # Record must not have expired yet and be marked as active
        .filter(VipListRecord.active == True)
        .filter(
            or_(
                VipListRecord.expires_at.is_(None),
                VipListRecord.expires_at > func.now(),
            )
        )
    )

    return sess.scalars(stmt).all()


def get_inactive_vip_records(
    sess: Session, vip_list_id: int
) -> Sequence[VipListRecord]:
    """Return all VipListRecords on a list that are either inactive or expired

    Expired records aren't immediately marked as inactive; the next time the list
    is reviewed (on a timer) it will be marked as inactive if it's expired
    """
    stmt = select(VipListRecord).filter(
        # Record must not have expired yet and be marked as active
        VipListRecord.vip_list_id == vip_list_id,
        or_(
            VipListRecord.active == False,
            VipListRecord.expires_at <= func.now(),
        ),
    )
    return sess.scalars(stmt).all()


def get_player_vip_list_records(
    sess: Session,
    player_id: str,
    include_expired: bool = True,
    include_inactive: bool = True,
    include_other_servers=True,
    exclude: set[int] | None = None,
) -> Sequence[VipListRecord]:
    """Return all VipListRecords associated with player_id based on the criteria"""
    stmt = (
        select(VipListRecord)
        .join(VipListRecord.player)
        .join(VipListRecord.vip_list)
        .filter(PlayerID.player_id == player_id)
    )

    if not include_inactive:
        stmt = stmt.filter(VipListRecord.active == True)

    if not include_expired:
        stmt = stmt.filter(
            or_(
                VipListRecord.expires_at.is_(None),
                VipListRecord.expires_at > func.now(),
            )
        )

    if not include_other_servers:
        stmt = stmt.filter(
            or_(
                # If there is no mask; the list applies to every server
                VipList.servers.is_(None),
                # Make sure the list applies to this specific server, i.e. there is a 1
                # in the mask position for this server number
                VipList.servers.bitwise_and(get_server_number_mask()) != 0,
            )
        )

    if exclude:
        stmt = stmt.filter(VipListRecord.id.not_in(exclude))

    return sess.scalars(stmt).all()


def search_vip_list_records(
    sess: Session,
    player_id: str | None = None,
    admin_name: str | None = None,
    active: bool | None = None,
    description_or_player_name: str | None = None,
    notes: str | None = None,
    email: str | None = None,
    discord_id: str | None = None,
    vip_list_id: int | None = None,
    exclude_expired: bool = False,
    page_size: int = 50,
    page: int = 1,
) -> tuple[Sequence[VipListRecord], int]:
    page_size = int(page_size)
    page = int(page)

    """Filter VIP list records by the criteria/page; returning the page records and  total number of records"""
    if page <= 0:
        raise ValueError("page needs to be >= 1")
    if page_size <= 0:
        raise ValueError("page_size needs to be >= 1")

    filters = []

    if player_id:
        filters.append(PlayerID.player_id == player_id)
    if admin_name:
        clean_admin_name = remove_accent(admin_name)
        filters.append(
            unaccent(VipListRecord.admin_name).ilike(f"%{clean_admin_name}%")
        )
        logger.info(f"{admin_name=}")
    if active:
        filters.append(VipListRecord.active == True)
    if description_or_player_name:
        clean_description = remove_accent(description_or_player_name)
        filters.append(
            or_(
                unaccent(VipListRecord.description).ilike(f"%{clean_description}%"),
                PlayerID.names.any(
                    unaccent(PlayerName.name).ilike(f"%{clean_description}%")
                ),
            )
        )
    if notes:
        clean_notes = remove_accent(notes)
        filters.append(unaccent(VipListRecord.notes).ilike(f"%{clean_notes}%"))
    if vip_list_id is not None:
        filters.append(VipListRecord.vip_list_id == vip_list_id)
    if exclude_expired:
        filters.append(
            or_(
                VipListRecord.expires_at.is_(None),
                VipListRecord.expires_at > func.now(),
            )
        )

    # Calculate the total records to return so API consumers can paginate properly
    total = sess.execute(
        select(func.count(VipListRecord.id)).join(VipListRecord.player).filter(*filters)
    ).scalar_one()

    stmt = (
        select(VipListRecord)
        .join(VipListRecord.player)
        .filter(*filters)
        .order_by(VipListRecord.created_at.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
        .options(selectinload(VipListRecord.vip_list))
        .options(selectinload(VipListRecord.player).selectinload(PlayerID.names))
        .options(selectinload(VipListRecord.player).selectinload(PlayerID.steaminfo))
    )
    return sess.scalars(stmt).all(), total


def get_all_records_for_server(
    sess: Session, server_number: int
) -> Sequence[VipListRecord]:
    """Return all VipListRecords for the indicated server"""
    vip_list_ids = [
        v.id for v in get_vip_lists_for_server(sess=sess, server_number=server_number)
    ]
    stmt = select(VipListRecord).where(VipListRecord.vip_list_id.in_(vip_list_ids))
    return sess.execute(stmt).scalars().all()


def is_player_vip_by_records(
    records: Iterable[VipListRecord], timestamp: datetime
) -> bool:
    """Return if the player should have VIP based on the provided records"""
    if any(
        record.active and (not record.expires_at or record.expires_at > timestamp)
        for record in records
    ):
        return True
    return False


def is_player_vip_by_query(
    sess: Session, player_id: str, exclude: set[int] | None = None
) -> VipListRecord | None:
    """Check if a player has current VIP from any list; not the game server"""

    # The player may or may not currently have VIP on the server; this just
    # determines if they *should* have VIP based on our list
    # Updating the game server will be handled when the list is synchronized
    records = get_player_vip_list_records(
        sess=sess,
        player_id=player_id,
        include_expired=False,
        include_inactive=False,
        # Need to exclude other game servers; doesn't matter if they have VIP there or not
        include_other_servers=False,
        exclude=exclude,
    )

    if not records:
        return

    # A player could have entries on multiple lists; get the most relevant one
    return get_highest_priority_record(records)


def is_higher_priority_record(record: VipListRecord, other: VipListRecord) -> bool:
    """Return True if the first record is higher priority or False if the other is"""

    def _is_higher_priority_record(
        record_created_at: datetime,
        record_expires_at: datetime | None,
        other_created_at: datetime,
        other_expires_at: datetime | None,
    ) -> bool:
        """Return True if the first record is higher priority or False if the other is"""
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

    return _is_higher_priority_record(
        record.created_at,
        record.expires_at,
        other.created_at,
        other.expires_at,
    )


def get_highest_priority_record(
    records: Sequence[VipListRecord],
) -> VipListRecord | None:
    """Return the highest priority VIP record amongst 0 or more records or None

    A record is higher priority if it either expires further in the future, or
    for ties was created more recently
    """
    if not records:
        return None

    # Find record with highest priority
    highest = records[0]
    for record in records[1:]:
        if is_higher_priority_record(record, highest):
            highest = record
    return highest


def inactivate_expired_records():
    """Mark all expired VipListRecords as inactive and cause a resynch

    This is run periodically on a cron job timer
    """
    logger.info(
        "Checking for expired/inactive VIP records since %s",
        datetime.now(tz=timezone.utc),
    )
    with enter_session() as sess:
        stmt = select(VipListRecord).filter(
            and_(
                VipListRecord.expires_at.is_not(None),
                VipListRecord.expires_at <= func.now(),
            )
        )
        records = sess.execute(stmt).scalars().all()
        # TODO: should probably do a bulk update here
        for record in records:
            logger.info(
                "Deactivating %s expired at: %s",
                record.player.player_id,
                record.expires_at,
            )
            record.active = False
        sess.commit()

    VipListCommandHandler.send(
        VipListCommand(
            command=VipListCommandType.SYNCH_GAME_SERVER,
            server_mask=ALL_SERVERS_MASK,
            payload=VipListSynchCommand().model_dump(),
        )
    )


def extend_vip_duration(
    record_id: int, duration: timedelta | int
) -> VipListRecordType | None:
    """Extend a temporary VIP record by duration; does nothing to indefinite VIP"""
    with enter_session() as sess:
        record = get_vip_record(sess=sess, record_id=record_id, strict=False)
        if not record:
            return

        # Do nothing; they already have indefinite VIP and the record should
        # be edited if someone wants to change from indefinite -> expiring
        if record.expires_at is None:
            return record.to_dict()

        if isinstance(duration, int):
            extend = timedelta(seconds=duration)
        elif isinstance(duration, timedelta):
            extend = duration
        else:
            raise ValueError(
                f"{duration} must be either a timedelta or an int quantity of seconds"
            )

        record.expires_at += extend
        modified_record = record.to_dict()

        # This is handled on model validation; but it makes type checking unhappy
        server_mask = record.vip_list.servers or ALL_SERVERS_MASK

        # This is effectively an edit even though you can only lengthen
        # the amount of VIP time someone has
        VipListCommandHandler.send(
            VipListCommand(
                command=VipListCommandType.EDIT_RECORD,
                server_mask=server_mask,
                # No actual payload is needed; this command causes a resynch
                # with the game server
                payload=VipListEditRecordCommand().model_dump(),
            )
        )

    return modified_record


def revoke_all_vip(player_id: str):
    """Mark all VIP records for player_id inactive and then resynch with the game server"""
    with enter_session() as sess:
        records = get_player_vip_list_records(
            sess=sess, player_id=player_id, include_other_servers=False
        )
        for record in records:
            record.active = False

        # Cause a resynch with the game server since we've modified records
        VipListCommandHandler.send(
            VipListCommand(
                command=VipListCommandType.REVOKE_VIP,
                server_mask=ALL_SERVERS_MASK,
                # No actual payload is needed; this command causes a resynch
                # with the game server
                payload=VipListRevokeAllCommand().model_dump(),
            )
        )


def synchronize_with_game_server(server_number: int, rcon=None):
    """Compare the game server with applicable lists and add/remove/update VIPs

    Inactive or expired entries will be removed from the game server
    Unknown entries (VIP on the game server; not on any applicable list)
    will be removed unless ANY applicable list sync method is IGNORE_UNKNOWN
    """
    if rcon is None:
        # Avoid circular imports
        from rcon.api_commands import get_rcon_api

        rcon = get_rcon_api()

    timestamp = datetime.now(tz=timezone.utc)
    game_server_vips: dict[str, str] = {
        vip["player_id"]: vip["name"] for vip in rcon.get_vip_ids()
    }
    logger.info("%s players with VIP on the game server", len(game_server_vips))

    records_by_player: defaultdict[str, list[VipListRecord]] = defaultdict(list)
    to_add: list[VipListRecordType] = []
    to_remove: set[str] = set()
    record_player_ids: set[str] = set()

    remove_unknown = True
    with enter_session() as sess:
        server_records = get_all_records_for_server(
            sess=sess, server_number=server_number
        )

        # A player can have multiple records; group by player
        # # TODO: There's probably some SQL we can write to offload this to postgres
        # but for now do it in Python
        for record in server_records:
            records_by_player[record.player.player_id].append(record)

        vip_lists = get_vip_lists_for_server(sess=sess, server_number=server_number)
        if any(lst.sync == VipListSyncMethod.IGNORE_UNKNOWN for lst in vip_lists):
            remove_unknown = False

        for player_id, player_records in records_by_player.items():
            # Keep track of all of the player IDs we have seen from VIP records
            # in case we are removing unknowns
            record_player_ids.add(player_id)
            top_record = get_highest_priority_record(records=player_records)
            # Check to make sure the player should have VIP; and then check if
            # they're missing from the game server; or the description differs
            if top_record and is_player_vip_by_records(
                records=player_records, timestamp=timestamp
            ):
                # On the game server we store them as PlayerName - Description, if there is no description
                # We just use their PlayerName
                try:
                    player_name = top_record.player.names[0].name
                except (IndexError, AttributeError):
                    player_name = "NO NAME IN CRCON"

                if top_record.description:
                    description = f"{player_name} - {top_record.description}"
                else:
                    description = f"{player_name}"

                if top_record.description != game_server_vips.get(player_id):
                    updated_record = top_record.to_dict()
                    updated_record["description"] = description
                    to_add.append(updated_record)

            # VIP is inactive or expired and should be removed if they're on the game server
            if player_id in game_server_vips and not is_player_vip_by_records(
                records=player_records, timestamp=timestamp
            ):
                to_remove.add(player_id)
            # When a record is deleted; VIP is removed in the handler
            # if they no longer have VIP from any other records

        if remove_unknown:
            unknown_vips: set[str] = set(game_server_vips.keys()) - record_player_ids
            to_remove |= unknown_vips
        else:
            unknown_vips: set[str] = set(game_server_vips.keys()) - record_player_ids
            logger.info("%s unknown VIP ids: %s", len(unknown_vips), unknown_vips)

        logger.info("Adding VIP to %s players", len(to_add))
        logger.info("Removing VIP from %s players", len(to_remove))
        rcon.bulk_add_vips(
            vips=[
                {
                    "player_id": record["player_id"],
                    "name": (
                        record["description"]
                        if record["description"]
                        else f"{record['player_id']} No Description Set"
                    ),
                }
                for record in to_add
            ]
        )
        rcon.bulk_remove_vips(player_ids=to_remove)


class VipListSynchCommand(BaseModel):
    pass


class VipListInactivateExpiredCommand(BaseModel):
    pass


class VipListEditListCommand(BaseModel):
    vip_list_id: int


class VipListDeleteListCommand(BaseModel):
    player_ids: set[str]


class VipListCreateRecordCommand(BaseModel):
    pass


class VipListEditRecordCommand(BaseModel):
    pass


class VipListDeleteRecordCommand(BaseModel):
    player_id: str


class VipListRevokeAllCommand(BaseModel):
    pass


class VipListCommandType(IntEnum):
    SYNCH_GAME_SERVER = auto()
    INACTIVATE_EXPIRED = auto()

    # CREATE_LIST is not needed; lists are created with no records
    EDIT_LIST = auto()
    DELETE_LIST = auto()

    CREATE_RECORD = auto()
    EDIT_RECORD = auto()
    DELETE_RECORD = auto()

    REVOKE_VIP = auto()


class VipListCommand(BaseModel):
    """Handles encoding/decoding commands to/from bytes for/from Redis"""

    command: VipListCommandType
    server_mask: int
    payload: dict

    # TODO: this is used multiple places, consolidate
    @staticmethod
    def _convert_types(o):
        if isinstance(o, set):
            return [val for val in sorted(o)]
        else:
            raise ValueError(f"Cannot serialize {o}, {type(o)} to JSON")

    @field_validator("server_mask", mode="before")
    @classmethod
    def convert_none_to_mask(cls, v: int | None) -> int:
        if v is None:
            # Create mask with the first 32 bits flipped
            return ALL_SERVERS_MASK
        return v

    def encode(self) -> bytes:
        """Dump our command type and payload to bytes for Redis"""
        return struct.pack("II", self.command, self.server_mask) + orjson.dumps(
            self.payload,
            default=VipListCommand._convert_types,
        )

    @classmethod
    def decode(cls, data: bytes) -> Self:
        """Unpack bytes from Redis and construct a VipListCommand"""
        split_at = struct.calcsize("II")

        command_id, server_mask = struct.unpack("II", data[:split_at])
        command = VipListCommandType(command_id)

        payload = orjson.loads(data[split_at:])

        return cls(command=command, server_mask=server_mask, payload=payload)


class VipListCommandHandler:
    CHANNEL = "vip_list"

    def __init__(self) -> None:
        redis_url = os.getenv("HLL_REDIS_URL")
        if not redis_url:
            raise RuntimeError("HLL_REDIS_URL not set")

        # Initialize our own little Redis client, because the shared one has
        # a global timeout and attempts to decode our little packets
        self.red = redis.Redis.from_url(
            redis_url, single_connection_client=True, decode_responses=False
        )

        self.pubsub = self.red.pubsub(ignore_subscribe_messages=True)

        # Avoid circular imports
        from rcon.api_commands import get_rcon_api

        self.rcon = get_rcon_api()

    @staticmethod
    def send(cmd: VipListCommand):
        if cmd.server_mask == 0:
            # Command will be ignored by all servers, don't bother sending it.
            return

        # Publish the command; each individual CRCON instance will be monitoring
        # this from VipListCommandHandler.run() run as a service from supervisord
        red.publish(VipListCommandHandler.CHANNEL, cmd.encode())

    def run(self) -> None:
        """Run the command handler loop, this is a blocking call.

        Cron is used externally to periodically inactivate expired records
        and resynch all the connected game servers
        """
        logger.info("Starting vip list command handler loop")
        self.pubsub.subscribe(self.CHANNEL)
        for message in self.pubsub.listen():
            try:
                data: bytes = message["data"]
                cmd = VipListCommand.decode(data)

                if not (cmd.server_mask & get_server_number_mask()):
                    # Command is not meant for this server
                    continue
                logger.info("Handling %s command", cmd.command.name)

                try:
                    match cmd.command:
                        case VipListCommandType.SYNCH_GAME_SERVER:
                            self.handle_synchronize(
                                VipListSynchCommand.model_validate(cmd.payload)
                            )
                        case VipListCommandType.INACTIVATE_EXPIRED:
                            self.handle_inactivate_expired_records(
                                VipListInactivateExpiredCommand.model_validate(
                                    cmd.payload
                                )
                            )
                        case VipListCommandType.EDIT_LIST:
                            self.handle_edit_list(
                                VipListEditListCommand.model_validate(cmd.payload)
                            )
                        case VipListCommandType.DELETE_LIST:
                            self.handle_delete_list(
                                VipListDeleteListCommand.model_validate(cmd.payload)
                            )
                        case VipListCommandType.CREATE_RECORD:
                            self.handle_create_record(
                                VipListCreateRecordCommand.model_validate(cmd.payload)
                            )
                        case VipListCommandType.EDIT_RECORD:
                            self.handle_edit_record(
                                VipListEditRecordCommand.model_validate(cmd.payload)
                            )
                        case VipListCommandType.DELETE_RECORD:
                            self.handle_delete_record(
                                VipListDeleteRecordCommand.model_validate(cmd.payload)
                            )
                        case VipListCommandType.REVOKE_VIP:
                            self.handle_revoke_all(
                                VipListRevokeAllCommand.model_validate(cmd.payload)
                            )
                        case _:
                            logger.error("Unknown command %r", cmd.command)
                except:
                    logger.exception(
                        "Error whilst executing %s command with payload %s",
                        cmd.command.name,
                        cmd.payload,
                    )
            except:
                logger.exception("Failed to parse data %s", message["data"])
            logger.info("Ready for next message!")

    def handle_synchronize(self, payload: VipListSynchCommand):
        """Resynch VIP records with the game server"""
        synchronize_with_game_server(rcon=self.rcon, server_number=SERVER_NUMBER)

    def handle_inactivate_expired_records(
        self, payload: VipListInactivateExpiredCommand
    ):
        """Inactivate any records that have expired"""
        inactivate_expired_records()

    def handle_edit_list(self, payload: VipListEditListCommand):
        """Editing a list causes a resynch with the game server"""
        synchronize_with_game_server(rcon=self.rcon, server_number=SERVER_NUMBER)

    def handle_delete_list(self, payload: VipListDeleteListCommand):
        """Handle a VipList being deleted.

        When a VipList is deleted; all players with VIP on the game server who were
        on the list and do not have VIP from another applicable list lose their
        VIP status on the game server

        Players with VIP on the game server who aren't on the affected list are ignored
        and unknown (not on any lists, but VIP on the game server) are handled
        according to other applicable lists VipListSyncMethod (the default list
        can never be deleted)
        """
        to_remove_player_ids: set[str] = set()
        with enter_session() as sess:
            for player_id in payload.player_ids:
                # Make sure the player shouldn't still have VIP from some other list
                if not is_player_vip_by_query(sess=sess, player_id=player_id):
                    to_remove_player_ids.add(player_id)

            self.rcon.bulk_remove_vips(player_ids=to_remove_player_ids)

    def handle_create_record(self, payload: VipListCreateRecordCommand):
        """Record creation causes a resynch with the game server"""
        synchronize_with_game_server(rcon=self.rcon, server_number=SERVER_NUMBER)

    def handle_edit_record(self, payload: VipListEditRecordCommand):
        """Record editing causes a resynch with the game server"""
        synchronize_with_game_server(rcon=self.rcon, server_number=SERVER_NUMBER)

    def handle_delete_record(self, payload: VipListDeleteRecordCommand):
        """Record deletion removes VIP if the player has no other applicable records"""
        with enter_session() as sess:
            if not is_player_vip_by_query(sess=sess, player_id=payload.player_id):
                self.rcon.remove_vip(player_id=payload.player_id)

    def handle_revoke_all(self, payload: VipListRevokeAllCommand):
        """Revoking VIP causes a resynch with the game server"""
        synchronize_with_game_server(rcon=self.rcon, server_number=SERVER_NUMBER)

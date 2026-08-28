"""Database service functions for VIP lists.

Gameserver synchronization is intentionally kept separate from this module's
CRUD operations.
"""

from collections.abc import Sequence
from datetime import datetime
from logging import getLogger

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from rcon.commands import HLLCommandFailedError
from rcon.models import PlayerID, VipList, VipListRecord, enter_session
from rcon.player_history import _get_set_player
from rcon.types import VipListRecordType, VipListSyncMethod, VipListType
from rcon.utils import MISSING, MissingType

logger = getLogger(__name__)


def get_vip_lists(sess: Session) -> Sequence[VipList]:
    """Return all VIP lists ordered by database ID."""
    return sess.scalars(select(VipList).order_by(VipList.id)).all()


def get_vip_lists_for_server(
    sess: Session,
    server_number: int,
) -> list[VipList]:
    """Return all VIP lists that apply to a server."""
    if server_number < 1 or server_number > 32:
        raise ValueError("Server number must be between 1 and 32")

    return [
        vip_list
        for vip_list in get_vip_lists(sess)
        if vip_list.servers is None or server_number in vip_list.get_server_numbers()
    ]


def get_vip_list(
    sess: Session,
    vip_list_id: int,
    strict: bool = False,
) -> VipList | None:
    """Return a VIP list by ID."""
    vip_list = sess.get(VipList, vip_list_id)

    if vip_list is None and strict:
        raise HLLCommandFailedError(f"No VIP list found with ID {vip_list_id}")

    return vip_list


def create_vip_list(
    name: str,
    sync: VipListSyncMethod = VipListSyncMethod.IGNORE_UNKNOWN,
    servers: Sequence[int] | None = None,
) -> VipListType:
    """Create an empty VIP list."""
    name = name.strip()
    if not name:
        raise ValueError("VIP list name must not be empty")

    with enter_session() as sess:
        vip_list = VipList(name=name, sync=sync)
        vip_list.set_server_numbers(servers)

        sess.add(vip_list)
        sess.commit()

        result = vip_list.to_dict()
        logger.info(
            "Created VIP list ID %s with name %s",
            vip_list.id,
            vip_list.name,
        )
        return result


def edit_vip_list(
    vip_list_id: int,
    name: str | MissingType = MISSING,
    sync: VipListSyncMethod | MissingType = MISSING,
    servers: Sequence[int] | None | MissingType = MISSING,
) -> VipListType:
    """Edit an existing VIP list without synchronizing a gameserver."""
    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=vip_list_id,
            strict=True,
        )
        assert vip_list is not None

        if name is not MISSING:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("VIP list name must not be empty")
            vip_list.name = normalized_name

        if sync is not MISSING:
            vip_list.sync = sync

        if servers is not MISSING:
            vip_list.set_server_numbers(servers)

        if sess.is_modified(vip_list):
            sess.commit()
            logger.info("Edited VIP list ID %s", vip_list.id)

        return vip_list.to_dict()


def delete_vip_list(vip_list_id: int) -> bool:
    """Delete a VIP list and its records."""
    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=vip_list_id,
            strict=False,
        )
        if vip_list is None:
            return False

        sess.delete(vip_list)
        sess.commit()
        logger.info("Deleted VIP list ID %s", vip_list_id)
        return True


def get_vip_record(
    sess: Session,
    record_id: int,
    strict: bool = False,
) -> VipListRecord | None:
    """Return a VIP list record by database ID."""
    record = sess.get(VipListRecord, record_id)

    if record is None and strict:
        raise HLLCommandFailedError(f"No VIP list record found with ID {record_id}")

    return record


def get_player_vip_list_record(
    sess: Session,
    player_id: str,
    vip_list_id: int,
) -> VipListRecord | None:
    """Return a player's record on a specific VIP list."""
    stmt = (
        select(VipListRecord)
        .join(VipListRecord.player)
        .where(PlayerID.player_id == player_id)
        .where(VipListRecord.vip_list_id == vip_list_id)
    )
    return sess.scalars(stmt).one_or_none()


def get_player_vip_list_records(
    sess: Session,
    player_id: str,
    *,
    include_expired: bool = True,
    include_inactive: bool = True,
    server_number: int | None = None,
) -> Sequence[VipListRecord]:
    """Return VIP list records associated with a player."""
    stmt = (
        select(VipListRecord)
        .join(VipListRecord.player)
        .where(PlayerID.player_id == player_id)
        .order_by(VipListRecord.id)
    )

    if not include_inactive:
        stmt = stmt.where(VipListRecord.active.is_(True))

    if not include_expired:
        stmt = stmt.where(
            or_(
                VipListRecord.expires_at.is_(None),
                VipListRecord.expires_at > func.now(),
            )
        )

    records = list(sess.scalars(stmt).all())

    if server_number is None:
        return records
    if server_number < 1 or server_number > 32:
        raise ValueError("Server number must be between 1 and 32")

    return [
        record
        for record in records
        if record.vip_list.servers is None
        or server_number in record.vip_list.get_server_numbers()
    ]


def get_active_vip_records(
    sess: Session,
    vip_list_id: int,
) -> Sequence[VipListRecord]:
    """Return active, non-expired records from a VIP list."""
    stmt = (
        select(VipListRecord)
        .where(VipListRecord.vip_list_id == vip_list_id)
        .where(VipListRecord.active.is_(True))
        .where(
            or_(
                VipListRecord.expires_at.is_(None),
                VipListRecord.expires_at > func.now(),
            )
        )
        .order_by(VipListRecord.id)
    )
    return sess.scalars(stmt).all()


def get_inactive_vip_records(
    sess: Session,
    vip_list_id: int,
) -> Sequence[VipListRecord]:
    """Return inactive or expired records from a VIP list."""
    stmt = (
        select(VipListRecord)
        .where(VipListRecord.vip_list_id == vip_list_id)
        .where(
            or_(
                VipListRecord.active.is_(False),
                VipListRecord.expires_at <= func.now(),
            )
        )
        .order_by(VipListRecord.id)
    )
    return sess.scalars(stmt).all()


def add_record_to_vip_list(
    player_id: str,
    vip_list_id: int,
    description: str | None = None,
    active: bool = True,
    expires_at: datetime | None = None,
    notes: str | None = None,
    admin_name: str = "CRCON",
) -> VipListRecordType:
    """Add one player to a VIP list."""
    player_id = player_id.strip()
    if not player_id:
        raise ValueError("Player ID must not be empty")
    if not isinstance(active, bool):
        raise TypeError("active must be a boolean")

    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=vip_list_id,
            strict=True,
        )
        assert vip_list is not None

        existing = get_player_vip_list_record(
            sess,
            player_id=player_id,
            vip_list_id=vip_list_id,
        )
        if existing is not None:
            raise HLLCommandFailedError(
                f"Player {player_id} already has a record on VIP list {vip_list_id}"
            )

        player = _get_set_player(sess, player_id)
        if player is None:
            raise RuntimeError("Unable to create PlayerID database record")

        record = VipListRecord(
            player=player,
            vip_list=vip_list,
            admin_name=admin_name.strip() or "CRCON",
            active=active,
            description=description,
            notes=notes,
            expires_at=expires_at,
        )
        sess.add(record)
        sess.commit()

        result = record.to_dict()
        logger.info(
            "Added player %s to VIP list ID %s",
            player_id,
            vip_list_id,
        )
        return result


def edit_vip_list_record(
    record_id: int,
    vip_list_id: int | MissingType = MISSING,
    description: str | None | MissingType = MISSING,
    active: bool | MissingType = MISSING,
    expires_at: datetime | None | MissingType = MISSING,
    notes: str | None | MissingType = MISSING,
    admin_name: str = "CRCON",
) -> VipListRecordType:
    """Edit a VIP record without synchronizing a gameserver."""
    with enter_session() as sess:
        record = get_vip_record(sess, record_id=record_id, strict=True)
        assert record is not None

        if vip_list_id is not MISSING and vip_list_id != record.vip_list_id:
            target_list = get_vip_list(
                sess,
                vip_list_id=vip_list_id,
                strict=True,
            )
            assert target_list is not None

            duplicate = get_player_vip_list_record(
                sess,
                player_id=record.player.player_id,
                vip_list_id=vip_list_id,
            )
            if duplicate is not None:
                raise HLLCommandFailedError(
                    f"Player {record.player.player_id} already has a record "
                    f"on VIP list {vip_list_id}"
                )

            record.vip_list = target_list

        if description is not MISSING:
            record.description = description
        if active is not MISSING:
            if not isinstance(active, bool):
                raise TypeError("active must be a boolean")
            record.active = active
        if expires_at is not MISSING:
            record.expires_at = expires_at
        if notes is not MISSING:
            record.notes = notes

        record.admin_name = admin_name.strip() or "CRCON"

        if sess.is_modified(record):
            sess.commit()
            logger.info("Edited VIP list record ID %s", record.id)

        return record.to_dict()


def delete_vip_list_record(record_id: int) -> bool:
    """Delete one VIP list record."""
    with enter_session() as sess:
        record = get_vip_record(
            sess,
            record_id=record_id,
            strict=False,
        )
        if record is None:
            return False

        sess.delete(record)
        sess.commit()
        logger.info("Deleted VIP list record ID %s", record_id)
        return True

"""Database service functions for VIP lists.

Gameserver synchronization is intentionally kept separate from this module's
CRUD operations.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from logging import getLogger

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from rcon.commands import HLLCommandFailedError
from rcon.models import (
    PlayerID,
    VipList,
    VipListDefault,
    VipListRecord,
    enter_session,
)
from rcon.player_history import _get_set_player
from rcon.player_id_utils import is_supported_player_id
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


def get_default_vip_list(
    sess: Session,
    server_number: int,
) -> VipList | None:
    """Return the default VIP list configured for one server."""
    if server_number < 1 or server_number > 32:
        raise ValueError("Server number must be between 1 and 32")

    default = sess.get(VipListDefault, server_number)
    return default.vip_list if default is not None else None


def set_default_vip_list(
    server_number: int,
    vip_list_id: int,
) -> VipListType:
    """Set the default VIP list for one server."""
    if server_number < 1 or server_number > 32:
        raise ValueError("Server number must be between 1 and 32")

    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=vip_list_id,
            strict=True,
        )
        assert vip_list is not None

        server_numbers = vip_list.get_server_numbers()
        if server_numbers is not None and server_number not in server_numbers:
            raise HLLCommandFailedError(
                f"VIP list {vip_list_id} does not apply to server {server_number}"
            )

        default = sess.get(VipListDefault, server_number)
        if default is None:
            default = VipListDefault(
                server_number=server_number,
                vip_list=vip_list,
            )
            sess.add(default)
        else:
            default.vip_list = vip_list

        sess.commit()
        logger.info(
            "Set VIP list ID %s as default for server %s",
            vip_list_id,
            server_number,
        )
        return vip_list.to_dict()


def clear_default_vip_list(server_number: int) -> bool:
    """Clear the default VIP list configured for one server."""
    if server_number < 1 or server_number > 32:
        raise ValueError("Server number must be between 1 and 32")

    with enter_session() as sess:
        default = sess.get(VipListDefault, server_number)
        if default is None:
            return False

        sess.delete(default)
        sess.commit()
        logger.info("Cleared default VIP list for server %s", server_number)
        return True


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
            incompatible_default_servers = (
                sorted(
                    default.server_number
                    for default in vip_list.defaults
                    if default.server_number not in servers
                )
                if servers is not None
                else []
            )
            if incompatible_default_servers:
                server_label = ", ".join(
                    f"#{server_number}"
                    for server_number in incompatible_default_servers
                )
                raise HLLCommandFailedError(
                    f"VIP list {vip_list_id} is the default for "
                    f"server {server_label}. Remove the default assignment "
                    "before changing the list's server scope."
                )

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
    if not is_supported_player_id(player_id):
        raise ValueError(
            "Player ID must be a 17-digit Steam64 ID or "
            "a 32-character hexadecimal network ID"
        )
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
            description=description if not player.names else None,
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
            if record.player.names:
                raise HLLCommandFailedError(
                    "Description is only available for players without "
                    "a known player name"
                )
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


def _normalize_vip_record_ids(record_ids: Sequence[int]) -> list[int]:
    """Normalize and validate record IDs for an atomic bulk operation."""
    normalized = list(dict.fromkeys(int(record_id) for record_id in record_ids))

    if not normalized:
        raise ValueError("At least one VIP list record ID is required")
    if any(record_id < 1 for record_id in normalized):
        raise ValueError("VIP list record IDs must be positive integers")

    return normalized


def _get_vip_records_for_bulk_operation(
    sess: Session,
    record_ids: Sequence[int],
) -> list[VipListRecord]:
    """Load every requested record or fail before changing any record."""
    normalized_ids = _normalize_vip_record_ids(record_ids)
    records_by_id = {
        record.id: record
        for record in sess.scalars(
            select(VipListRecord).where(VipListRecord.id.in_(normalized_ids))
        ).all()
    }
    missing_ids = [
        record_id for record_id in normalized_ids if record_id not in records_by_id
    ]

    if missing_ids:
        raise HLLCommandFailedError(
            "No VIP list records found with IDs "
            + ", ".join(str(record_id) for record_id in missing_ids)
        )

    return [records_by_id[record_id] for record_id in normalized_ids]


def edit_vip_list_records(
    record_ids: Sequence[int],
    vip_list_id: int | MissingType = MISSING,
    description: str | None | MissingType = MISSING,
    active: bool | MissingType = MISSING,
    expires_at: datetime | None | MissingType = MISSING,
    notes: str | None | MissingType = MISSING,
    admin_name: str = "CRCON",
) -> list[VipListRecordType]:
    """Atomically edit selected fields on multiple VIP list records."""
    if (
        vip_list_id is MISSING
        and description is MISSING
        and active is MISSING
        and expires_at is MISSING
        and notes is MISSING
    ):
        raise ValueError("At least one field must be selected for bulk editing")
    if active is not MISSING and not isinstance(active, bool):
        raise TypeError("active must be a boolean")

    with enter_session() as sess:
        records = _get_vip_records_for_bulk_operation(sess, record_ids)
        normalized_admin_name = admin_name.strip() or "CRCON"

        target_list = None
        if vip_list_id is not MISSING:
            target_list = get_vip_list(
                sess,
                vip_list_id=vip_list_id,
                strict=True,
            )
            assert target_list is not None

            selected_record_ids = {record.id for record in records}
            selected_player_ids = {record.player_id_id for record in records}
            duplicate_player_ids = set(
                sess.scalars(
                    select(VipListRecord.player_id_id)
                    .where(VipListRecord.vip_list_id == vip_list_id)
                    .where(VipListRecord.player_id_id.in_(selected_player_ids))
                    .where(VipListRecord.id.not_in(selected_record_ids))
                ).all()
            )
            if duplicate_player_ids:
                conflicting_players = sorted(
                    record.player.player_id
                    for record in records
                    if record.player_id_id in duplicate_player_ids
                )
                raise HLLCommandFailedError(
                    "Players already have records on VIP list "
                    f"{vip_list_id}: {', '.join(conflicting_players)}"
                )

        if description is not MISSING:
            named_records = [record for record in records if record.player.names]
            if named_records:
                raise HLLCommandFailedError(
                    "Description is only available for players without "
                    "a known player name; affected record IDs: "
                    + ", ".join(str(record.id) for record in named_records)
                )

        for record in records:
            if target_list is not None:
                record.vip_list = target_list
            if description is not MISSING:
                record.description = description
            if active is not MISSING:
                record.active = active
            if expires_at is not MISSING:
                record.expires_at = expires_at
            if notes is not MISSING:
                record.notes = notes
            record.admin_name = normalized_admin_name

        sess.commit()
        result = [record.to_dict() for record in records]
        logger.info(
            "Bulk edited VIP list record IDs %s",
            [record.id for record in records],
        )
        return result


def delete_vip_list_records(record_ids: Sequence[int]) -> int:
    """Atomically delete multiple VIP list records."""
    with enter_session() as sess:
        records = _get_vip_records_for_bulk_operation(sess, record_ids)

        for record in records:
            sess.delete(record)

        deleted_count = len(records)
        sess.commit()
        logger.info(
            "Bulk deleted VIP list record IDs %s",
            [record.id for record in records],
        )
        return deleted_count


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


def get_effective_vip_records(
    sess: Session,
    server_number: int,
    timestamp: datetime | None = None,
) -> dict[str, VipListRecord]:
    """Return the highest-priority active VIP record per player for a server."""
    timestamp = timestamp or datetime.now(tz=UTC)
    effective: dict[str, VipListRecord] = {}

    for vip_list in get_vip_lists_for_server(
        sess,
        server_number=server_number,
    ):
        for record in vip_list.records:
            if not record.active:
                continue
            if record.expires_at is not None and record.expires_at <= timestamp:
                continue

            player_id = record.player.player_id
            current = effective.get(player_id)
            if current is None:
                effective[player_id] = record
                continue

            if current.expires_at == record.expires_at:
                if record.created_at > current.created_at:
                    effective[player_id] = record
            elif record.expires_at is None:
                effective[player_id] = record
            elif (
                current.expires_at is not None
                and record.expires_at > current.expires_at
            ):
                effective[player_id] = record

    return effective


def upsert_default_vip_record(
    player_id: str,
    server_number: int,
    description: str | None = None,
    expires_at: datetime | None = None,
    admin_name: str = "Legacy VIP API",
) -> VipListRecordType:
    """Create or update a player's record in the server's default VIP list."""
    player_id = player_id.strip()
    if not is_supported_player_id(player_id):
        raise ValueError(
            "Player ID must be a 17-digit Steam64 ID or "
            "a 32-character hexadecimal network ID"
        )

    with enter_session() as sess:
        default_list = get_default_vip_list(
            sess,
            server_number=server_number,
        )
        if default_list is None:
            raise HLLCommandFailedError(
                f"No default VIP list configured for server {server_number}"
            )

        player = _get_set_player(sess, player_id)
        if player is None:
            raise RuntimeError("Unable to create PlayerID database record")

        record = get_player_vip_list_record(
            sess,
            player_id=player_id,
            vip_list_id=default_list.id,
        )
        if record is None:
            record = VipListRecord(
                player=player,
                vip_list=default_list,
                admin_name=admin_name.strip() or "Legacy VIP API",
                active=True,
                description=description if not player.names else None,
                expires_at=expires_at,
            )
            sess.add(record)
        else:
            record.admin_name = admin_name.strip() or "Legacy VIP API"
            record.active = True
            record.description = description if not player.names else None
            record.expires_at = expires_at

        sess.commit()
        result = record.to_dict()
        logger.info(
            "Upserted player %s in default VIP list ID %s for server %s",
            player_id,
            default_list.id,
            server_number,
        )
        return result


def deactivate_default_vip_record(
    player_id: str,
    server_number: int,
    admin_name: str = "Legacy VIP API",
) -> bool:
    """Deactivate a player's record in the server's default VIP list."""
    with enter_session() as sess:
        default_list = get_default_vip_list(
            sess,
            server_number=server_number,
        )
        if default_list is None:
            raise HLLCommandFailedError(
                f"No default VIP list configured for server {server_number}"
            )

        record = get_player_vip_list_record(
            sess,
            player_id=player_id,
            vip_list_id=default_list.id,
        )
        if record is None:
            return False

        record.active = False
        record.admin_name = admin_name.strip() or "Legacy VIP API"
        sess.commit()
        logger.info(
            "Deactivated player %s in default VIP list ID %s for server %s",
            player_id,
            default_list.id,
            server_number,
        )
        return True


def deactivate_all_default_vip_records(
    server_number: int,
    admin_name: str = "Legacy VIP API",
) -> int:
    """Deactivate all active records in the server's default VIP list."""
    with enter_session() as sess:
        default_list = get_default_vip_list(
            sess,
            server_number=server_number,
        )
        if default_list is None:
            raise HLLCommandFailedError(
                f"No default VIP list configured for server {server_number}"
            )

        records = [record for record in default_list.records if record.active]
        normalized_admin_name = admin_name.strip() or "Legacy VIP API"

        for record in records:
            record.active = False
            record.admin_name = normalized_admin_name

        sess.commit()
        logger.info(
            "Deactivated %s records in default VIP list ID %s for server %s",
            len(records),
            default_list.id,
            server_number,
        )
        return len(records)

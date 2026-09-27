"""Database service functions for VIP lists.

Gameserver synchronization is intentionally kept separate from this module's
CRUD operations.
"""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from logging import getLogger

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from rcon.commands import HLLCommandFailedError
from rcon.models import (
    PlayerFlag,
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

ALL_VIP_SERVERS_MASK = 2**32 - 1


def _merge_vip_server_masks(*server_masks: int | None) -> int:
    """Merge VIP server masks, treating None as all configured servers."""
    if any(server_mask is None for server_mask in server_masks):
        return ALL_VIP_SERVERS_MASK

    merged_mask = 0
    for server_mask in server_masks:
        assert server_mask is not None
        merged_mask |= int(server_mask)

    return merged_mask


def _notify_vip_sync(server_mask: int | None) -> None:
    """Request synchronization without rolling back committed DB changes."""
    normalized_mask = ALL_VIP_SERVERS_MASK if server_mask is None else int(server_mask)
    if normalized_mask == 0:
        return

    try:
        from rcon.vip_sync_handler import VipSyncCommandHandler

        subscribers = VipSyncCommandHandler.send(normalized_mask)
        logger.info(
            "Published VIP synchronization request for server mask %s "
            "to %s subscriber(s)",
            normalized_mask,
            subscribers,
        )
    except Exception:
        logger.exception(
            "Unable to publish VIP synchronization request for server mask %s; "
            "the committed database change will be recovered by periodic sync",
            normalized_mask,
        )


def _normalize_server_number(server_number: int | str) -> int:
    """Return a validated integer gameserver number."""
    try:
        normalized = int(server_number)
    except (TypeError, ValueError):
        raise ValueError("Server number must be between 1 and 32") from None

    if normalized < 1 or normalized > 32:
        raise ValueError("Server number must be between 1 and 32")

    return normalized


def get_vip_lists(sess: Session) -> Sequence[VipList]:
    """Return all VIP lists ordered by database ID."""
    return sess.scalars(select(VipList).order_by(VipList.id)).all()


def _ensure_editable(vip_list: VipList) -> None:
    if vip_list.partner_import is not None:
        raise HLLCommandFailedError(
            "Imported VIP lists are read-only; use partner approval or exclusion actions"
        )


def get_vip_lists_for_server(
    sess: Session,
    server_number: int | str,
) -> list[VipList]:
    """Return all VIP lists that apply to a server."""
    server_number = _normalize_server_number(server_number)

    return [
        vip_list
        for vip_list in get_vip_lists(sess)
        if vip_list.servers is None or server_number in vip_list.get_server_numbers()
    ]


def get_default_vip_list(
    sess: Session,
    server_number: int | str,
) -> VipList | None:
    """Return the default VIP list configured for one server."""
    server_number = _normalize_server_number(server_number)

    default = sess.get(VipListDefault, server_number)
    return default.vip_list if default is not None else None


def set_default_vip_list(
    server_number: int | str,
    vip_list_id: int,
) -> VipListType:
    """Set the default VIP list for one server."""
    server_number = _normalize_server_number(server_number)

    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=vip_list_id,
            strict=True,
        )
        assert vip_list is not None
        _ensure_editable(vip_list)

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


def clear_default_vip_list(server_number: int | str) -> bool:
    """Clear the default VIP list configured for one server."""
    server_number = _normalize_server_number(server_number)

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


def _validate_expired_retention_days(value: int | None) -> int | None:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > 3650
    ):
        raise ValueError("Expired VIP retention must be between 0 and 3650 days")
    return value


def _validate_default_expiration_seconds(value: int | None) -> int | None:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > 315360000
    ):
        raise ValueError("Default VIP duration must be between 0 and 10 years")
    return value


def _validate_vip_list_flags(flags: Sequence[str]) -> list[str]:
    if isinstance(flags, (str, bytes)) or not isinstance(flags, (tuple, list)):
        raise TypeError("VIP list flags must be an array of strings")
    normalized = []
    for item in flags:
        if not isinstance(item, str) or not item.strip() or len(item.strip()) > 64:
            raise ValueError("Each VIP list flag must contain 1 to 64 characters")
        if item.strip() not in normalized:
            normalized.append(item.strip())
    if len(normalized) > 20:
        raise ValueError("A VIP list can have at most 20 flags")
    return normalized


def reconcile_vip_list_flags(sess: Session, player_ids: set[int] | None = None) -> int:
    """Materialize effective list flags without taking ownership of manual flags."""
    sess.flush()
    now = datetime.now(UTC)
    stmt = (
        select(VipListRecord.player_id_id, VipList.flags)
        .join(VipList, VipList.id == VipListRecord.vip_list_id)
        .where(
            VipListRecord.active.is_(True),
            or_(VipListRecord.expires_at.is_(None), VipListRecord.expires_at > now),
        )
    )
    if player_ids is not None:
        if not player_ids:
            return 0
        stmt = stmt.where(VipListRecord.player_id_id.in_(player_ids))
    desired: dict[int, set[str]] = {}
    for player_id_id, flags in sess.execute(stmt):
        desired.setdefault(player_id_id, set()).update(flags or ())

    existing_stmt = select(PlayerFlag)
    if player_ids is not None:
        existing_stmt = existing_stmt.where(PlayerFlag.player_id_id.in_(player_ids))
    else:
        existing_stmt = existing_stmt.where(
            or_(
                PlayerFlag.managed_by_vip_list.is_(True),
                PlayerFlag.player_id_id.in_(desired),
            )
        )
    existing = {
        (item.player_id_id, item.flag): item for item in sess.scalars(existing_stmt)
    }
    changed = 0
    for key, flag in existing.items():
        if flag.managed_by_vip_list and key[1] not in desired.get(key[0], ()):
            sess.delete(flag)
            changed += 1
    for player_id_id, flags in desired.items():
        for flag in flags:
            if (player_id_id, flag) not in existing:
                sess.add(
                    PlayerFlag(
                        player_id_id=player_id_id,
                        flag=flag,
                        comment="Managed by VIP Lists",
                        managed_by_vip_list=True,
                    )
                )
                changed += 1
    return changed


def _list_expiration(vip_list: VipList) -> datetime | None:
    seconds = vip_list.default_expiration_seconds
    return datetime.now(UTC) + timedelta(seconds=seconds) if seconds else None


def apply_vip_list_expiration(
    vip_list_id: int,
    expected_expiration_seconds: int | None,
    include_expired: bool = False,
    include_inactive: bool = False,
) -> int:
    """Apply the configured duration to existing records.

    Expired and inactive records are only included when explicitly requested.
    This operation never changes a record's active state.
    """
    if not isinstance(include_expired, bool):
        raise TypeError("include_expired must be a boolean")
    if not isinstance(include_inactive, bool):
        raise TypeError("include_inactive must be a boolean")
    with enter_session() as sess:
        vip_list = get_vip_list(sess, vip_list_id, strict=True)
        assert vip_list is not None
        _ensure_editable(vip_list)
        if vip_list.default_expiration_seconds != expected_expiration_seconds:
            raise HLLCommandFailedError("VIP list duration changed; review it again")
        if expected_expiration_seconds is None:
            raise HLLCommandFailedError("VIP list has no default duration to apply")
        now = datetime.now(UTC)
        stmt = select(VipListRecord).where(VipListRecord.vip_list_id == vip_list_id)
        if not include_inactive:
            stmt = stmt.where(VipListRecord.active.is_(True))
        if not include_expired:
            stmt = stmt.where(
                or_(VipListRecord.expires_at.is_(None), VipListRecord.expires_at > now)
            )
        records = sess.scalars(stmt).all()
        expires_at = (
            now + timedelta(seconds=expected_expiration_seconds)
            if expected_expiration_seconds
            else None
        )
        changed = 0
        for record in records:
            if record.expires_at != expires_at:
                record.expires_at = expires_at
                changed += 1
        if changed:
            reconcile_vip_list_flags(sess, {record.player_id_id for record in records})
            sess.commit()
            _notify_vip_sync(vip_list.servers)
        logger.info(
            "Applied default duration of VIP list %s to %s records",
            vip_list_id,
            changed,
        )
        return changed


def cleanup_expired_vip_records(now: datetime | None = None) -> int:
    """Delete only records whose list explicitly enables expiry cleanup."""
    now = now or datetime.now(UTC)
    deleted = 0
    with enter_session() as sess:
        lists = sess.scalars(
            select(VipList).where(VipList.expired_retention_days.is_not(None))
        ).all()
        for vip_list in lists:
            if (
                vip_list.partner_import is not None
                and vip_list.default_expiration_seconds == 0
            ):
                continue
            cutoff = now - timedelta(days=vip_list.expired_retention_days)
            result = sess.execute(
                delete(VipListRecord).where(
                    VipListRecord.vip_list_id == vip_list.id,
                    VipListRecord.partner_excluded.is_(False),
                    or_(
                        (
                            VipListRecord.expires_at.is_not(None)
                            & (VipListRecord.expires_at <= cutoff)
                        ),
                        (
                            VipListRecord.partner_deactivated_at.is_not(None)
                            & (VipListRecord.partner_deactivated_at <= cutoff)
                            & VipListRecord.partner_excluded.is_(False)
                        ),
                    ),
                )
            )
            deleted += result.rowcount or 0
        flag_changes = reconcile_vip_list_flags(sess)
        if deleted:
            logger.info("Deleted %s expired VIP list record(s)", deleted)
        if flag_changes:
            logger.info("Reconciled %s VIP list-managed player flag(s)", flag_changes)
    return deleted


def create_vip_list(
    name: str,
    sync: VipListSyncMethod = VipListSyncMethod.IGNORE_UNKNOWN,
    servers: Sequence[int] | None = None,
    expired_retention_days: int | None = None,
    default_expiration_seconds: int | None = None,
    flags: Sequence[str] = (),
) -> VipListType:
    """Create an empty VIP list."""
    name = name.strip()
    if not name:
        raise ValueError("VIP list name must not be empty")

    with enter_session() as sess:
        vip_list = VipList(
            name=name,
            sync=sync,
            expired_retention_days=_validate_expired_retention_days(
                expired_retention_days
            ),
            default_expiration_seconds=_validate_default_expiration_seconds(
                default_expiration_seconds
            ),
            flags=_validate_vip_list_flags(flags),
        )
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
    expired_retention_days: int | None | MissingType = MISSING,
    default_expiration_seconds: int | None | MissingType = MISSING,
    flags: Sequence[str] | MissingType = MISSING,
) -> VipListType:
    """Edit an existing VIP list without synchronizing a gameserver."""
    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=vip_list_id,
            strict=True,
        )
        assert vip_list is not None
        _ensure_editable(vip_list)
        old_server_mask = vip_list.servers

        if name is not MISSING:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("VIP list name must not be empty")
            vip_list.name = normalized_name

        if sync is not MISSING:
            vip_list.sync = sync

        if expired_retention_days is not MISSING:
            vip_list.expired_retention_days = _validate_expired_retention_days(
                expired_retention_days
            )

        if default_expiration_seconds is not MISSING:
            vip_list.default_expiration_seconds = _validate_default_expiration_seconds(
                default_expiration_seconds
            )

        if flags is not MISSING:
            vip_list.flags = _validate_vip_list_flags(flags)

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
            new_server_mask = vip_list.servers
            reconcile_vip_list_flags(sess)
            sess.commit()
            logger.info("Edited VIP list ID %s", vip_list.id)
            _notify_vip_sync(
                _merge_vip_server_masks(
                    old_server_mask,
                    new_server_mask,
                )
            )

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

        server_mask = vip_list.servers
        sess.delete(vip_list)
        reconcile_vip_list_flags(sess)
        sess.commit()
        logger.info("Deleted VIP list ID %s", vip_list_id)
        _notify_vip_sync(server_mask)
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
    server_number: int | str | None = None,
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
    server_number = _normalize_server_number(server_number)

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
    expires_at: datetime | None | MissingType = MISSING,
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
        _ensure_editable(vip_list)

        if expires_at is MISSING:
            expires_at = _list_expiration(vip_list)

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
        reconcile_vip_list_flags(sess, {player.id})
        sess.commit()
        _notify_vip_sync(vip_list.servers)

        result = record.to_dict()
        logger.info(
            "Added player %s to VIP list ID %s",
            player_id,
            vip_list_id,
        )
        return result


def upsert_vip_list_record(
    player_id: str,
    vip_list_id: int,
    description: str | None = None,
    expires_at: datetime | None | MissingType = MISSING,
    notes: str | None = None,
    admin_name: str = "CRCON",
) -> VipListRecordType:
    """Create or reactivate one player record on a specific VIP list."""
    player_id = player_id.strip()
    if not is_supported_player_id(player_id):
        raise ValueError(
            "Player ID must be a 17-digit Steam64 ID or "
            "a 32-character hexadecimal network ID"
        )

    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=int(vip_list_id),
            strict=True,
        )
        assert vip_list is not None
        _ensure_editable(vip_list)

        if expires_at is MISSING:
            expires_at = _list_expiration(vip_list)

        record = get_player_vip_list_record(
            sess,
            player_id=player_id,
            vip_list_id=vip_list.id,
        )
        created = record is None

        if created:
            player = _get_set_player(sess, player_id)
            if player is None:
                raise RuntimeError("Unable to create PlayerID database record")

            record = VipListRecord(
                player=player,
                vip_list=vip_list,
                admin_name=admin_name.strip() or "CRCON",
                active=True,
                description=description if not player.names else None,
                notes=notes,
                expires_at=expires_at,
            )
            sess.add(record)
        else:
            record.active = True
            record.expires_at = expires_at
            record.notes = notes
            record.admin_name = admin_name.strip() or "CRCON"

            if not record.player.names:
                record.description = description

        changed = created or sess.is_modified(record)

        if changed:
            reconcile_vip_list_flags(sess, {record.player_id_id})
            sess.commit()
            logger.info(
                "%s player %s on VIP list ID %s",
                "Created" if created else "Updated",
                player_id,
                vip_list.id,
            )
            _notify_vip_sync(vip_list.servers)

        return record.to_dict()


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
        _ensure_editable(record.vip_list)
        old_server_mask = record.vip_list.servers

        if vip_list_id is not MISSING and vip_list_id != record.vip_list_id:
            target_list = get_vip_list(
                sess,
                vip_list_id=vip_list_id,
                strict=True,
            )
            assert target_list is not None
            _ensure_editable(target_list)

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
            new_server_mask = record.vip_list.servers
            reconcile_vip_list_flags(sess, {record.player_id_id})
            sess.commit()
            logger.info("Edited VIP list record ID %s", record.id)
            _notify_vip_sync(
                _merge_vip_server_masks(
                    old_server_mask,
                    new_server_mask,
                )
            )

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
        for record in records:
            _ensure_editable(record.vip_list)
        old_server_masks = [record.vip_list.servers for record in records]
        normalized_admin_name = admin_name.strip() or "CRCON"

        target_list = None
        if vip_list_id is not MISSING:
            target_list = get_vip_list(
                sess,
                vip_list_id=vip_list_id,
                strict=True,
            )
            assert target_list is not None
            _ensure_editable(target_list)

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

        reconcile_vip_list_flags(sess, {record.player_id_id for record in records})
        sess.commit()
        result = [record.to_dict() for record in records]
        logger.info(
            "Bulk edited VIP list record IDs %s",
            [record.id for record in records],
        )
        _notify_vip_sync(
            _merge_vip_server_masks(
                *old_server_masks,
                *(record.vip_list.servers for record in records),
            )
        )
        return result


def delete_vip_list_records(record_ids: Sequence[int]) -> int:
    """Atomically delete multiple VIP list records."""
    with enter_session() as sess:
        records = _get_vip_records_for_bulk_operation(sess, record_ids)
        for record in records:
            if record.vip_list.partner_import is not None and (
                record.active or record.partner_present or record.partner_excluded
            ):
                raise HLLCommandFailedError(
                    "Only partner-removed VIP entries without a local exclusion may be deleted"
                )
        server_mask = _merge_vip_server_masks(
            *(record.vip_list.servers for record in records)
        )

        for record in records:
            sess.delete(record)

        deleted_count = len(records)
        reconcile_vip_list_flags(sess, {record.player_id_id for record in records})
        sess.commit()
        logger.info(
            "Bulk deleted VIP list record IDs %s",
            [record.id for record in records],
        )
        _notify_vip_sync(server_mask)
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
        if record.vip_list.partner_import is not None and (
            record.active or record.partner_present or record.partner_excluded
        ):
            raise HLLCommandFailedError(
                "Only partner-removed VIP entries without a local exclusion may be deleted"
            )

        server_mask = record.vip_list.servers
        sess.delete(record)
        reconcile_vip_list_flags(sess, {record.player_id_id})
        sess.commit()
        logger.info("Deleted VIP list record ID %s", record_id)
        _notify_vip_sync(server_mask)
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
            elif record.expires_at is None or (
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

        reconcile_vip_list_flags(sess, {player.id})
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
        reconcile_vip_list_flags(sess, {record.player_id_id})
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

        reconcile_vip_list_flags(sess, {record.player_id_id for record in records})
        sess.commit()
        logger.info(
            "Deactivated %s records in default VIP list ID %s for server %s",
            len(records),
            default_list.id,
            server_number,
        )
        return len(records)

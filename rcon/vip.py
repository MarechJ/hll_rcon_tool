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
    PlayerAccount,
    PlayerFlag,
    PlayerID,
    PlayerIdentityGame,
    PlayerSoldier,
    VipList,
    VipListDefault,
    VipListPendingRecord,
    VipListRecord,
    VipServerSyncConfig,
    enter_session,
)
from rcon.player_history import _get_set_player
from rcon.player_id_utils import is_network_player_id, is_supported_player_id
from rcon.types import (
    GameEnum,
    VipListPendingRecordType,
    VipListRecordType,
    VipListSyncMethod,
    VipListType,
)
from rcon.utils import MISSING, MissingType

logger = getLogger(__name__)

ALL_VIP_SERVERS_MASK = 2**32 - 1


def _get_or_create_import_player(
    sess: Session,
    player_id: str,
) -> PlayerID:
    """Get or create a player without committing the import transaction."""
    player = sess.scalar(select(PlayerID).where(PlayerID.player_id == player_id))
    if player is not None:
        return player

    logger.info("Adding player %s during VIP list import", player_id)
    player = PlayerID(player_id=player_id)
    sess.add(player)
    sess.add(PlayerAccount(player=player))
    sess.add(PlayerSoldier(player=player))

    # Assign the PlayerID primary key while keeping creation part of the
    # surrounding VIP import transaction.
    sess.flush()
    return player


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


def get_server_vip_sync_mode(
    sess: Session, server_number: int | str
) -> VipListSyncMethod:
    server_number = _normalize_server_number(server_number)
    config = sess.get(VipServerSyncConfig, server_number)
    return config.sync if config is not None else VipListSyncMethod.IGNORE_UNKNOWN


def set_server_vip_sync_mode(
    server_number: int | str, sync: VipListSyncMethod | str
) -> dict:
    server_number = _normalize_server_number(server_number)
    sync = VipListSyncMethod(sync)
    with enter_session() as sess:
        config = sess.get(VipServerSyncConfig, server_number)
        if config is None:
            config = VipServerSyncConfig(server_number=server_number, sync=sync)
            sess.add(config)
        else:
            config.sync = sync
    return {"server_number": server_number, "sync": sync.value}


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


def _resolve_manual_vip_player(
    sess: Session,
    player_id: str,
    target_game: GameEnum,
) -> PlayerID:
    """Resolve one manually entered VIP identity for the target game."""
    identity = _resolve_vip_identity(
        sess,
        player_id,
        target_game=target_game,
    )

    status = identity["resolution_status"]
    if status == "pending":
        raise HLLCommandFailedError(
            f"Player {player_id} has no known {target_game.value} identity yet"
        )
    if status == "conflict":
        raise HLLCommandFailedError(
            identity["resolution_error"]
            or f"Player {player_id} has an ambiguous {target_game.value} identity"
        )

    player = identity["player"]
    if player is None:
        player = _get_set_player(
            sess,
            identity["resolved_player_id"],
            steam_id=identity["steam_id"],
        )

    if player is None:
        raise RuntimeError("Unable to create PlayerID database record")

    return player


def add_record_to_vip_list(
    player_id: str,
    vip_list_id: int,
    description: str | None = None,
    active: bool = True,
    expires_at: datetime | None | MissingType = MISSING,
    notes: str | None = None,
    admin_name: str = "CRCON",
    target_game: GameEnum = GameEnum.HLL_WW2,
) -> VipListRecordType | VipListPendingRecordType:
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

        # A Steam64 added manually to an HLL Vietnam list may not have a
        # known HLLV network identity yet. Keep it pending until CRCON
        # observes an unambiguous HLLV identity for that Steam account.
        if target_game == GameEnum.HLL_VIETNAM and _is_steam_id(player_id):
            identity = _resolve_vip_identity(
                sess,
                player_id,
                target_game=target_game,
            )

            if identity["resolution_status"] == "conflict":
                raise HLLCommandFailedError(
                    identity["resolution_error"]
                    or f"Player {player_id} has multiple HLL Vietnam identities"
                )

            if identity["resolution_status"] == "pending":
                existing_record = sess.scalar(
                    select(VipListRecord)
                    .join(PlayerID, PlayerID.id == VipListRecord.player_id_id)
                    .where(
                        VipListRecord.vip_list_id == vip_list.id,
                        PlayerID.steam_id == player_id,
                    )
                )
                if existing_record is not None:
                    raise HLLCommandFailedError(
                        f"Steam ID {player_id} already has a resolved record on "
                        f"VIP list {vip_list_id}"
                    )

                existing_pending = sess.scalar(
                    select(VipListPendingRecord).where(
                        VipListPendingRecord.vip_list_id == vip_list.id,
                        VipListPendingRecord.steam_id == player_id,
                    )
                )
                if existing_pending is not None:
                    raise HLLCommandFailedError(
                        f"Steam ID {player_id} already has a pending record on "
                        f"VIP list {vip_list_id}"
                    )

                pending = VipListPendingRecord(
                    vip_list=vip_list,
                    steam_id=player_id,
                    admin_name=admin_name.strip() or "CRCON",
                    description=description,
                    notes=notes,
                    expires_at=expires_at,
                )
                sess.add(pending)
                sess.commit()

                logger.info(
                    "Added Steam ID %s as pending to HLL Vietnam VIP list ID %s",
                    player_id,
                    vip_list_id,
                )

                return pending_vip_record_to_dict(pending)

            player = identity["player"]
            if player is None:
                raise HLLCommandFailedError(
                    f"Unable to resolve HLL Vietnam identity for {player_id}"
                )
        else:
            player = _resolve_manual_vip_player(
                sess,
                player_id,
                target_game,
            )

        existing = get_player_vip_list_record(
            sess,
            player_id=player.player_id,
            vip_list_id=vip_list_id,
        )
        if existing is not None:
            raise HLLCommandFailedError(
                f"Player {player.player_id} already has a record on "
                f"VIP list {vip_list_id}"
            )

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
    target_game: GameEnum = GameEnum.HLL_WW2,
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

        player = _resolve_manual_vip_player(
            sess,
            player_id,
            target_game,
        )

        record = get_player_vip_list_record(
            sess,
            player_id=player.player_id,
            vip_list_id=vip_list.id,
        )
        created = record is None

        if created:
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


def get_vip_list_records(
    sess: Session,
    vip_list_id: int,
) -> list[VipListRecord]:
    """Return all records belonging to one VIP list."""
    return list(
        sess.scalars(
            select(VipListRecord)
            .where(VipListRecord.vip_list_id == int(vip_list_id))
            .order_by(VipListRecord.id)
        ).all()
    )


def get_pending_vip_records(
    sess: Session,
    vip_list_id: int,
) -> Sequence[VipListPendingRecord]:
    """Return unresolved HLL Vietnam identities from one VIP list."""
    return sess.scalars(
        select(VipListPendingRecord)
        .where(VipListPendingRecord.vip_list_id == int(vip_list_id))
        .order_by(VipListPendingRecord.id)
    ).all()


def pending_vip_record_to_dict(
    record: VipListPendingRecord,
) -> VipListPendingRecordType:
    """Serialize one unresolved VIP identity for the VIP list UI."""
    return {
        "id": record.id,
        "vip_list_id": record.vip_list_id,
        "player_id": record.steam_id,
        "steam_id": record.steam_id,
        "player_name": None,
        "admin_name": record.admin_name,
        "created_at": record.created_at,
        "is_active": True,
        "is_expired": bool(
            record.expires_at is not None
            and record.expires_at <= datetime.now(UTC)
        ),
        "expires_at": record.expires_at,
        "description": record.description,
        "notes": record.notes,
        "partner_approved": False,
        "partner_excluded": False,
        "partner_present": False,
        "partner_deactivated_at": None,
        "record_type": "pending",
        "resolution_status": "pending",
        "resolution_error": record.resolution_error,
    }


def get_all_vip_records(
    sess: Session,
) -> Sequence[VipListRecord]:
    """Return all VIP list records across all configured lists."""
    return sess.scalars(
        select(VipListRecord).order_by(
            VipListRecord.vip_list_id,
            VipListRecord.id,
        )
    ).all()


def _normalize_vip_list_import(
    entries: Sequence[dict],
    mode: str,
) -> tuple[str, dict[str, dict]]:
    """Normalize and validate a VIP list import request."""
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"merge", "replace"}:
        raise ValueError("VIP list import mode must be 'merge' or 'replace'")

    normalized_entries: dict[str, dict] = {}
    for entry in entries:
        player_id = str(entry["player_id"]).strip()
        if not is_supported_player_id(player_id):
            raise ValueError(f"Unsupported player ID in VIP list import: {player_id}")
        if player_id in normalized_entries:
            raise ValueError(f"Duplicate player ID in VIP list import: {player_id}")

        steam_id = entry.get("steam_id")
        if steam_id is not None:
            steam_id = str(steam_id).strip() or None
            if steam_id is not None and (len(steam_id) != 17 or not steam_id.isdigit()):
                raise ValueError(f"Invalid Steam ID in VIP list import: {steam_id}")

        normalized_entries[player_id] = {
            "player_id": player_id,
            "steam_id": steam_id,
            "description": entry.get("description"),
            "expires_at": entry.get("expires_at", MISSING),
            "notes": entry.get("notes"),
            "legacy_import": bool(entry.get("legacy_import", False)),
        }

    if normalized_mode == "replace" and not normalized_entries:
        raise ValueError("Cannot replace a VIP list with an empty import")

    return normalized_mode, normalized_entries


def _is_steam_id(value: str | None) -> bool:
    """Return whether a value is a Steam64 ID."""
    return value is not None and len(value) == 17 and value.isdigit()


def _find_players_for_steam_id(
    sess: Session,
    steam_id: str,
) -> list[PlayerID]:
    """Return all PlayerID rows associated with a Steam64 ID."""
    return (
        sess.scalars(
            select(PlayerID)
            .where(
                or_(
                    PlayerID.player_id == steam_id,
                    PlayerID.steam_id == steam_id,
                )
            )
            .order_by(PlayerID.id)
        )
        .unique()
        .all()
    )


def _player_was_observed_in_game(
    sess: Session,
    player: PlayerID,
    game: GameEnum,
) -> bool:
    """Return whether this concrete player identity was observed in a game."""
    return (
        sess.query(PlayerIdentityGame.id)
        .filter(
            PlayerIdentityGame.player_id_id == player.id,
            PlayerIdentityGame.game == game.value,
        )
        .first()
        is not None
    )


def _find_hllv_players_for_steam_id(
    sess: Session,
    steam_id: str,
) -> list[PlayerID]:
    """Return network identities with an exact Steam64 mapping.

    An existing unambiguous network ID <-> Steam64 mapping is sufficient for
    HLL Vietnam VIP identity resolution. Game observations are tracked
    separately and are not required for resolving an existing mapping.
    """
    return [
        player
        for player in _find_players_for_steam_id(sess, steam_id)
        if is_network_player_id(player.player_id)
        and player.steam_id == steam_id
    ]


def resolve_pending_vip_records(
    steam_id: str | None = None,
    *,
    notify: bool = True,
) -> dict[str, int]:
    """Resolve pending HLL Vietnam VIP identities from known Steam mappings."""
    if steam_id is not None:
        steam_id = str(steam_id).strip()
        if not _is_steam_id(steam_id):
            raise ValueError(f"Invalid Steam ID: {steam_id}")

    checked = 0
    resolved = 0
    pending = 0
    conflicts = 0
    affected_player_ids: set[int] = set()
    changed_server_masks: list[int | None] = []
    now = datetime.now(UTC)

    with enter_session() as sess:
        pending_list_ids_stmt = (
            select(VipListPendingRecord.vip_list_id)
            .distinct()
            .order_by(VipListPendingRecord.vip_list_id)
        )
        if steam_id is not None:
            pending_list_ids_stmt = pending_list_ids_stmt.where(
                VipListPendingRecord.steam_id == steam_id
            )

        pending_list_ids = list(sess.scalars(pending_list_ids_stmt).all())

        # Use the VipList row as the shared serialization point with imports.
        # SKIP LOCKED keeps another list operation from blocking this resolver.
        locked_list_ids = set(
            sess.scalars(
                select(VipList.id)
                .where(VipList.id.in_(pending_list_ids))
                .order_by(VipList.id)
                .with_for_update(skip_locked=True)
            ).all()
        )

        stmt = (
            select(VipListPendingRecord)
            .where(VipListPendingRecord.vip_list_id.in_(locked_list_ids))
            .order_by(VipListPendingRecord.id)
            .with_for_update(skip_locked=True)
        )
        if steam_id is not None:
            stmt = stmt.where(VipListPendingRecord.steam_id == steam_id)

        pending_records = sess.scalars(stmt).all()

        for pending_record in pending_records:
            checked += 1
            pending_record.last_checked_at = now

            candidates = _find_hllv_players_for_steam_id(
                sess,
                pending_record.steam_id,
            )

            if not candidates:
                pending_record.resolution_error = None
                pending += 1
                continue

            if len(candidates) > 1:
                candidate_ids = ", ".join(
                    candidate.player_id for candidate in candidates
                )
                pending_record.resolution_error = (
                    f"Ambiguous Steam ID {pending_record.steam_id}: "
                    f"matches {candidate_ids}"
                )
                conflicts += 1
                continue

            player = candidates[0]
            vip_list = pending_record.vip_list

            record = sess.scalar(
                select(VipListRecord).where(
                    VipListRecord.vip_list_id == pending_record.vip_list_id,
                    VipListRecord.player_id_id == player.id,
                )
            )

            if record is None:
                record = VipListRecord(
                    player=player,
                    vip_list=vip_list,
                    admin_name=pending_record.admin_name,
                    active=True,
                    description=pending_record.description,
                    notes=pending_record.notes,
                    expires_at=pending_record.expires_at,
                )
                sess.add(record)
            else:
                record.active = True
                record.admin_name = pending_record.admin_name
                record.description = pending_record.description
                record.notes = pending_record.notes
                record.expires_at = pending_record.expires_at

            affected_player_ids.add(player.id)
            changed_server_masks.append(vip_list.servers)

            sess.delete(pending_record)
            resolved += 1

        if affected_player_ids:
            sess.flush()
            reconcile_vip_list_flags(sess, affected_player_ids)

        sess.commit()

    if notify and changed_server_masks:
        _notify_vip_sync(_merge_vip_server_masks(*changed_server_masks))

    result = {
        "checked": checked,
        "resolved": resolved,
        "pending": pending,
        "conflicts": conflicts,
    }

    if checked:
        logger.info(
            "Pending VIP identity resolution completed: "
            "%s checked, %s resolved, %s pending, %s conflicts",
            checked,
            resolved,
            pending,
            conflicts,
        )

    return result


def _resolve_vip_identity(
    sess: Session,
    player_id: str,
    *,
    steam_id: str | None = None,
    target_game: GameEnum = GameEnum.HLL_WW2,
) -> dict:
    """Resolve one player identity for a target game without creating records."""
    player_id = player_id.strip()

    if not is_supported_player_id(player_id):
        raise ValueError(f"Unsupported player ID: {player_id}")

    if steam_id is not None:
        steam_id = str(steam_id).strip() or None
        if steam_id is not None and not _is_steam_id(steam_id):
            raise ValueError(f"Invalid Steam ID: {steam_id}")

    player: PlayerID | None = None
    resolved_player_id = player_id
    resolution_status = "resolved"
    resolution_error: str | None = None

    if target_game == GameEnum.HLL_WW2:
        if steam_id is not None:
            candidates = _find_players_for_steam_id(sess, steam_id)
            steam_player = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate.player_id == steam_id
                ),
                None,
            )

            resolved_player_id = steam_id
            player = steam_player

            if len(candidates) > 1 and steam_player is None:
                resolution_status = "conflict"
                candidate_ids = ", ".join(
                    candidate.player_id for candidate in candidates
                )
                resolution_error = (
                    f"Ambiguous Steam ID {steam_id}: matches {candidate_ids}"
                )
        else:
            player = sess.scalar(
                select(PlayerID).where(PlayerID.player_id == player_id)
            )

    elif target_game == GameEnum.HLL_VIETNAM:
        if not _is_steam_id(player_id):
            player = sess.scalar(
                select(PlayerID).where(PlayerID.player_id == player_id)
            )

            # A network ID is accepted when CRCON observed it on an HLL
            # Vietnam server or when the caller supplies the exact Steam64
            # mapping already stored for this concrete identity. Importing an
            # existing mapping does not count as a game observation.
            observed_in_hllv = (
                player is not None
                and _player_was_observed_in_game(
                    sess,
                    player,
                    GameEnum.HLL_VIETNAM,
                )
            )
            mapped_to_supplied_steam_id = (
                player is not None
                and steam_id is not None
                and player.steam_id == steam_id
            )

            if not observed_in_hllv and not mapped_to_supplied_steam_id:
                raise ValueError(
                    f"Network ID {player_id} is not a known HLL Vietnam identity "
                    "and cannot be resolved without a matching Steam ID"
                )
        else:
            lookup_steam_id = steam_id or player_id
            hllv_candidates = _find_hllv_players_for_steam_id(
                sess,
                lookup_steam_id,
            )

            if len(hllv_candidates) == 1:
                player = hllv_candidates[0]
                resolved_player_id = player.player_id
            elif len(hllv_candidates) == 0:
                resolution_status = "pending"
                resolved_player_id = lookup_steam_id
            else:
                resolution_status = "conflict"
                resolved_player_id = lookup_steam_id
                candidate_ids = ", ".join(
                    candidate.player_id for candidate in hllv_candidates
                )
                resolution_error = (
                    f"Ambiguous Steam ID {lookup_steam_id}: matches {candidate_ids}"
                )

            steam_id = lookup_steam_id

    else:
        raise ValueError(
            f"Unsupported target game for VIP identity resolution: {target_game}"
        )

    return {
        "player_id": player_id,
        "steam_id": steam_id,
        "player": player,
        "resolved_player_id": resolved_player_id,
        "resolution_status": resolution_status,
        "resolution_error": resolution_error,
    }


def _resolve_vip_import_identities(
    sess: Session,
    normalized_entries: dict[str, dict],
    target_game: GameEnum,
) -> dict[int | str, dict]:
    """Resolve imported identities for the target game."""
    resolved_entries: dict[int | str, dict] = {}

    for imported_player_id, entry in normalized_entries.items():
        try:
            identity = _resolve_vip_identity(
                sess,
                imported_player_id,
                steam_id=entry.get("steam_id"),
                target_game=target_game,
            )
        except ValueError as exc:
            if (
                target_game == GameEnum.HLL_VIETNAM
                and entry.get("legacy_import")
                and not _is_steam_id(imported_player_id)
                and entry.get("steam_id") is None
            ):
                identity = {
                    "player_id": imported_player_id,
                    "steam_id": None,
                    "player": None,
                    "resolved_player_id": imported_player_id,
                    "resolution_status": "skipped",
                    "resolution_error": str(exc),
                }
            else:
                raise

        resolved = dict(entry)
        resolved.update(identity)

        resolution_status = resolved["resolution_status"]
        steam_id = resolved["steam_id"]
        player = resolved["player"]
        resolved_player_id = resolved["resolved_player_id"]

        if resolution_status == "resolved" and player is not None:
            key: int | str = player.id
        elif resolution_status in {"pending", "conflict"}:
            key = f"{resolution_status}:{steam_id or resolved_player_id}"
        else:
            key = resolved_player_id

        if key in resolved_entries:
            raise ValueError(
                "Duplicate player identity in VIP list import after resolution: "
                f"{resolved_player_id}"
            )

        resolved_entries[key] = resolved

    return resolved_entries


def preview_vip_list_import(
    vip_list_id: int,
    entries: Sequence[dict],
    mode: str = "merge",
    target_game: GameEnum = GameEnum.HLL_WW2,
) -> dict:
    """Preview importing records into one editable VIP list."""
    normalized_mode, normalized_entries = _normalize_vip_list_import(
        entries,
        mode,
    )

    with enter_session() as sess:
        vip_list = get_vip_list(
            sess,
            vip_list_id=int(vip_list_id),
            strict=True,
        )
        assert vip_list is not None
        _ensure_editable(vip_list)

        resolved_entries = _resolve_vip_import_identities(
            sess,
            normalized_entries,
            target_game,
        )

        existing_records = list(
            sess.scalars(
                select(VipListRecord)
                .where(VipListRecord.vip_list_id == vip_list.id)
                .order_by(VipListRecord.id)
            ).all()
        )
        existing_by_player_id = {
            record.player_id_id: record for record in existing_records
        }

        existing_pending = list(
            sess.scalars(
                select(VipListPendingRecord)
                .where(VipListPendingRecord.vip_list_id == vip_list.id)
                .order_by(VipListPendingRecord.id)
            ).all()
        )
        existing_pending_by_steam_id = {
            record.steam_id: record for record in existing_pending
        }

        ready = 0
        pending = 0
        conflicts = 0
        skipped = 0

        created = 0
        updated = 0
        unchanged = 0
        deactivated = 0

        pending_created = 0
        pending_updated = 0
        pending_unchanged = 0
        pending_removed = 0

        imported_player_ids: set[int] = set()
        imported_logical_ids: set[str] = set()
        imported_pending_steam_ids: set[str] = set()
        resolved_pending_steam_ids: set[str] = set()

        for identity_key, entry in resolved_entries.items():
            status = entry["resolution_status"]
            steam_id = entry.get("steam_id")
            resolved_player_id = entry["resolved_player_id"]

            if status == "skipped":
                skipped += 1
                continue

            if steam_id:
                imported_logical_ids.add(steam_id)
            imported_logical_ids.add(resolved_player_id)

            imported_expires_at = entry["expires_at"]
            expires_at = imported_expires_at
            if expires_at is MISSING:
                expires_at = _list_expiration(vip_list)

            if status in {"pending", "conflict"}:
                if not steam_id:
                    raise RuntimeError("Pending VIP import identity has no Steam ID")

                if status == "pending":
                    pending += 1
                else:
                    conflicts += 1

                imported_pending_steam_ids.add(steam_id)
                pending_record = existing_pending_by_steam_id.get(steam_id)

                if pending_record is not None and imported_expires_at is MISSING:
                    expires_at = pending_record.expires_at

                if pending_record is None:
                    pending_created += 1
                else:
                    changed = (
                        pending_record.expires_at != expires_at
                        or pending_record.description != entry["description"]
                        or pending_record.notes != entry["notes"]
                        or pending_record.resolution_error != entry["resolution_error"]
                    )

                    if changed:
                        pending_updated += 1
                    else:
                        pending_unchanged += 1

                continue

            ready += 1

            record = (
                existing_by_player_id.get(identity_key)
                if isinstance(identity_key, int)
                else None
            )

            player = entry["player"]

            if player is not None:
                imported_player_ids.add(player.id)

            old_pending = (
                existing_pending_by_steam_id.get(steam_id) if steam_id else None
            )

            if old_pending is not None:
                resolved_pending_steam_ids.add(steam_id)
                pending_removed += 1

                if imported_expires_at is MISSING:
                    expires_at = old_pending.expires_at

            if record is None and player is not None:
                record = existing_by_player_id.get(player.id)

            if record is None:
                created += 1
                continue

            # An omitted expires_at keeps the existing record expiration.
            # The list default is only applied when creating a new record.
            if imported_expires_at is MISSING and old_pending is None:
                expires_at = record.expires_at

            description = entry["description"]

            if (
                not record.active
                or record.expires_at != expires_at
                or record.description != description
                or record.notes != entry["notes"]
            ):
                updated += 1
            else:
                unchanged += 1

        if normalized_mode == "replace":
            for record in existing_records:
                if not record.active:
                    continue

                if record.player_id_id in imported_player_ids:
                    continue

                player_logical_ids = {record.player.player_id}
                if record.player.steam_id:
                    player_logical_ids.add(record.player.steam_id)

                if player_logical_ids & imported_logical_ids:
                    continue

                deactivated += 1

            for pending_record in existing_pending:
                steam_id = pending_record.steam_id

                if steam_id in imported_pending_steam_ids:
                    continue

                if steam_id in imported_logical_ids:
                    continue

                if steam_id in resolved_pending_steam_ids:
                    continue

                pending_removed += 1

        return {
            "vip_list_id": vip_list.id,
            "mode": normalized_mode,
            "total": len(normalized_entries),
            "ready": ready,
            "pending": pending,
            "conflicts": conflicts,
            "skipped": skipped,
            "created": created,
            "updated": updated,
            "unchanged": unchanged,
            "deactivated": deactivated,
            "pending_created": pending_created,
            "pending_updated": pending_updated,
            "pending_unchanged": pending_unchanged,
            "pending_removed": pending_removed,
        }


def import_vip_list_records(
    vip_list_id: int,
    entries: Sequence[dict],
    mode: str = "merge",
    admin_name: str = "CRCON",
    target_game: GameEnum = GameEnum.HLL_WW2,
) -> dict:
    """Atomically import records into one editable VIP list."""
    normalized_mode, normalized_entries = _normalize_vip_list_import(
        entries,
        mode,
    )
    normalized_admin_name = admin_name.strip() or "CRCON"

    with enter_session() as sess:
        # Serialize writes for one VIP list. This also protects identities
        # whose pending row does not exist yet and therefore cannot be locked
        # individually.
        vip_list = sess.scalar(
            select(VipList).where(VipList.id == int(vip_list_id)).with_for_update()
        )
        if vip_list is None:
            raise ValueError(f"VIP list ID {vip_list_id} does not exist")
        _ensure_editable(vip_list)

        resolved_entries = _resolve_vip_import_identities(
            sess,
            normalized_entries,
            target_game,
        )

        existing_records = list(
            sess.scalars(
                select(VipListRecord)
                .where(VipListRecord.vip_list_id == vip_list.id)
                .order_by(VipListRecord.id)
            ).all()
        )
        existing_by_player_id = {
            record.player_id_id: record for record in existing_records
        }

        existing_pending = list(
            sess.scalars(
                select(VipListPendingRecord)
                .where(VipListPendingRecord.vip_list_id == vip_list.id)
                .order_by(VipListPendingRecord.id)
            ).all()
        )
        existing_pending_by_steam_id = {
            record.steam_id: record for record in existing_pending
        }

        ready = 0
        pending = 0
        conflicts = 0
        skipped = 0

        created = 0
        updated = 0
        unchanged = 0
        deactivated = 0

        pending_created = 0
        pending_updated = 0
        pending_unchanged = 0
        pending_removed = 0

        affected_player_ids: set[int] = set()
        imported_player_ids: set[int] = set()
        imported_logical_ids: set[str] = set()
        imported_pending_steam_ids: set[str] = set()
        removed_pending_steam_ids: set[str] = set()

        for identity_key, entry in resolved_entries.items():
            status = entry["resolution_status"]
            steam_id = entry.get("steam_id")
            resolved_player_id = entry["resolved_player_id"]

            if status == "skipped":
                skipped += 1
                continue

            if steam_id:
                imported_logical_ids.add(steam_id)
            imported_logical_ids.add(resolved_player_id)

            imported_expires_at = entry["expires_at"]
            expires_at = imported_expires_at
            if expires_at is MISSING:
                expires_at = _list_expiration(vip_list)

            if status in {"pending", "conflict"}:
                if not steam_id:
                    raise RuntimeError("Pending VIP import identity has no Steam ID")

                if status == "pending":
                    pending += 1
                else:
                    conflicts += 1

                imported_pending_steam_ids.add(steam_id)
                pending_record = existing_pending_by_steam_id.get(steam_id)

                # Keep the originally calculated list expiration while an
                # identity remains pending. An omitted expires_at must not
                # extend the VIP on every repeated import.
                if pending_record is not None and imported_expires_at is MISSING:
                    expires_at = pending_record.expires_at

                if pending_record is None:
                    pending_record = VipListPendingRecord(
                        vip_list=vip_list,
                        steam_id=steam_id,
                        admin_name=normalized_admin_name,
                        description=entry["description"],
                        notes=entry["notes"],
                        expires_at=expires_at,
                        resolution_error=entry["resolution_error"],
                    )
                    sess.add(pending_record)
                    existing_pending_by_steam_id[steam_id] = pending_record
                    pending_created += 1
                else:
                    changed = (
                        pending_record.expires_at != expires_at
                        or pending_record.description != entry["description"]
                        or pending_record.notes != entry["notes"]
                        or pending_record.resolution_error != entry["resolution_error"]
                    )

                    if changed:
                        pending_record.expires_at = expires_at
                        pending_record.description = entry["description"]
                        pending_record.notes = entry["notes"]
                        pending_record.resolution_error = entry["resolution_error"]
                        pending_record.admin_name = normalized_admin_name
                        pending_record.last_checked_at = datetime.now(tz=UTC)
                        pending_updated += 1
                    else:
                        pending_unchanged += 1

                continue

            ready += 1

            record = (
                existing_by_player_id.get(identity_key)
                if isinstance(identity_key, int)
                else None
            )

            player = entry["player"]
            if player is None:
                player = _get_or_create_import_player(
                    sess,
                    resolved_player_id,
                )
                if player is None:
                    raise RuntimeError(
                        "Unable to create PlayerID database record for "
                        f"{resolved_player_id}"
                    )
                entry["player"] = player

            imported_player_ids.add(player.id)

            old_pending = None
            if steam_id:
                old_pending = existing_pending_by_steam_id.pop(
                    steam_id,
                    None,
                )

                # When a pending identity becomes resolvable, preserve its
                # original expiration unless the import explicitly supplies
                # a new expires_at value.
                if old_pending is not None and imported_expires_at is MISSING:
                    expires_at = old_pending.expires_at

                if old_pending is not None:
                    sess.delete(old_pending)
                    removed_pending_steam_ids.add(steam_id)
                    pending_removed += 1

            if record is None:
                record = existing_by_player_id.get(player.id)

            if record is None:
                record = VipListRecord(
                    player=player,
                    vip_list=vip_list,
                    admin_name=normalized_admin_name,
                    active=True,
                    description=entry["description"],
                    notes=entry["notes"],
                    expires_at=expires_at,
                )
                sess.add(record)
                existing_by_player_id[player.id] = record
                affected_player_ids.add(player.id)
                created += 1
                continue

            # An omitted expires_at keeps the existing record expiration.
            # The list default is only applied when creating a new record.
            if imported_expires_at is MISSING and old_pending is None:
                expires_at = record.expires_at

            description = entry["description"]

            changed = (
                not record.active
                or record.expires_at != expires_at
                or record.description != description
                or record.notes != entry["notes"]
            )

            if changed:
                record.active = True
                record.expires_at = expires_at
                record.description = description
                record.notes = entry["notes"]
                record.admin_name = normalized_admin_name
                affected_player_ids.add(record.player_id_id)
                updated += 1
            else:
                unchanged += 1

        if normalized_mode == "replace":
            for record in existing_records:
                if not record.active:
                    continue

                if record.player_id_id in imported_player_ids:
                    continue

                player_logical_ids = {record.player.player_id}
                if record.player.steam_id:
                    player_logical_ids.add(record.player.steam_id)

                if player_logical_ids & imported_logical_ids:
                    continue

                record.active = False
                record.admin_name = normalized_admin_name
                affected_player_ids.add(record.player_id_id)
                deactivated += 1

            for pending_record in existing_pending:
                if pending_record.steam_id in imported_pending_steam_ids:
                    continue

                # A pending identity may have resolved during this import.
                if pending_record.steam_id in imported_logical_ids:
                    continue

                if pending_record.steam_id in removed_pending_steam_ids:
                    continue

                sess.delete(pending_record)
                removed_pending_steam_ids.add(pending_record.steam_id)
                pending_removed += 1

        if affected_player_ids:
            sess.flush()
            reconcile_vip_list_flags(sess, affected_player_ids)

        sess.commit()

        result = {
            "vip_list_id": vip_list.id,
            "mode": normalized_mode,
            "total": len(normalized_entries),
            "ready": ready,
            "pending": pending,
            "conflicts": conflicts,
            "skipped": skipped,
            "created": created,
            "updated": updated,
            "unchanged": unchanged,
            "deactivated": deactivated,
            "pending_created": pending_created,
            "pending_updated": pending_updated,
            "pending_unchanged": pending_unchanged,
            "pending_removed": pending_removed,
        }

        if (
            created
            or updated
            or deactivated
            or pending_created
            or pending_updated
            or pending_removed
        ):
            logger.info(
                "Imported %s VIP record(s) into list ID %s: "
                "%s ready, %s pending, %s conflicts, "
                "%s created, %s updated, %s unchanged, "
                "%s deactivated, %s pending created, "
                "%s pending updated, %s pending removed",
                len(normalized_entries),
                vip_list.id,
                ready,
                pending,
                conflicts,
                created,
                updated,
                unchanged,
                deactivated,
                pending_created,
                pending_updated,
                pending_removed,
            )

        if created or updated or deactivated:
            _notify_vip_sync(vip_list.servers)

        return result


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


def delete_pending_vip_record(record_id: int) -> bool:
    """Delete one unresolved VIP list record without gameserver synchronization."""
    with enter_session() as sess:
        record = sess.get(VipListPendingRecord, int(record_id))
        if record is None:
            return False

        vip_list_id = record.vip_list_id
        steam_id = record.steam_id
        sess.delete(record)
        sess.commit()

        logger.info(
            "Deleted pending VIP list record ID %s from list %s for Steam ID %s",
            record_id,
            vip_list_id,
            steam_id,
        )
        return True


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


def get_player_legacy_vip_statuses(
    sess: Session,
    player_id: str,
    timestamp: datetime | None = None,
) -> list[dict]:
    """Build legacy per-server VIP status from VIP List records.

    Only active, non-expired records for the requested player are considered.
    If multiple applicable lists grant VIP on the same server, the same
    expiration/creation priority as get_effective_vip_records() is used.
    """
    timestamp = timestamp or datetime.now(tz=UTC)

    records = sess.scalars(
        select(VipListRecord)
        .join(VipListRecord.player)
        .where(
            PlayerID.player_id == player_id,
            VipListRecord.active.is_(True),
            or_(
                VipListRecord.expires_at.is_(None),
                VipListRecord.expires_at > timestamp,
            ),
        )
    ).all()

    configured_server_numbers = set(
        sess.scalars(select(VipListDefault.server_number)).all()
    )

    effective: dict[int, VipListRecord] = {}

    for record in records:
        vip_list = record.vip_list
        server_numbers = (
            configured_server_numbers
            if vip_list.servers is None
            else vip_list.get_server_numbers()
        )

        for server_number in server_numbers:
            current = effective.get(server_number)
            if current is None:
                effective[server_number] = record
                continue

            if current.expires_at == record.expires_at:
                if record.created_at > current.created_at:
                    effective[server_number] = record
            elif record.expires_at is None or (
                current.expires_at is not None
                and record.expires_at > current.expires_at
            ):
                effective[server_number] = record

    return [
        {
            "server_number": server_number,
            "expiration": record.expires_at,
        }
        for server_number, record in sorted(effective.items())
    ]


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

"""Read-only adapters for building VIP synchronization plans."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.orm import Session

from rcon.models import VipListRecord, enter_session
from rcon.types import VipIdType, VipListSyncMethod
from rcon.vip import get_vip_lists_for_server
from rcon.vip_sync import VipSyncPlan, VipSyncRecord, build_vip_sync_plan


class VipSyncDatabaseUnavailableError(RuntimeError):
    """Raised when the VIP List database schema is unavailable."""


class VipRconReader(Protocol):
    def get_vip_ids(self) -> Sequence[VipIdType]: ...


def get_record_player_name(record: VipListRecord) -> str:
    """Return the most recently seen player name for a VIP record."""
    if record.player.names:
        return record.player.names[0].name
    return ""


def database_record_to_sync_record(record: VipListRecord) -> VipSyncRecord:
    """Convert a database VIP record into the pure planner representation."""
    return VipSyncRecord(
        player_id=record.player.player_id,
        player_name=get_record_player_name(record),
        description=record.description,
        active=record.active,
        created_at=record.created_at,
        expires_at=record.expires_at,
    )


def load_database_sync_state(
    sess: Session,
    server_number: int,
) -> tuple[list[VipSyncRecord], list[VipListSyncMethod]]:
    """Load all VIP records and sync modes applicable to one server."""
    vip_lists = get_vip_lists_for_server(
        sess,
        server_number=server_number,
    )

    records = [
        database_record_to_sync_record(record)
        for vip_list in vip_lists
        for record in vip_list.records
    ]
    sync_methods = [vip_list.sync for vip_list in vip_lists]

    return records, sync_methods


def read_gameserver_vips(
    rcon: VipRconReader,
) -> dict[str, str]:
    """Read the current VIP IDs and comments from a gameserver."""
    return {vip["player_id"]: vip.get("name", "") or "" for vip in rcon.get_vip_ids()}


def build_database_vip_sync_plan(
    gameserver_vips: Mapping[str, str],
    server_number: int,
    timestamp: datetime | None = None,
) -> VipSyncPlan:
    """Build a synchronization plan from database state without RCON writes."""
    timestamp = timestamp or datetime.now(tz=UTC)
    records: list[VipSyncRecord] | None = None
    sync_methods: list[VipListSyncMethod] | None = None

    with enter_session() as sess:
        records, sync_methods = load_database_sync_state(
            sess,
            server_number=server_number,
        )

    if records is None or sync_methods is None:
        raise VipSyncDatabaseUnavailableError(
            "VIP List tables are unavailable; apply database migrations first."
        )

    return build_vip_sync_plan(
        gameserver_vips=gameserver_vips,
        records=records,
        sync_methods=sync_methods,
        timestamp=timestamp,
    )


def plan_gameserver_vip_sync(
    server_number: int,
    rcon: VipRconReader | None = None,
    timestamp: datetime | None = None,
) -> VipSyncPlan:
    """Read a gameserver and return its proposed VIP changes without applying."""
    if rcon is None:
        from rcon.api_commands import get_rcon_api

        rcon = get_rcon_api()

    gameserver_vips = read_gameserver_vips(rcon)

    return build_database_vip_sync_plan(
        gameserver_vips=gameserver_vips,
        server_number=server_number,
        timestamp=timestamp,
    )

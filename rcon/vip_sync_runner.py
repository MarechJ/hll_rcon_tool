"""Orchestration for VIP synchronization runs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from rcon.vip_sync import VipSyncPlan
from rcon.vip_sync_executor import (
    VipRconWriter,
    VipSyncExecutionResult,
    execute_vip_sync_plan,
)
from rcon.vip_sync_service import (
    VipRconReader,
    build_database_vip_sync_plan,
    read_gameserver_vips,
)


class VipRconClient(VipRconReader, VipRconWriter, Protocol):
    pass


@dataclass(frozen=True)
class VipSyncRunResult:
    plan: VipSyncPlan
    execution: VipSyncExecutionResult


def synchronize_gameserver_vips(
    server_number: int,
    rcon: VipRconClient | None = None,
    timestamp: datetime | None = None,
    dry_run: bool = True,
) -> VipSyncRunResult:
    """Read, plan and optionally apply VIP synchronization."""
    if rcon is None:
        from rcon.api_commands import get_rcon_api

        rcon = get_rcon_api()

    gameserver_vips = read_gameserver_vips(rcon)
    plan = build_database_vip_sync_plan(
        gameserver_vips=gameserver_vips,
        server_number=server_number,
        timestamp=timestamp,
    )
    execution = execute_vip_sync_plan(
        plan=plan,
        rcon=rcon,
        dry_run=dry_run,
    )

    return VipSyncRunResult(
        plan=plan,
        execution=execution,
    )

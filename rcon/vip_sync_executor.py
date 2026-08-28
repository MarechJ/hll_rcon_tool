"""Execution of previously calculated VIP synchronization plans."""

from dataclasses import dataclass
from logging import getLogger
from typing import Literal, Protocol

from rcon.vip_sync import VipSyncAdd, VipSyncPlan


logger = getLogger(__name__)


class VipRconWriter(Protocol):
    def add_vip_to_gameserver(
        self,
        player_id: str,
        description: str,
    ) -> bool: ...

    def remove_vip_from_gameserver(
        self,
        player_id: str,
    ) -> bool: ...


@dataclass(frozen=True)
class VipSyncFailure:
    action: Literal["add", "remove"]
    player_id: str
    error: str


@dataclass(frozen=True)
class VipSyncExecutionResult:
    dry_run: bool
    added: frozenset[str]
    removed: frozenset[str]
    skipped_additions: tuple[VipSyncAdd, ...]
    skipped_removals: frozenset[str]
    failures: tuple[VipSyncFailure, ...]

    @property
    def successful(self) -> bool:
        return not self.failures


def execute_vip_sync_plan(
    plan: VipSyncPlan,
    rcon: VipRconWriter,
    dry_run: bool = True,
) -> VipSyncExecutionResult:
    """Execute a VIP plan, defaulting to a side-effect-free dry-run."""
    if dry_run:
        logger.info(
            "VIP synchronization dry-run: %s additions, %s removals",
            len(plan.to_add),
            len(plan.to_remove),
        )
        return VipSyncExecutionResult(
            dry_run=True,
            added=frozenset(),
            removed=frozenset(),
            skipped_additions=plan.to_add,
            skipped_removals=plan.to_remove,
            failures=(),
        )

    added: set[str] = set()
    removed: set[str] = set()
    failures: list[VipSyncFailure] = []

    # Additions are intentionally attempted before removals.
    for item in plan.to_add:
        logger.info(
            "Adding VIP on gameserver: %s (%s)",
            item.player_id,
            item.description,
        )
        try:
            result = rcon.add_vip_to_gameserver(
                player_id=item.player_id,
                description=item.description,
            )
            if result:
                added.add(item.player_id)
            else:
                failures.append(
                    VipSyncFailure(
                        action="add",
                        player_id=item.player_id,
                        error="Gameserver returned False",
                    )
                )
        except Exception as exc:
            logger.exception(
                "Failed to add VIP on gameserver for %s",
                item.player_id,
            )
            failures.append(
                VipSyncFailure(
                    action="add",
                    player_id=item.player_id,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    for player_id in sorted(plan.to_remove):
        logger.info("Removing VIP from gameserver: %s", player_id)
        try:
            result = rcon.remove_vip_from_gameserver(
                player_id=player_id,
            )
            if result:
                removed.add(player_id)
            else:
                failures.append(
                    VipSyncFailure(
                        action="remove",
                        player_id=player_id,
                        error="Gameserver returned False",
                    )
                )
        except Exception as exc:
            logger.exception(
                "Failed to remove VIP on gameserver for %s",
                player_id,
            )
            failures.append(
                VipSyncFailure(
                    action="remove",
                    player_id=player_id,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    return VipSyncExecutionResult(
        dry_run=False,
        added=frozenset(added),
        removed=frozenset(removed),
        skipped_additions=(),
        skipped_removals=frozenset(),
        failures=tuple(failures),
    )

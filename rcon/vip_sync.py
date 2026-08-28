"""Pure planning logic for synchronizing VIP lists with a gameserver."""

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from rcon.types import VipListSyncMethod


@dataclass(frozen=True)
class VipSyncRecord:
    player_id: str
    player_name: str
    description: str | None
    active: bool
    created_at: datetime
    expires_at: datetime | None


@dataclass(frozen=True)
class VipSyncAdd:
    player_id: str
    description: str


@dataclass(frozen=True)
class VipSyncPlan:
    to_add: tuple[VipSyncAdd, ...]
    to_remove: frozenset[str]
    unchanged: frozenset[str]
    unknown: frozenset[str]


def is_active_vip_record(record: VipSyncRecord, timestamp: datetime) -> bool:
    """Return whether a record currently grants VIP access."""
    return record.active and (
        record.expires_at is None or record.expires_at > timestamp
    )


def is_higher_priority_record(
    record: VipSyncRecord,
    other: VipSyncRecord,
) -> bool:
    """Return whether record has higher priority than other."""
    if record.expires_at == other.expires_at:
        return record.created_at > other.created_at
    if record.expires_at is None:
        return True
    if other.expires_at is None:
        return False
    return record.expires_at > other.expires_at


def get_highest_priority_record(
    records: Sequence[VipSyncRecord],
) -> VipSyncRecord | None:
    """Return the highest-priority record, or None for an empty sequence."""
    if not records:
        return None

    highest = records[0]
    for record in records[1:]:
        if is_higher_priority_record(record, highest):
            highest = record
    return highest


def get_gameserver_description(record: VipSyncRecord) -> str:
    """Build the public description sent to the gameserver."""
    player_name = record.player_name.strip() or "NO NAME IN CRCON"
    description = (record.description or "").strip()

    if description:
        return f"{player_name} - {description}"
    return player_name


def build_vip_sync_plan(
    gameserver_vips: Mapping[str, str],
    records: Iterable[VipSyncRecord],
    sync_methods: Iterable[VipListSyncMethod],
    timestamp: datetime,
) -> VipSyncPlan:
    """Calculate VIP additions, updates and removals without side effects."""
    records_by_player: defaultdict[str, list[VipSyncRecord]] = defaultdict(list)

    for record in records:
        records_by_player[record.player_id].append(record)

    sync_methods = tuple(sync_methods)
    remove_unknown = bool(sync_methods) and all(
        method == VipListSyncMethod.REMOVE_UNKNOWN for method in sync_methods
    )

    to_add: list[VipSyncAdd] = []
    to_remove: set[str] = set()
    unchanged: set[str] = set()

    for player_id, player_records in records_by_player.items():
        active_records = [
            record
            for record in player_records
            if is_active_vip_record(record, timestamp)
        ]
        top_record = get_highest_priority_record(active_records)

        if top_record is None:
            if player_id in gameserver_vips:
                to_remove.add(player_id)
            continue

        expected_description = get_gameserver_description(top_record)
        current_description = gameserver_vips.get(player_id)

        if current_description is None:
            to_add.append(
                VipSyncAdd(
                    player_id=player_id,
                    description=expected_description,
                )
            )
        elif current_description and current_description != expected_description:
            to_add.append(
                VipSyncAdd(
                    player_id=player_id,
                    description=expected_description,
                )
            )
        else:
            unchanged.add(player_id)

    unknown = frozenset(set(gameserver_vips) - set(records_by_player))
    if remove_unknown:
        to_remove.update(unknown)

    return VipSyncPlan(
        to_add=tuple(sorted(to_add, key=lambda item: item.player_id)),
        to_remove=frozenset(to_remove),
        unchanged=frozenset(unchanged),
        unknown=unknown,
    )

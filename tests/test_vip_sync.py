from datetime import UTC, datetime, timedelta

from rcon.types import VipListSyncMethod
from rcon.vip_sync import (
    VipSyncAdd,
    VipSyncRecord,
    build_vip_sync_plan,
)

NOW = datetime(2030, 1, 1, tzinfo=UTC)


def record(
    player_id: str,
    *,
    player_name: str = "Player",
    description: str | None = None,
    active: bool = True,
    created_at: datetime = NOW,
    expires_at: datetime | None = None,
) -> VipSyncRecord:
    return VipSyncRecord(
        player_id=player_id,
        player_name=player_name,
        description=description,
        active=active,
        created_at=created_at,
        expires_at=expires_at,
    )


def plan(
    gameserver_vips,
    records,
    sync_mode=VipListSyncMethod.IGNORE_UNKNOWN,
):
    return build_vip_sync_plan(
        gameserver_vips=gameserver_vips,
        records=records,
        sync_mode=sync_mode,
        timestamp=NOW,
    )


def test_adds_missing_active_vip():
    result = plan({}, [record("player-1", description="Supporter")])

    assert result.to_add == (VipSyncAdd("player-1", "Player - Supporter"),)
    assert result.to_remove == frozenset()


def test_empty_hllv_comment_is_accepted_as_unchanged():
    result = plan(
        {"player-1": ""},
        [record("player-1", description="Supporter")],
    )

    assert result.to_add == ()
    assert result.unchanged == frozenset({"player-1"})


def test_nonempty_mismatched_hll_comment_is_updated():
    result = plan(
        {"player-1": "Old comment"},
        [record("player-1", description="Supporter")],
    )

    assert result.to_add == (VipSyncAdd("player-1", "Player - Supporter"),)


def test_inactive_and_expired_records_remove_existing_vips():
    result = plan(
        {
            "inactive": "",
            "expired": "",
        },
        [
            record("inactive", active=False),
            record("expired", expires_at=NOW - timedelta(seconds=1)),
        ],
    )

    assert result.to_remove == frozenset({"inactive", "expired"})


def test_ignore_unknown_keeps_unknown_gameserver_vip():
    result = plan(
        {"unknown": "External VIP"},
        [],
        VipListSyncMethod.IGNORE_UNKNOWN,
    )

    assert result.to_remove == frozenset()
    assert result.unknown == frozenset({"unknown"})


def test_server_mode_controls_unknown_removal_with_multiple_lists():
    result = plan(
        {"unknown": "External VIP"},
        [record("managed")],
        VipListSyncMethod.REMOVE_UNKNOWN,
    )

    assert result.to_remove == frozenset({"unknown"})


def test_default_server_mode_keeps_unknown_without_lists():
    result = plan(
        {"unknown": "External VIP"},
        [],
        VipListSyncMethod.IGNORE_UNKNOWN,
    )

    assert result.to_remove == frozenset()


def test_indefinite_record_has_priority_over_finite_record():
    result = plan(
        {},
        [
            record(
                "player-1",
                description="Finite",
                created_at=NOW,
                expires_at=NOW + timedelta(days=30),
            ),
            record(
                "player-1",
                description="Indefinite",
                created_at=NOW - timedelta(days=1),
                expires_at=None,
            ),
        ],
    )

    assert result.to_add == (VipSyncAdd("player-1", "Player - Indefinite"),)


def test_inactive_indefinite_record_does_not_override_active_record():
    result = plan(
        {},
        [
            record(
                "player-1",
                description="Inactive indefinite",
                active=False,
                created_at=NOW + timedelta(days=1),
                expires_at=None,
            ),
            record(
                "player-1",
                description="Active finite",
                active=True,
                expires_at=NOW + timedelta(days=30),
            ),
        ],
    )

    assert result.to_add == (VipSyncAdd("player-1", "Player - Active finite"),)


def test_later_expiration_has_priority_over_earlier_expiration():
    result = plan(
        {},
        [
            record(
                "player-1",
                description="Earlier",
                created_at=NOW + timedelta(days=1),
                expires_at=NOW + timedelta(days=10),
            ),
            record(
                "player-1",
                description="Later",
                created_at=NOW,
                expires_at=NOW + timedelta(days=30),
            ),
        ],
    )

    assert result.to_add == (VipSyncAdd("player-1", "Player - Later"),)


def test_newer_record_wins_when_expiration_is_equal():
    expiration = NOW + timedelta(days=30)

    result = plan(
        {},
        [
            record(
                "player-1",
                description="Older",
                created_at=NOW,
                expires_at=expiration,
            ),
            record(
                "player-1",
                description="Newer",
                created_at=NOW + timedelta(seconds=1),
                expires_at=expiration,
            ),
        ],
    )

    assert result.to_add == (VipSyncAdd("player-1", "Player - Newer"),)


def test_missing_player_name_uses_safe_fallback():
    result = plan(
        {},
        [
            record(
                "player-1",
                player_name="",
                description="Supporter",
            )
        ],
    )

    assert result.to_add == (VipSyncAdd("player-1", "NO NAME IN CRCON - Supporter"),)


def test_inactive_known_record_is_not_classified_as_unknown():
    result = plan(
        {"known": ""},
        [record("known", active=False)],
        (VipListSyncMethod.REMOVE_UNKNOWN,),
    )

    assert result.to_remove == frozenset({"known"})
    assert result.unknown == frozenset()

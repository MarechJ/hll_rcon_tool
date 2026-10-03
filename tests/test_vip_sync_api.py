import pytest

from rcon.api_commands import RconAPI
from rcon.vip_sync import VipSyncAdd, VipSyncPlan
from rcon.vip_sync_executor import (
    VipSyncExecutionResult,
    VipSyncFailure,
)
from rcon.vip_sync_runner import VipSyncRunResult


def test_vip_sync_api_preview_and_apply(monkeypatch):
    calls = []

    plan = VipSyncPlan(
        to_add=(
            VipSyncAdd(
                player_id="player-add",
                description="Player Add - API test",
            ),
        ),
        to_remove=frozenset({"player-remove"}),
        unchanged=frozenset({"player-unchanged"}),
        unknown=frozenset({"player-unknown"}),
    )

    def fake_synchronize_gameserver_vips(
        server_number,
        rcon,
        timestamp=None,
        dry_run=True,
        trigger="manual",
    ):
        calls.append(
            {
                "server_number": server_number,
                "rcon": rcon,
                "timestamp": timestamp,
                "dry_run": dry_run,
                "trigger": trigger,
            }
        )

        if dry_run:
            execution = VipSyncExecutionResult(
                dry_run=True,
                added=frozenset(),
                removed=frozenset(),
                skipped_additions=plan.to_add,
                skipped_removals=plan.to_remove,
                failures=(),
            )
        else:
            execution = VipSyncExecutionResult(
                dry_run=False,
                added=frozenset({"player-add"}),
                removed=frozenset(),
                skipped_additions=(),
                skipped_removals=frozenset(),
                failures=(
                    VipSyncFailure(
                        action="remove",
                        player_id="player-remove",
                        error="Gameserver returned False",
                    ),
                ),
            )

        return VipSyncRunResult(
            plan=plan,
            execution=execution,
        )

    monkeypatch.setattr(
        "rcon.vip_sync_runner.synchronize_gameserver_vips",
        fake_synchronize_gameserver_vips,
    )

    api = object.__new__(RconAPI)

    preview = api.get_vip_sync_plan(server_number=5)

    assert preview == {
        "plan": {
            "to_add": [
                {
                    "player_id": "player-add",
                    "description": "Player Add - API test",
                }
            ],
            "to_remove": ["player-remove"],
            "unchanged": ["player-unchanged"],
            "unknown": ["player-unknown"],
        },
        "execution": {
            "dry_run": True,
            "added": [],
            "removed": [],
            "skipped_additions": [
                {
                    "player_id": "player-add",
                    "description": "Player Add - API test",
                }
            ],
            "skipped_removals": ["player-remove"],
            "failures": [],
            "successful": True,
        },
    }

    applied = api.synchronize_vip_lists(server_number=5)

    assert applied["plan"] == preview["plan"]
    assert applied["execution"] == {
        "dry_run": False,
        "added": ["player-add"],
        "removed": [],
        "skipped_additions": [],
        "skipped_removals": [],
        "failures": [
            {
                "action": "remove",
                "player_id": "player-remove",
                "error": "Gameserver returned False",
            }
        ],
        "successful": False,
    }

    assert calls == [
        {
            "server_number": 5,
            "rcon": api,
            "timestamp": None,
            "dry_run": True,
            "trigger": "manual",
        },
        {
            "server_number": 5,
            "rcon": api,
            "timestamp": None,
            "dry_run": False,
            "trigger": "manual",
        },
    ]


def _make_dry_run_result(plan):
    return VipSyncRunResult(
        plan=plan,
        execution=VipSyncExecutionResult(
            dry_run=True,
            added=frozenset(),
            removed=frozenset(),
            skipped_additions=plan.to_add,
            skipped_removals=plan.to_remove,
            failures=(),
        ),
    )


def test_get_vip_sync_status_returns_persisted_status(monkeypatch):
    expected = {
        "server_number": 4,
        "state": "successful",
        "trigger": "periodic",
        "started_at": "2026-08-30T10:00:00+00:00",
        "completed_at": "2026-08-30T10:00:01+00:00",
        "last_success_at": "2026-08-30T10:00:01+00:00",
        "added": 1,
        "removed": 2,
        "failures": [],
    }

    monkeypatch.setattr(
        "rcon.vip_sync_status.get_vip_sync_status",
        lambda server_number: expected if server_number == 4 else None,
    )

    api = object.__new__(RconAPI)

    assert api.get_vip_sync_status(server_number=4) == expected


def test_get_vip_sync_status_reports_never_without_record(monkeypatch):
    monkeypatch.setattr(
        "rcon.vip_sync_status.get_vip_sync_status",
        lambda server_number: None,
    )

    api = object.__new__(RconAPI)
    status = api.get_vip_sync_status(server_number=6)

    assert status == {
        "server_number": 6,
        "state": "never",
        "trigger": None,
        "started_at": None,
        "completed_at": None,
        "last_success_at": None,
        "added": 0,
        "removed": 0,
        "failures": [],
    }


def test_remove_unknown_vip_from_gameserver(monkeypatch):
    target_id = "unknown-player"
    removed = []
    calls = []

    before = VipSyncPlan(
        to_add=(),
        to_remove=frozenset(),
        unchanged=frozenset({"managed-player"}),
        unknown=frozenset({target_id}),
    )
    after = VipSyncPlan(
        to_add=(),
        to_remove=frozenset(),
        unchanged=frozenset({"managed-player"}),
        unknown=frozenset(),
    )

    results = iter(
        (
            _make_dry_run_result(before),
            _make_dry_run_result(after),
        )
    )

    def fake_synchronize_gameserver_vips(**kwargs):
        calls.append(kwargs)
        return next(results)

    def fake_remove(self, player_id):
        removed.append(player_id)
        return True

    monkeypatch.setattr(
        "rcon.vip_sync_runner.synchronize_gameserver_vips",
        fake_synchronize_gameserver_vips,
    )
    monkeypatch.setattr(
        RconAPI,
        "remove_vip_from_gameserver",
        fake_remove,
        raising=False,
    )

    api = object.__new__(RconAPI)
    result = api.remove_unknown_vip_from_gameserver(
        player_id=f"  {target_id}  ",
        server_number=3,
    )

    assert removed == [target_id]
    assert result == {
        "player_id": target_id,
        "removed": True,
        "plan": {
            "to_add": [],
            "to_remove": [],
            "unchanged": ["managed-player"],
            "unknown": [],
        },
    }
    assert calls == [
        {
            "server_number": 3,
            "rcon": api,
            "dry_run": True,
        },
        {
            "server_number": 3,
            "rcon": api,
            "dry_run": True,
        },
    ]


def test_remove_unknown_vip_rejects_managed_entry(monkeypatch):
    removals = []

    plan = VipSyncPlan(
        to_add=(),
        to_remove=frozenset(),
        unchanged=frozenset({"managed-player"}),
        unknown=frozenset(),
    )

    monkeypatch.setattr(
        "rcon.vip_sync_runner.synchronize_gameserver_vips",
        lambda **kwargs: _make_dry_run_result(plan),
    )

    def fake_remove(self, player_id):
        removals.append(player_id)
        return True

    monkeypatch.setattr(
        RconAPI,
        "remove_vip_from_gameserver",
        fake_remove,
        raising=False,
    )

    api = object.__new__(RconAPI)

    with pytest.raises(
        ValueError,
        match="not an unknown gameserver entry",
    ):
        api.remove_unknown_vip_from_gameserver(
            player_id="managed-player",
            server_number=3,
        )

    assert removals == []


def test_remove_unknown_vip_rejects_empty_player_id():
    api = object.__new__(RconAPI)

    with pytest.raises(
        ValueError,
        match="Player ID must not be empty",
    ):
        api.remove_unknown_vip_from_gameserver(
            player_id="   ",
            server_number=1,
        )

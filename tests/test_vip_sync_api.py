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
    ):
        calls.append(
            {
                "server_number": server_number,
                "rcon": rcon,
                "timestamp": timestamp,
                "dry_run": dry_run,
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
        },
        {
            "server_number": 5,
            "rcon": api,
            "timestamp": None,
            "dry_run": False,
        },
    ]

from datetime import datetime

import rcon.vip_sync_status as status_module
from rcon.vip_sync_executor import (
    VipSyncExecutionResult,
    VipSyncFailure,
)


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.closed = False

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value
        return True

    def close(self):
        self.closed = True


def make_execution(*, successful=True):
    failures = (
        ()
        if successful
        else (
            VipSyncFailure(
                action="remove",
                player_id="failed-player",
                error="Gameserver returned False",
            ),
        )
    )

    return VipSyncExecutionResult(
        dry_run=False,
        added=frozenset({"added-player"}) if successful else frozenset(),
        removed=frozenset({"removed-player"}) if successful else frozenset(),
        skipped_additions=(),
        skipped_removals=frozenset(),
        failures=failures,
    )


def assert_timestamp(value):
    assert value is not None
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None


def test_records_started_and_successful_sync(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(status_module, "_get_redis", lambda: fake_redis)

    status_module.record_vip_sync_started(
        server_number=2,
        trigger="notification",
    )

    running = status_module.get_vip_sync_status(2)

    assert running["server_number"] == 2
    assert running["state"] == "running"
    assert running["trigger"] == "notification"
    assert running["completed_at"] is None
    assert running["last_success_at"] is None
    assert_timestamp(running["started_at"])

    status_module.record_vip_sync_completed(
        server_number=2,
        trigger="notification",
        execution=make_execution(successful=True),
    )

    completed = status_module.get_vip_sync_status(2)

    assert completed["state"] == "successful"
    assert completed["trigger"] == "notification"
    assert completed["started_at"] == running["started_at"]
    assert completed["added"] == 1
    assert completed["removed"] == 1
    assert completed["failures"] == []
    assert_timestamp(completed["completed_at"])
    assert completed["last_success_at"] == completed["completed_at"]


def test_failed_sync_preserves_last_success(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(status_module, "_get_redis", lambda: fake_redis)

    status_module.record_vip_sync_started(1, "startup")
    status_module.record_vip_sync_completed(
        server_number=1,
        trigger="startup",
        execution=make_execution(successful=True),
    )

    successful = status_module.get_vip_sync_status(1)

    status_module.record_vip_sync_started(1, "periodic")
    status_module.record_vip_sync_completed(
        server_number=1,
        trigger="periodic",
        execution=make_execution(successful=False),
    )

    failed = status_module.get_vip_sync_status(1)

    assert failed["state"] == "failed"
    assert failed["trigger"] == "periodic"
    assert failed["last_success_at"] == successful["last_success_at"]
    assert failed["added"] == 0
    assert failed["removed"] == 0
    assert failed["failures"] == [
        {
            "action": "remove",
            "player_id": "failed-player",
            "error": "Gameserver returned False",
        }
    ]


def test_records_failure_before_plan_execution(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(status_module, "_get_redis", lambda: fake_redis)

    status_module.record_vip_sync_started(3, "manual")
    status_module.record_vip_sync_failed(
        server_number=3,
        trigger="manual",
        error=RuntimeError("RCON unavailable"),
    )

    failed = status_module.get_vip_sync_status(3)

    assert failed["state"] == "failed"
    assert failed["trigger"] == "manual"
    assert failed["added"] == 0
    assert failed["removed"] == 0
    assert failed["failures"] == [
        {
            "action": "synchronize",
            "player_id": None,
            "error": "RuntimeError: RCON unavailable",
        }
    ]
    assert_timestamp(failed["completed_at"])


def test_status_write_failure_does_not_break_sync(monkeypatch):
    def unavailable_redis():
        raise ConnectionError("Redis unavailable")

    monkeypatch.setattr(
        status_module,
        "_get_redis",
        unavailable_redis,
    )

    status_module.record_vip_sync_started(1, "periodic")
    status_module.record_vip_sync_completed(
        server_number=1,
        trigger="periodic",
        execution=make_execution(successful=True),
    )
    status_module.record_vip_sync_failed(
        server_number=1,
        trigger="periodic",
        error=RuntimeError("RCON unavailable"),
    )

from datetime import UTC, datetime

from rcon.vip_sync import VipSyncAdd, VipSyncPlan
from rcon.vip_sync_runner import synchronize_gameserver_vips

NOW = datetime(2030, 1, 1, tzinfo=UTC)


def make_plan():
    return VipSyncPlan(
        to_add=(VipSyncAdd("add-1", "Player"),),
        to_remove=frozenset({"remove-1"}),
        unchanged=frozenset({"unchanged-1"}),
        unknown=frozenset(),
    )


class FakeRcon:
    def __init__(self):
        self.calls = []

    def get_vip_ids(self):
        self.calls.append(("get",))
        return [
            {
                "player_id": "unchanged-1",
                "name": "",
                "vip_expiration": None,
            }
        ]

    def add_vip_to_gameserver(self, player_id, description):
        self.calls.append(("add", player_id, description))
        return True

    def remove_vip_from_gameserver(self, player_id):
        self.calls.append(("remove", player_id))
        return True


def test_runner_defaults_to_read_only_dry_run(monkeypatch):
    captured = {}

    def fake_build_plan(gameserver_vips, server_number, timestamp):
        captured["gameserver_vips"] = gameserver_vips
        captured["server_number"] = server_number
        captured["timestamp"] = timestamp
        return make_plan()

    monkeypatch.setattr(
        "rcon.vip_sync_runner.build_database_vip_sync_plan",
        fake_build_plan,
    )

    rcon = FakeRcon()
    result = synchronize_gameserver_vips(
        server_number=2,
        rcon=rcon,
        timestamp=NOW,
    )

    assert result.execution.dry_run is True
    assert result.execution.added == frozenset()
    assert result.execution.removed == frozenset()
    assert rcon.calls == [("get",)]
    assert captured == {
        "gameserver_vips": {"unchanged-1": ""},
        "server_number": 2,
        "timestamp": NOW,
    }


def test_runner_applies_only_when_explicitly_enabled(monkeypatch):
    monkeypatch.setattr(
        "rcon.vip_sync_runner.build_database_vip_sync_plan",
        lambda **kwargs: make_plan(),
    )

    rcon = FakeRcon()
    result = synchronize_gameserver_vips(
        server_number=1,
        rcon=rcon,
        timestamp=NOW,
        dry_run=False,
    )

    assert result.execution.dry_run is False
    assert result.execution.added == frozenset({"add-1"})
    assert result.execution.removed == frozenset({"remove-1"})
    assert rcon.calls == [
        ("get",),
        ("add", "add-1", "Player"),
        ("remove", "remove-1"),
    ]


def _empty_sync_plan():
    from rcon.vip_sync import VipSyncPlan

    return VipSyncPlan(
        to_add=(),
        to_remove=frozenset(),
        unchanged=frozenset(),
        unknown=frozenset(),
    )


def _empty_execution(*, dry_run):
    from rcon.vip_sync_executor import VipSyncExecutionResult

    return VipSyncExecutionResult(
        dry_run=dry_run,
        added=frozenset(),
        removed=frozenset(),
        skipped_additions=(),
        skipped_removals=frozenset(),
        failures=(),
    )


def test_runner_dry_run_does_not_record_status(monkeypatch):
    import rcon.vip_sync_runner as runner_module
    import rcon.vip_sync_status as status_module

    monkeypatch.setattr(
        runner_module,
        "read_gameserver_vips",
        lambda rcon: [],
    )
    monkeypatch.setattr(
        runner_module,
        "build_database_vip_sync_plan",
        lambda **kwargs: _empty_sync_plan(),
    )
    monkeypatch.setattr(
        runner_module,
        "execute_vip_sync_plan",
        lambda **kwargs: _empty_execution(dry_run=True),
    )

    def unexpected_status_write(*args, **kwargs):
        raise AssertionError("Dry-run attempted to write synchronization status")

    monkeypatch.setattr(
        status_module,
        "record_vip_sync_started",
        unexpected_status_write,
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_completed",
        unexpected_status_write,
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_failed",
        unexpected_status_write,
    )

    result = runner_module.synchronize_gameserver_vips(
        server_number=2,
        rcon=object(),
        dry_run=True,
        trigger="manual",
    )

    assert result.execution.dry_run is True


def test_runner_records_real_sync_lifecycle(monkeypatch):
    import rcon.vip_sync_runner as runner_module
    import rcon.vip_sync_status as status_module

    events = []

    monkeypatch.setattr(
        runner_module,
        "read_gameserver_vips",
        lambda rcon: [],
    )
    monkeypatch.setattr(
        runner_module,
        "build_database_vip_sync_plan",
        lambda **kwargs: _empty_sync_plan(),
    )
    monkeypatch.setattr(
        runner_module,
        "execute_vip_sync_plan",
        lambda **kwargs: _empty_execution(dry_run=False),
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_started",
        lambda **kwargs: events.append(("started", kwargs)),
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_completed",
        lambda **kwargs: events.append(("completed", kwargs)),
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_failed",
        lambda **kwargs: events.append(("failed", kwargs)),
    )

    result = runner_module.synchronize_gameserver_vips(
        server_number=3,
        rcon=object(),
        dry_run=False,
        trigger="notification",
    )

    assert result.execution.successful is True
    assert [event[0] for event in events] == [
        "started",
        "completed",
    ]
    assert events[0][1] == {
        "server_number": 3,
        "trigger": "notification",
    }
    assert events[1][1]["server_number"] == 3
    assert events[1][1]["trigger"] == "notification"
    assert events[1][1]["execution"] is result.execution


def test_runner_records_failure_before_execution(monkeypatch):
    import rcon.vip_sync_runner as runner_module
    import rcon.vip_sync_status as status_module

    events = []
    expected_error = RuntimeError("RCON unavailable")

    def fail_read(rcon):
        raise expected_error

    monkeypatch.setattr(
        runner_module,
        "read_gameserver_vips",
        fail_read,
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_started",
        lambda **kwargs: events.append(("started", kwargs)),
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_completed",
        lambda **kwargs: events.append(("completed", kwargs)),
    )
    monkeypatch.setattr(
        status_module,
        "record_vip_sync_failed",
        lambda **kwargs: events.append(("failed", kwargs)),
    )

    import pytest

    with pytest.raises(RuntimeError, match="RCON unavailable"):
        runner_module.synchronize_gameserver_vips(
            server_number=4,
            rcon=object(),
            dry_run=False,
            trigger="periodic",
        )

    assert [event[0] for event in events] == [
        "started",
        "failed",
    ]
    assert events[1][1] == {
        "server_number": 4,
        "trigger": "periodic",
        "error": expected_error,
    }
